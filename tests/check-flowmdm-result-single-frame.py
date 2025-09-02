"""
FlowMDM Motion Visualization Script

Visualizes T2M format motion data from FlowMDM results using correct joint topology.
- Fixed skeleton connections to match T2M kinematic chain structure
- Corrected joint indices and labels based on HumanML3D documentation
- Supports both Babel (30 FPS) and HumanML3D (20 FPS) datasets

Usage:
    python scripts/check-flowmdm-result.py
    
Settings:
    - frame_index: Which frame to visualize (0 to seq_len-1)
    - show_all_joints: True to label all 22 joints, False for key joints only
"""

import numpy as np
# import torch
# import smplx
import pathlib
import igpy.myplot.vistaplot as vp

# Load FlowMDM result
flowmdm_result_dir = pathlib.Path(r'model_zoo\FlowMDM\results\babel\FlowMDM\001300000_s10_simple_walk_instructions')
flowmdm_result_file = flowmdm_result_dir / 'results.npy'

result = np.load(flowmdm_result_file, allow_pickle=True).item()
motion_data: np.ndarray = result['motion']  # Shape: (batch, 22, 3, seq_len)

# Print dataset info
print(f"Loaded motion data: {motion_data.shape}")
print(f"Text prompts: {result.get('text', ['No text available'])}")
print(f"Sequence lengths: {result.get('lengths', 'Not specified')}")
print(f"FPS: 30 (Babel dataset)")

# T2M joint indices and names (HumanML3D format)
t2m_joint_names = {
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
t2m_kinematic_chain = [
    [0, 2, 5, 8, 11],      # Right leg: Pelvis → R.Hip → R.Knee → R.Ankle → R.Foot
    [0, 1, 4, 7, 10],      # Left leg: Pelvis → L.Hip → L.Knee → L.Ankle → L.Foot
    [0, 3, 6, 9, 12, 15],  # Spine: Pelvis → Spine1 → Spine2 → Spine3 → Neck → Head
    [9, 14, 17, 19, 21],   # Right arm: Spine3 → R.Collar → R.Shoulder → R.Elbow → R.Wrist
    [9, 13, 16, 18, 20]    # Left arm: Spine3 → L.Collar → L.Shoulder → L.Elbow → L.Wrist
]

# Build skeleton pairs from kinematic chains
skeleton_pairs = []
for chain in t2m_kinematic_chain:
    for i in range(len(chain) - 1):
        skeleton_pairs.append((chain[i], chain[i + 1]))

# Create interactive plotter with Qt backend
plot = vp.ExPlotter.init_with_background_plotter(
    title="FlowMDM T2M Motion Viewer - 22 Joints",
    background_color3f=[0.95, 0.95, 0.95],  # Light gray background
    with_menu=False,
    with_toolbar=False
)

# Add ground plane for reference
plot.add_ground_plane(
    x_size=4, y_size=4,
    up_vector=[0, 1, 0],  # Y-up coordinate system
    x_seg=20, y_seg=20,
    color3f=[0.6, 0.6, 0.6],
    line_width=0.5
)

# Add coordinate axes at origin
plot.add_axes(
    origin=[0, 0, 0],
    xyz_dirs=np.eye(3),
    axis_length=0.5,
    line_width=3.0
)

# Visualization settings
frame_index = 10
show_all_joints = False  # Set to True to label all joints

joints = motion_data[0, :, :, frame_index]  # Extract 22x3 joint positions
print(f"Visualizing frame {frame_index}/{motion_data.shape[-1]-1}")

# Draw skeleton bones
for bone_start, bone_end in skeleton_pairs:
    plot.add_line_segments(
        pts1=joints[bone_start:bone_start+1],  # Start joint (1x3)
        pts2=joints[bone_end:bone_end+1],      # End joint (1x3)
        color3f=[0.2, 0.4, 0.8],  # Blue bones
        line_width=3.0
    )

# Draw joint points
plot.add_points(
    pts=joints,
    color3f=[1.0, 0.2, 0.2],  # Red joints
    point_size=10,
    style='sphere'  # Render as spheres for better visibility
)

# Add text labels for joints
if show_all_joints:
    # Show all joint labels
    joints_to_label = t2m_joint_names
else:
    # Show only key joints
    joints_to_label = {
        0: "Pelvis",
        12: "Neck",
        15: "Head",
        10: "L.Foot",
        11: "R.Foot",
        20: "L.Wrist",
        21: "R.Wrist"
    }

for joint_idx, label in joints_to_label.items():
    joint_pos = joints[joint_idx]
    plot.add_text(
        text_content=label,
        position=joint_pos + [0, 0.1, 0],  # Offset slightly above joint
        font_size=8,
        color3f=[0.2, 0.2, 0.2],
        shadow=True
    )

# Add frame counter
plot.add_text(
    text_content=f"Frame: {frame_index}/{motion_data.shape[-1]-1}",
    position=[0, 2.5, 0],
    font_size=14,
    color3f=[0, 0, 0],
    bold=True
)

# Set camera for good viewing angle
plot.set_camera_transform_by_vectors(
    view_dir=[-1, -0.5, -1],  # Look from front-right
    up_dir=[0, 1, 0],         # Y-up
    position=[3, 2, 3],       # Camera position
    focal_distance=4.0
)

# Show the interactive viewer
plot.show()

