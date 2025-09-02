# Useful Information
- `flowmdm` source code: `model_zoo\FlowMDM`
- howto run flowmdm: `context\tasks\features\run-flowmdm\howto-evaluate-and-run-flowmdm.md`
- all required packages are already installed, in pixi environment `rt-flowmdm`, to run anything you need to `pixi run -e rt-flowmdm`
- smplx models are in `data\smplx`
- you can use `jq` to parse and create json files

# Task 1: Download Pretrained Models

based on `context\tasks\features\run-flowmdm\about-flowmdm-text-to-motion-generation.md`, create a simple walking animation:
- segment 1: "a person walks forwards and then stop" (60 frames)
- segment 2: "a person walks backwards to the origin" (60 frames)

**Deliverables**:
- related scripts and json files should be put in `model_zoo\FlowMDM\tests\simple-walk`
- output should be put in `tmp/FlowMDM/simple-walk`