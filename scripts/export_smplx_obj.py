"""Quick SMPLX axis confirmation & OBJ export utility.

Usage (from FlowMDM root or project root containing data/smplx models):
    pixi run -e latest python tmp/export_smplx_obj.py --gender neutral --out tmp/smplx_neutral.obj

The script:
 1. Loads SMPLX model (neutral/male/female) from data/smplx
 2. Creates a zero pose & zero shape (T-pose) vertex array
 3. Exports an OBJ (Y-up version) to requested path
 4. Prints raw vertex coordinate ranges (min/max per axis) BEFORE and AFTER converting to Y-up
 5. Infers up-axis by tallest spread dimension and reports transformation applied

Axis Logic:
 SMPLX canonical mesh is generally Z-up. To convert to Y-up (FlowMDM joints convention):
   (x, y, z)_Zup -> (x, z, -y)_Yup   # equivalent to -90 deg rotation about X
Reverse:
   (x, y, z)_Yup -> (x, -z, y)_Zup

We keep both arrays to print stats for verification.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np

try:
    import torch
except Exception as e:  # pragma: no cover
    print("ERROR: torch import failed (required for smplx):", e, file=sys.stderr)
    sys.exit(1)

try:
    import smplx  # type: ignore
except ImportError as e:  # pragma: no cover
    print("ERROR: smplx not installed in this environment:", e, file=sys.stderr)
    sys.exit(1)

try:
    import trimesh  # type: ignore
except ImportError as e:  # pragma: no cover
    print("ERROR: trimesh not installed in this environment:", e, file=sys.stderr)
    sys.exit(1)


def axis_stats(verts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vmin = verts.min(axis=0)
    vmax = verts.max(axis=0)
    return vmin, vmax


def infer_up_axis(vmin: np.ndarray, vmax: np.ndarray) -> str:
    spans = vmax - vmin
    # Typical human body: vertical span >> lateral (x) ~ depth
    axis_idx = int(np.argmax(spans))
    return {0: "X (unexpected)", 1: "Y", 2: "Z"}[axis_idx]


def convert_zup_to_yup(verts: np.ndarray) -> np.ndarray:
    # (x, y, z)_Z -> (x, z, -y)_Y
    x = verts[:, 0]
    y = verts[:, 1]
    z = verts[:, 2]
    return np.stack([x, z, -y], axis=1)


def main() -> None:
    parser = argparse.ArgumentParser(description="SMPLX OBJ export & axis confirmation")
    parser.add_argument("--gender", choices=["neutral", "male", "female"], default="neutral")
    parser.add_argument("--model-path", default="data", help="Path containing smplx/ directory (default: data)")
    parser.add_argument("--out", default="tmp/smplx_axis_check_yup.obj", help="Output converted Y-up OBJ path")
    parser.add_argument("--out-raw", default="tmp/smplx_axis_check_raw.obj", help="Output raw (as-loaded) OBJ path")
    parser.add_argument("--no-export", action="store_true", help="Skip writing OBJ (still prints stats)")
    args = parser.parse_args()

    model_root = pathlib.Path(args.model_path).expanduser().resolve()
    smplx_dir = model_root / "smplx"
    if not smplx_dir.exists():
        print(f"ERROR: Could not find smplx directory at {smplx_dir}", file=sys.stderr)
        sys.exit(2)

    print(f"Loading SMPLX model gender={args.gender} from {smplx_dir} (full components)")
    model = smplx.SMPLX(
        model_path=str(smplx_dir),
        gender=args.gender,
        use_pca=False,
        create_global_orient=True,
        create_body_pose=True,
        create_betas=True,
        create_left_hand_pose=True,
        create_right_hand_pose=True,
        create_expression=True,
        create_jaw_pose=True,
        create_leye_pose=True,
        create_reye_pose=True,
        num_betas=10,
        num_expression_coeffs=10,
    )
    model_type = "smplx"

    with torch.no_grad():
        device = model.global_orient.device
        zeros = lambda *shape: torch.zeros(*shape, device=device)  # noqa: E731
        output = model(
            betas=zeros(1, 10),
            body_pose=zeros(1, model.NUM_BODY_JOINTS * 3),
            global_orient=zeros(1, 3),
            left_hand_pose=zeros(1, 15 * 3),
            right_hand_pose=zeros(1, 15 * 3),
            expression=zeros(1, 10),
            jaw_pose=zeros(1, 3),
            leye_pose=zeros(1, 3),
            reye_pose=zeros(1, 3),
        )
    verts_z = output.vertices[0].cpu().numpy()

    vmin_z, vmax_z = axis_stats(verts_z)
    up_inferred_z = infer_up_axis(vmin_z, vmax_z)

    verts_y = convert_zup_to_yup(verts_z)
    vmin_y, vmax_y = axis_stats(verts_y)
    up_inferred_y = infer_up_axis(vmin_y, vmax_y)

    print(f"Raw Z-up vertex bounds ({model_type}):")
    print(f"  min: {vmin_z}")
    print(f"  max: {vmax_z}")
    print(f"  span: {vmax_z - vmin_z}")
    print(f"  inferred up-axis: {up_inferred_z}")

    print("\nConverted Y-up vertex bounds:")
    print(f"  min: {vmin_y}")
    print(f"  max: {vmax_y}")
    print(f"  span: {vmax_y - vmin_y}")
    print(f"  inferred up-axis: {up_inferred_y}")

    if not args.no_export:
        raw_path = pathlib.Path(args.out_raw)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        mesh_raw = trimesh.Trimesh(vertices=verts_z, faces=model.faces, process=False)
        mesh_raw.export(raw_path)
        print(f"\nExported RAW OBJ (no axis conversion) to: {raw_path}")

        out_path = pathlib.Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        mesh_y = trimesh.Trimesh(vertices=verts_y, faces=model.faces, process=False)
        mesh_y.export(out_path)
        print(f"Exported Y-up OBJ to: {out_path}")
        print("Import both to compare orientation. If RAW already stands upright in Y-up tools, model is Y-up.")

    print("\nConclusion:")
    if up_inferred_z.startswith("Z") and up_inferred_y.startswith("Y"):
        print("  SMPLX canonical mesh is Z-up. Conversion to Y-up applied correctly.")
    else:
        print("  Unexpected axis inference results – review transformation logic.")


if __name__ == "__main__":  # pragma: no cover
    main()
