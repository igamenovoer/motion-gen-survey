"""
FlowMDM Motion Animation Script

Animates T2M format motion data from FlowMDM results using PyVistaQT.
- Interactive 3D animation of 22-joint human skeleton
- Supports both Babel (30 FPS) and HumanML3D (20 FPS) datasets
- Uses correct T2M kinematic chain structure from HumanML3D documentation
- Provides play/pause controls and frame scrubbing

Usage:
    python check-flowmdm-result-animation.py
    
Controls:
    - Spacebar: Play/Pause animation
    - Left/Right arrows: Step frame by frame
    - 'r': Reset to frame 0
    - 'q': Quit
"""

import numpy as np
import pathlib
import time
from threading import Thread, Event
import contextlib
import pyvista as pv
import pyvistaqt as pvqt

# Load FlowMDM result
flowmdm_result_dir = pathlib.Path(r'model_zoo\FlowMDM\results\babel\FlowMDM\001300000_s10_simple_walk_instructions')
flowmdm_result_file = flowmdm_result_dir / 'results.npy'

result = np.load(flowmdm_result_file, allow_pickle=True).item()
motion_data: np.ndarray = result['motion']  # Shape: (batch, 22, 3, seq_len)

# Print dataset info
print(f"Loaded motion data: {motion_data.shape}")
print(f"Text prompts: {result.get('text', ['No text available'])}")
print(f"Sequence lengths: {result.get('lengths', 'Not specified')}")
print("FPS: 30 (Babel dataset)")
print(f"Total frames: {motion_data.shape[-1]}")

# T2M joint indices and names (HumanML3D format)
t2m_joint_names: dict[int, str] = {
    0: "Pelvis",
    1: "L.Hip", 2: "R.Hip", 3: "Spine1",
    4: "L.Knee", 5: "R.Knee", 6: "Spine2",
    7: "L.Ankle", 8: "R.Ankle", 9: "Spine3",
    10: "L.Foot", 11: "R.Foot", 12: "Neck",
    13: "L.Collar", 14: "R.Collar", 15: "Head",
    16: "L.Shoulder", 17: "R.Shoulder",
    18: "L.Elbow", 19: "R.Elbow",
    20: "L.Wrist", 21: "R.Wrist"
}

# T2M kinematic chain structure from data_loaders/humanml/utils/paramUtil.py
t2m_kinematic_chain: list[list[int]] = [
    [0, 2, 5, 8, 11],      # Right leg: Pelvis → R.Hip → R.Knee → R.Ankle → R.Foot
    [0, 1, 4, 7, 10],      # Left leg: Pelvis → L.Hip → L.Knee → L.Ankle → L.Foot
    [0, 3, 6, 9, 12, 15],  # Spine: Pelvis → Spine1 → Spine2 → Spine3 → Neck → Head
    [9, 14, 17, 19, 21],   # Right arm: Spine3 → R.Collar → R.Shoulder → R.Elbow → R.Wrist
    [9, 13, 16, 18, 20]    # Left arm: Spine3 → L.Collar → L.Shoulder → L.Elbow → L.Wrist
]
# Build skeleton pairs once (list of (start,end) indices for lines)
skeleton_pairs: list[tuple[int, int]] = []
for _chain in t2m_kinematic_chain:
    for _i in range(len(_chain) - 1):
        skeleton_pairs.append((_chain[_i], _chain[_i + 1]))


