# Useful Information
- `flowmdm` source code: `model_zoo\FlowMDM`
- `flowmdm` has a local pixi environment in the same dir as its source code, use `pixi run -e latest <your command>` to run commands, when your `pwd` is `model_zoo\FlowMDM`
- `flowmdm` pyproject.toml has defined tasks for examples
  - `generate-motion-ex`: run motion generation
  - `show-motion-ex`: visualize generated motion
- smplx models are in `data\smplx`, source code is in `context/refcode/smplx`
- you can use `jq` to parse and create json files
- `HumanML3D` source code: `context/refcode/HumanML3D`, you can find text2motion skeleton definitions there

# Task 1: Figure out FlowMDM output coordinate

- `output-spec` with info about output format:  `model_zoo\FlowMDM\explain\about-flowmdm-output-format.md`, not very detailed.

figure out these questions:
- is the output skeleton consistent with smplx or smplh, or which smpl model variant?
- the output skeleton is given as 22 joint points, but smpl series models uses rotation vector per-joint to represent pose, what is the mapping between the two?
- the output skeleton by `flowmdm` has translation and orientation, where are these information in its generation process, specifically, which part of the source code?

save this info in `model_zoo\FlowMDM\explain\howto-interpret-flowmdm-output.md`

## If you want to run python code

- DO NOT run inline python code in cli, create a temp script in `<workspace>/tmp` dir instead, and use `pixi run -e latest` to run it
- ALWAYS make sure your pwd is in `flowmdm` source code dir.

