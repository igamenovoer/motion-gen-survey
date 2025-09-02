# FlowMDM Text-to-Motion Usage Guide

## HEADER
- **Purpose**: Essential usage information for FlowMDM text-to-motion generation
- **Status**: Active
- **Date**: 2025-01-02
- **Dependencies**: FlowMDM pretrained models, instruction JSON files
- **Target**: Developers using FlowMDM for motion generation

## What is FlowMDM

Diffusion-based model that generates seamless human motion compositions from text descriptions. Creates long, continuous sequences with smooth transitions between actions using Blended Positional Encodings (BPE).

## Training Datasets

### HumanML3D Dataset
Large-scale 3D human motion-language dataset with **14,616 motion sequences** and **44,970 text descriptions**. Each motion has 3 detailed text descriptions averaging 12 words. Motions are 7.1 seconds average length at 20 FPS with 22 joint points.

**Characteristics**: Detailed, descriptive language ("a person walks forward slowly while looking around nervously")

**Reference**: [HumanML3D: A large and diverse 3d human motion-language dataset](https://github.com/EricGuo5513/HumanML3D) (CVPR 2022)

### BABEL Dataset  
Bodies, Action and Behavior with English Labels - **43 hours** of mocap sequences with **28k sequence labels** and **63k frame labels** across **250+ action categories**. More concise action-focused labels averaging 2.3 words.

**Characteristics**: Simple, direct actions ("walk forward", "turn left", "jump")

**Reference**: [BABEL: Bodies, Action and Behavior with English Labels](https://babel.is.tue.mpg.de/) (CVPR 2021)

## JSON Input Format

FlowMDM uses structured JSON files to define motion compositions:

```json
{
  "lengths": [99, 169, 199],
  "text": [
    "person walks backwards quickly, then stops.",
    "a person is patting something in front of him",
    "waving arms side to side."
  ]
}
```

### Format Requirements
- **lengths**: Array of integers (frame counts at 30fps)
- **text**: Array of motion descriptions  
- Arrays must have equal length
- Each text[i] corresponds to lengths[i] frames

### Dataset Style Differences

**HumanML3D Style** (detailed descriptions):
```json
{
  "lengths": [120, 150],
  "text": [
    "a person walks forward slowly while looking around nervously",
    "the person stops and waves enthusiastically with both hands"
  ]
}
```

**Babel Style** (simple actions):
```json
{
  "lengths": [60, 45], 
  "text": [
    "walk forward",
    "turn left"
  ]
}
```

### Provided Examples
- `runners/jsons/composition_humanml.json` - Complex motion composition
- `runners/jsons/composition_babel.json` - Simple action sequence
- `runners/jsons/extrapolation_humanml.json` - Repeated motion (treadmill)
- `runners/jsons/extrapolation_babel.json` - Simple repetition

## Key Parameters

### `--bpe_denoising_step`
Controls quality vs smoothness trade-off:
- **Low values (30-100)**: Smoother transitions, less individual action quality
- **High values (800-1000)**: Better individual actions, more abrupt transitions
- **Recommended**: HumanML3D=60, Babel=125

### `--guidance_param`  
Text conditioning strength:
- **0.0**: Ignores text completely
- **2.5**: Strong text adherence (recommended)
- **Higher**: More faithful to text, potentially less natural

## Usage Examples

### Basic Generation Command
```bash
python -m runners.generate \
  --model_path ./results/humanml/FlowMDM/model000500000.pt \
  --instructions_file ./runners/jsons/composition_humanml.json \
  --bpe_denoising_step 60 \
  --guidance_param 2.5
```

### Memory-Optimized for Long Sequences
```bash
python -m runners.generate \
  --model_path ./results/humanml/FlowMDM/model000500000.pt \
  --instructions_file my_custom_sequence.json \
  --bpe_denoising_step 60 \
  --guidance_param 2.5 \
  --use_chunked_att \
  --num_repetitions 3
```

## Creating Custom Instructions

### Single Action
```json
{
  "lengths": [120],
  "text": ["a person walks forward confidently"]
}
```

### Action Sequence
```json
{
  "lengths": [80, 60, 90, 100],
  "text": [
    "walk to the table",
    "pick up the cup", 
    "sit down on chair",
    "drink from cup"
  ]
}
```

### Motion Extrapolation
```json
{
  "lengths": [100, 100, 100],
  "text": [
    "person jogs steadily",
    "continue jogging",
    "maintain same pace"
  ]
}
```

## Frame Duration Guidelines
- **30 fps**: 1 second = 30 frames
- **Typical ranges**: 30-200 frames per action
- **Walking**: ~60-120 frames
- **Complex actions**: 100-200 frames
- **Quick gestures**: 30-60 frames

## Troubleshooting

**Memory Issues**: Use `--use_chunked_att` for sequences >500 frames

**Poor Transitions**: Decrease `--bpe_denoising_step` (try 30-60)

**Low Action Quality**: Increase `--bpe_denoising_step` (try 100-200)

**Text Ignored**: Increase `--guidance_param` (try 3.0-5.0)

## Repository
https://github.com/imsight-forks/FlowMDM