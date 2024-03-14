# Stable Diffusion WebUI Aspect Ratio Resolutions selector

Extension for [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui.git) adding image aspect ratio resolutions selector buttons.

## Updates

- 11/02/2024 :Add common resolutions, hide Delete aspect ratio button.
- 20/02/2023 :warning: this update will remove your local config files (`aspect_ratios.txt` and `resolutions.txt`) and it will create new default ones. These can be then modified freely and preserved in the future. For more info read [here](https://github.com/alemelis/sd-webui-ar/issues/9).

## Install

Browse to the `Extensions` tab -> go to `Install from URL` -> paste in `https://github.com/xhoxye/sd-webui-ar_xhox` -> click `Install`


Here's how the UI looks like after installing this extension

<img width="666" alt="sd-webui-ar_xhox-UI 2024 02 11" src="https://github.com/xhoxye/sd-webui-ar_xhox/raw/main/sd-webui-ar_xhox-UI.png">

## Usage

- Click on the resolutions button you want to set

### Configuration

Resolutions presets are defined inside `/sd-webui-ar/Custom_resolutions.txt` file. For example,

```
640*480
480*640
1280*720
720*1280
1920*1080
1080*1920
```

Note the `#` marking the line as a comment, i.e. the extension is not reading that line. To use a custom value, un-comment the relative line by removing the starting `#`. 

The format to be used is `width*height, # optional comment`. As before, lines starting with `#` will be ignored.

## Calculator Panel
Use the calculator to determine new width or height values based on the aspect ratio of source dimensions.
- Set the source dimensions:
  - Enter manually, or
  - Click ⬇️ to get source dimentions from txt2img/img2img sliders, or
  - Click 🖼️ to get source dimensions from input image component on the current tab
- Click ⇅ to swap the width and height, if desired
- Set the desired width or height, then click either `Calculate Height` or `Calculate Width` to calculate the missing value
- Click `Apply` to send the values to the txt2txt/img2img sliders
--- 
<img width="666" style="border: solid 3px black;" alt="Basic usage of aspect ratio calculator" src="https://user-images.githubusercontent.com/121050401/229391634-4ec06027-e603-4672-bad9-ec77647b0941.gif">

