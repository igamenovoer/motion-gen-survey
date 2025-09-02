# Useful Information
- `flowmdm` source code: `model_zoo\FlowMDM`
- howto run flowmdm: `context\tasks\features\run-flowmdm\howto-evaluate-and-run-flowmdm.md`
- all required packages are already installed, in pixi environment `rt-flowmdm`, to run anything you need to `pixi run -e rt-flowmdm`
- smplx models are in `data\smplx`

# Task 1: Download Pretrained Models

we need to download the pretrained models for FlowMDM, note that, we are in windows, so we need to use powershell scripts instead of bash scripts. Now create the powershell script to download the models, in `model_zoo\FlowMDM\win64-scripts`