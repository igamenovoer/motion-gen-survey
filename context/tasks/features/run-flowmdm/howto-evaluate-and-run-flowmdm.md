# How to Evaluate and Run FlowMDM Models

## HEADER
- **Purpose**: Comprehensive guide for evaluating and running FlowMDM models for human motion generation and composition
- **Status**: Active
- **Date**: 2025-01-02
- **Dependencies**: FlowMDM environment, pretrained models, datasets (optional)
- **Target**: Researchers working with FlowMDM human motion generation

## Overview

FlowMDM (CVPR'24) is a diffusion-based model for seamless human motion composition using Blended Positional Encodings. It generates long, continuous motion sequences guided by varying textual descriptions without postprocessing.

**Key Features:**
- Blended Positional Encodings (BPE) for smooth transitions
- Pose-Centric Cross-ATtention (PCCAT) for text robustness  
- Support for both Babel and HumanML3D datasets
- Evaluation using Peak Jerk and Area Under Jerk metrics

## Environment Setup

### 1. Install System Dependencies

```bash
# Ubuntu/Linux
sudo apt update && sudo apt install ffmpeg

# Windows - Install ffmpeg from https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/
```

### 2. Create Conda Environment

```bash
cd model_zoo/FlowMDM
conda env create -f environment.yml
conda activate FlowMDM

# Install additional dependencies
python -m spacy download en_core_web_sm
pip install git+https://github.com/openai/CLIP.git
pip install git+https://github.com/GuyTevet/smplx.git
conda install ffmpeg -y
```

### 3. Download Required Dependencies

```bash
# Download SMPL files, GloVe embeddings, and evaluation tools
bash runners/prepare/download_smpl_files.sh
bash runners/prepare/download_glove.sh  
bash runners/prepare/download_t2m_evaluators.sh

# Download pretrained models (required)
bash runners/prepare/download_pretrained_models.sh
```

## Quick Start: Generate Motion Examples

### Generate with Babel Model

```bash
python -m runners.generate \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --num_repetitions 1 \
  --bpe_denoising_step 125 \
  --guidance_param 1.5 \
  --instructions_file ./runners/jsons/composition_babel.json
```

### Generate with HumanML3D Model

```bash
python -m runners.generate \
  --model_path ./results/humanml/FlowMDM/model000500000.pt \
  --num_repetitions 1 \
  --bpe_denoising_step 60 \
  --guidance_param 2.5 \
  --instructions_file ./runners/jsons/composition_humanml.json \
  --use_chunked_att
```

## Custom Motion Generation

### 1. Create Custom Instruction File

Create a JSON file with your desired motion sequences:

```json
{
  "lengths": [64, 42, 32, 41, 82],
  "text": [
    "turn left",
    "walk forward", 
    "t-pose",
    "turn right",
    "jog forward"
  ]
}
```

### 2. Generate Custom Motions

```bash
python -m runners.generate \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --instructions_file ./path/to/your/custom_instructions.json \
  --num_repetitions 3 \
  --bpe_denoising_step 125 \
  --guidance_param 1.5
```

## Model Evaluation

### Babel Dataset Evaluation

```bash
python -m runners.eval \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --dataset babel \
  --eval_mode final \
  --bpe_denoising_step 125 \
  --guidance_param 1.5 \
  --transition_length 30
```

### HumanML3D Dataset Evaluation

```bash
python -m runners.eval \
  --model_path ./results/humanml/FlowMDM/model000500000.pt \
  --dataset humanml \
  --eval_mode final \
  --bpe_denoising_step 60 \
  --guidance_param 2.5 \
  --transition_length 60 \
  --use_chunked_att
```

### Quick Evaluation (3 repetitions)

```bash
python -m runners.eval \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --dataset babel \
  --eval_mode fast \
  --bpe_denoising_step 125 \
  --guidance_param 1.5
```

## Advanced Usage

### Render SMPL Meshes

Convert generated motion to 3D meshes for Blender/Maya:

```bash
python -m runners.render_mesh --input_path /path/to/generated/motion.mp4
```

**Outputs:**
- `sample_rep##_smpl_params.npy` - SMPL parameters
- `sample_rep##_obj/` - Mesh frames in OBJ format

### Generate Motion Extrapolations

```bash
python -m runners.generate \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --instructions_file ./runners/jsons/extrapolation_babel.json \
  --bpe_denoising_step 125 \
  --guidance_param 1.5
```

### Sample from Dataset (No Custom Instructions)

```bash
python -m runners.generate \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --num_samples 10 \
  --num_repetitions 3 \
  --bpe_denoising_step 125 \
  --guidance_param 1.5
```

## Key Parameters

### Generation Parameters

- `--bpe_denoising_step`: Controls smoothness vs. quality trade-off
  - Higher values (up to 1000): Better individual action quality, more abrupt transitions
  - Babel: 125, HumanML3D: 60 (recommended)
- `--guidance_param`: Classifier-free guidance strength
  - Babel: 1.5, HumanML3D: 2.5 (recommended)
- `--use_chunked_att`: Accelerates inference for long sequences (recommended for HumanML3D)

### Evaluation Parameters

- `--eval_mode`: `fast` (3 reps) or `final` (10 reps)
- `--transition_length`: Length for transition evaluation (Babel: 30, HumanML3D: 60)

## Dataset Requirements (Optional)

Only needed for evaluation/training, not for generation with pretrained models.

### HumanML3D Setup

```bash
# Follow https://github.com/EricGuo5513/HumanML3D.git
cp -r ../HumanML3D/HumanML3D ./dataset/HumanML3D
```

### Babel Setup

Download processed datasets:
- [Main dataset](https://drive.google.com/file/d/18a4eRh8mbIFb55FMHlnmI8B8tSTkbp4t/view?usp=share_link) → `./dataset/babel`
- [Additional files](https://drive.google.com/file/d/1PBlbxawaeFTxtKkKDsoJwQGuDTdp52DD/view?usp=sharing) → `./dataset/babel`

## Technical Notes

- **GPU Required**: PyTorch 1.13.0 + CUDA support recommended  
- **Memory**: Evaluation can take >12h depending on GPU power
- **Backup**: Generated motions are automatically backed up during evaluation
- **Platform**: Tested on Ubuntu 20.04.6 + Python 3.8
- **Core Implementation**: `model/FlowMDM.py`, `diffusion/diffusion_wrappers.py`

## Troubleshooting

### Common Issues

1. **CUDA/GPU Issues**: Ensure PyTorch CUDA version matches your system
2. **Memory Errors**: Use `--use_chunked_att` for long sequences
3. **Environment Issues**: Stick to exact Python 3.8 + PyTorch 1.13.0 versions
4. **Missing Files**: Ensure all preparation scripts completed successfully

### Performance Optimization

- Use `--use_chunked_att` for long sequences (HumanML3D)
- Adjust `--bpe_denoising_step` based on quality/speed trade-off
- Use `--eval_mode fast` for quick testing

## Source References

- **Paper**: [Seamless Human Motion Composition with Blended Positional Encodings (CVPR'24)](https://arxiv.org/abs/2402.15509)
- **Project Page**: https://barquerogerman.github.io/FlowMDM/
- **Original Repository**: https://github.com/BarqueroGerman/FlowMDM
- **Forked Repository**: https://github.com/imsight-forks/FlowMDM
- **Documentation**: `runners/README.md` in the repository