# How to Download FlowMDM Models

This guide explains how to download the pretrained models and dependencies required to run FlowMDM for human motion generation and evaluation.

## Overview

FlowMDM requires several components to be downloaded:
1. **SMPL body model files** - For human body representation
2. **GloVe word embeddings** - For text processing in evaluators
3. **T2M evaluation models** - For text-to-motion benchmarking
4. **Pretrained FlowMDM models** - The main model weights

## Prerequisites

- `gdown` package for downloading from Google Drive
- Bash environment (on Windows: WSL, Git Bash, or similar)
- Internet connection for downloading large files (~several GB total)

## Step-by-Step Download Process

### 1. Navigate to FlowMDM Directory
```bash
cd model_zoo/FlowMDM
```

### 2. Download Dependencies (Required)
Run these scripts in order to download all necessary dependencies:

```bash
# Download SMPL body model files
bash runners/prepare/download_smpl_files.sh

# Download GloVe word embeddings (used by evaluators)
bash runners/prepare/download_glove.sh

# Download text-to-motion evaluation models
bash runners/prepare/download_t2m_evaluators.sh
```

### 3. Download Pretrained Models (Required for Generation/Evaluation)
```bash
# Download the main FlowMDM pretrained models
bash runners/prepare/download_pretrained_models.sh
```

## What Gets Downloaded

### SMPL Files (`download_smpl_files.sh`)
- **Location**: `body_models/smpl/` and `body_models/smplh/`
- **Purpose**: Human body model parameters for motion representation
- **Files**: SMPL and SMPLH model files

### GloVe Embeddings (`download_glove.sh`)
- **Location**: `glove/`
- **Purpose**: Pre-trained word vectors for text processing in evaluators
- **Note**: Used by evaluators, not by FlowMDM model itself

### T2M Evaluators (`download_t2m_evaluators.sh`)
- **Location**: `t2m/` and extracted dataset files
- **Purpose**: Text-to-motion evaluation models and benchmark datasets
- **Usage**: Required for model evaluation and benchmarking

### Pretrained Models (`download_pretrained_models.sh`)
- **Location**: `results/`
- **Models**:
  - Babel model: `./results/babel/FlowMDM/model001300000.pt`
  - HumanML3D model: `./results/humanml/FlowMDM/model000500000.pt`
- **Purpose**: Main FlowMDM model weights for generation and evaluation

## Usage Examples

Once downloaded, you can use the models for generation:

### Babel Model Generation
```bash
python -m runners.generate \
  --model_path ./results/babel/FlowMDM/model001300000.pt \
  --num_repetitions 1 \
  --bpe_denoising_step 125 \
  --guidance_param 1.5 \
  --instructions_file ./runners/jsons/composition_babel.json
```

### HumanML3D Model Generation
```bash
python -m runners.generate \
  --model_path ./results/humanml/FlowMDM/model000500000.pt \
  --num_repetitions 1 \
  --bpe_denoising_step 60 \
  --guidance_param 2.5 \
  --instructions_file ./runners/jsons/composition_humanml.json \
  --use_chunked_att
```

## Troubleshooting

### Common Issues

1. **gdown not found**: Install with `pip install gdown`
2. **Permission errors**: Ensure you have write permissions in the directory
3. **Network timeouts**: Large files may take time; retry if downloads fail
4. **Disk space**: Ensure sufficient disk space (~5-10GB total)

### Windows-Specific Notes

- Use WSL, Git Bash, or PowerShell with bash compatibility
- Alternatively, manually download files from the Google Drive links in the scripts
- Ensure proper path handling for Windows file systems

## File Structure After Download

```
FlowMDM/
├── body_models/
│   ├── smpl/
│   └── smplh/
├── glove/
├── t2m/
├── results/
│   ├── babel/FlowMDM/model001300000.pt
│   └── humanml/FlowMDM/model000500000.pt
└── dataset/  # If you also download training datasets
```

## References

- [FlowMDM GitHub Repository](https://github.com/BarqueroGerman/FlowMDM)
- [FlowMDM Paper](https://arxiv.org/abs/2402.15509)
- [Project Page](https://barquerogerman.github.io/FlowMDM/)
- [SMPL Model](https://smpl.is.tue.mpg.de/)
- [HumanML3D Dataset](https://github.com/EricGuo5513/HumanML3D)

## Related Tasks

- **Setup**: First complete the conda environment setup as described in FlowMDM README
- **Generation**: Use downloaded models for motion generation and composition
- **Evaluation**: Run benchmarks using the downloaded evaluation models
- **Training**: Download additional datasets if you want to retrain models
