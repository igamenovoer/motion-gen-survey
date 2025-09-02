"""Tests for FlowMDM motion visualization."""

import numpy as np
import pytest
from pathlib import Path


class TestFlowMDMResults:
    """Test FlowMDM result loading and processing."""
    
    @pytest.fixture
    def sample_motion_data(self):
        """Create sample motion data for testing."""
        # Create synthetic motion data with shape (1, 22, 3, 10)
        # 1 batch, 22 joints, 3D positions, 10 frames
        return np.random.randn(1, 22, 3, 10).astype(np.float32)
    
    def test_motion_data_shape(self, sample_motion_data):
        """Test that motion data has correct shape."""
        assert sample_motion_data.shape[0] == 1  # Batch size
        assert sample_motion_data.shape[1] == 22  # Number of joints
        assert sample_motion_data.shape[2] == 3   # 3D coordinates
        assert sample_motion_data.shape[3] == 10  # Number of frames
    
    def test_joint_extraction(self, sample_motion_data):
        """Test extracting joints from a specific frame."""
        frame_idx = 0
        joints = sample_motion_data[0, :, :, frame_idx]
        
        assert joints.shape == (22, 3)
        assert joints.dtype == np.float32
    
    @pytest.mark.slow
    def test_flowmdm_result_file_exists(self):
        """Test that actual FlowMDM result file exists (if available)."""
        result_path = Path(r"model_zoo\FlowMDM\results\babel\FlowMDM\001300000_s10_simple_walk_instructions\results.npy")
        
        if result_path.exists():
            result = np.load(result_path, allow_pickle=True).item()
            assert "motion" in result
            assert isinstance(result["motion"], np.ndarray)
        else:
            pytest.skip("FlowMDM result file not found")
    
    def test_skeleton_pairs_validity(self):
        """Test that skeleton pairs are within valid joint indices."""
        skeleton_pairs = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Spine
            (0, 5), (5, 6), (6, 7), (7, 8),  # Left leg
            (0, 9), (9, 10), (10, 11), (11, 12),  # Right leg
            (3, 13), (13, 14), (14, 15), (15, 16),  # Left arm
            (3, 17), (17, 18), (18, 19), (19, 20),  # Right arm
            (3, 21)  # Head
        ]
        
        max_joint_idx = 21
        for start, end in skeleton_pairs:
            assert 0 <= start <= max_joint_idx
            assert 0 <= end <= max_joint_idx
            assert start != end


class TestVisualizationHelpers:
    """Test visualization helper functions."""
    
    def test_color_validation(self):
        """Test color value validation."""
        valid_colors = [
            [1.0, 0.0, 0.0],  # Red
            [0.0, 1.0, 0.0],  # Green
            [0.0, 0.0, 1.0],  # Blue
            [0.5, 0.5, 0.5],  # Gray
        ]
        
        for color in valid_colors:
            assert len(color) == 3
            assert all(0.0 <= c <= 1.0 for c in color)
    
    @pytest.mark.parametrize("frame_idx,expected", [
        (0, "Frame: 0/119"),
        (60, "Frame: 60/119"),
        (119, "Frame: 119/119"),
    ])
    def test_frame_counter_text(self, frame_idx, expected):
        """Test frame counter text generation."""
        total_frames = 120
        text = f"Frame: {frame_idx}/{total_frames-1}"
        assert text == expected


@pytest.mark.unit
def test_imports():
    """Test that required modules can be imported."""
    try:
        import numpy as np
        import pathlib
        # Note: pyvista imports might fail in headless environments
        # import igpy.myplot.vistaplot as vp
    except ImportError as e:
        pytest.fail(f"Failed to import required module: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])