class FlowMDMAnimator:
    """Interactive animator for FlowMDM motion data with in-place geometry updates."""

    def __init__(self, motion_data: np.ndarray) -> None:
        self.motion_data = motion_data
        self.current_frame = 0
        self.total_frames = motion_data.shape[-1]
        self.is_playing = False
        self.fps = 30.0
        self.frame_delay = 1.0 / self.fps

        self.stop_event = Event()
        self.animation_thread: Thread | None = None

        # Plotter
        self.plotter = pvqt.BackgroundPlotter(  # type: ignore[attr-defined]
            title="FlowMDM T2M Motion Animation - 22 Joints",
            window_size=(1024, 768)
        )
        self.setup_scene()
        self.setup_controls()

        # Skeleton polydata
        self.skel_poly = self._build_skeleton_polydata(0)
        self.skel_actor = self.plotter.add_mesh(  # type: ignore[attr-defined]
            self.skel_poly,
            color=[0.2, 0.4, 0.8],
            line_width=3.0,
            render_lines_as_tubes=True,
            point_size=12,
            render_points_as_spheres=True
        )

        # Labels (anchor points updated in-place)
        self.key_joint_ids = [0, 12, 15, 10, 11, 20, 21]
        first = self.motion_data[0, :, :, 0]
        self.label_poly = pv.PolyData(first[self.key_joint_ids].copy())
        self.labels_actor = self.plotter.add_point_labels(  # type: ignore[attr-defined]
            self.label_poly,
            [t2m_joint_names[i] for i in self.key_joint_ids],
            show_points=False,
            font_size=10,
            always_visible=True
        )

        # Create a single status text actor (updated in-place each frame)
        self.status_text = self.plotter.add_text(  # type: ignore[attr-defined]
            "", position='lower_left', font_size=11, color=[0, 0, 0]
        )

        self.render_frame(0)

    # Scene
    def setup_scene(self) -> None:
        plane = pv.Plane(center=[0, 0, 0], direction=[0, 1, 0],
                          i_size=4, j_size=4, i_resolution=20, j_resolution=20)
        self.plotter.add_mesh(plane, color=[0.6, 0.6, 0.6], opacity=0.3,  # type: ignore[attr-defined]
                               show_edges=True, line_width=0.5)
        self.plotter.add_axes()  # type: ignore[attr-defined]
        self.plotter.set_background([0.95, 0.95, 0.95])  # type: ignore[attr-defined]
        self.plotter.camera_position = ([3, 2, 3], [0, 1, 0], [0, 1, 0])  # type: ignore[attr-defined]

    # Controls
    def setup_controls(self) -> None:
        self.plotter.add_key_event(' ', self.toggle_animation)  # type: ignore[attr-defined]
        self.plotter.add_key_event('Left', lambda: self.step_frame(-1))  # type: ignore[attr-defined]
        self.plotter.add_key_event('Right', lambda: self.step_frame(1))  # type: ignore[attr-defined]
        self.plotter.add_key_event('r', self.reset_animation)  # type: ignore[attr-defined]
        self.plotter.add_key_event('q', self.quit_animation)  # type: ignore[attr-defined]

    # Geometry
    def _build_skeleton_polydata(self, frame_index: int) -> pv.PolyData:
        joints = self.motion_data[0, :, :, frame_index].copy()
        line_cells: list[int] = []
        for a, b in skeleton_pairs:
            line_cells.extend([2, a, b])
        poly = pv.PolyData()
        poly.points = joints
        poly.lines = np.array(line_cells)
        return poly

    # Frame update
    def render_frame(self, frame_index: int) -> None:
        if frame_index < 0 or frame_index >= self.total_frames:
            return
        self.current_frame = frame_index
        joints = self.motion_data[0, :, :, frame_index]
        # In-place update of skeleton points (keeps VTK data objects stable)
        skel_pts = self.skel_poly.points
        skel_pts[:] = joints  # type: ignore[index]
        self.skel_poly.points = skel_pts  # reassign is optional but explicit
        # In-place update of label anchor points
        label_pts = self.label_poly.points
        label_pts[:] = joints[self.key_joint_ids]  # type: ignore[index]
        self.label_poly.points = label_pts
        # Force label actor to re-read updated dataset (some backends need this)
        with contextlib.suppress(Exception):
            self.labels_actor.SetInputData(self.label_poly)  # type: ignore[attr-defined]

        # Compact status line (lower-left) updated in place; avoid adding new actors
        status = f"F {frame_index}/{self.total_frames-1} | {'Play' if self.is_playing else 'Pause'} | Space Play/Pause, Arrows Step, R Reset, Q Quit"
        updated = False
        if hasattr(self.status_text, "SetInput"):
            try:
                self.status_text.SetInput(status)  # type: ignore[attr-defined]
                updated = True
            except Exception:
                pass
        if (not updated) and hasattr(self.status_text, "SetText"):
            try:
                self.status_text.SetText(status)  # type: ignore[attr-defined]
                updated = True
            except Exception:
                pass
        if not updated:
            # Fallback: remove previous actor before recreating to prevent overlap
            with contextlib.suppress(Exception):
                self.plotter.remove_actor(self.status_text)  # type: ignore[attr-defined]
            self.status_text = self.plotter.add_text(  # type: ignore[attr-defined]
                status, position='lower_left', font_size=11, color=[0, 0, 0]
            )
        self.plotter.render()  # type: ignore[attr-defined]

    # Playback
    def toggle_animation(self) -> None:
        if self.is_playing:
            self.stop_animation()
        else:
            self.start_animation()

    def start_animation(self) -> None:
        if not self.is_playing:
            self.is_playing = True
            self.stop_event.clear()
            self.animation_thread = Thread(target=self._animation_loop, daemon=True)
            self.animation_thread.start()
            print("Animation started")

    def stop_animation(self) -> None:
        if self.is_playing:
            self.is_playing = False
            self.stop_event.set()
            if self.animation_thread is not None:
                self.animation_thread.join()
            print("Animation paused")

    def _animation_loop(self) -> None:
        while not self.stop_event.is_set():
            self.render_frame((self.current_frame + 1) % self.total_frames)
            time.sleep(self.frame_delay)

    def step_frame(self, direction: int) -> None:
        self.stop_animation()
        self.render_frame((self.current_frame + direction) % self.total_frames)

    def reset_animation(self) -> None:
        self.stop_animation()
        self.render_frame(0)
        print("Animation reset")

    def quit_animation(self) -> None:
        self.stop_animation()
        self.plotter.close()  # type: ignore[attr-defined]

    # UI
    def show(self) -> None:
        print("\nAnimation Controls:")
        print("  Spacebar: Play/Pause")
        print("  Left/Right arrows: Step frame by frame")
        print("  'r': Reset to frame 0")
        print("  'q': Quit")
        print("\nStarting interactive animation...")
        self.plotter.show()  # type: ignore[attr-defined]

if __name__ == "__main__":
    # Create and run the animator
    animator = FlowMDMAnimator(motion_data)
    animator.show()
