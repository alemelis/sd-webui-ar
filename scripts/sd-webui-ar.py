import contextlib
from pathlib import Path

import gradio as gr

import modules.scripts as scripts
from modules.ui_components import ToolButton

aspect_ratios_dir = scripts.basedir()


class ResButton(ToolButton):
    def __init__(self, res=(512, 512), **kwargs):
        super().__init__(**kwargs)

        self.w, self.h = res 

    def reset(self):
        return [self.w, self.h]


class ARButton(ToolButton):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)

        self.ar = ar

    def apply(self, w, h):
        if self.ar > 1.0:  # fix height, change width
            w = self.ar * h
        elif self.ar < 1.0:  # fix width, change height
            h = self.ar * w
        else:  # set minimum dimension to both
            min_dim = min([w, h])
            w, h = min_dim, min_dim

        return list(map(round, [w, h]))

    def reset(self, w, h):
        return [self.res, self.res]


def parse_aspect_ratios_file(filename):
    labels, values, comments = [], [], []
    file = Path(aspect_ratios_dir, filename)

    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        label, value = line.strip().split(",")
        comment = ""
        if "#" in value:
            value, comment = value.split("#")

        labels.append(label)
        values.append(value)
        comments.append(comment)

    return labels, values, comments


def parse_resolutions_file(filename):
    labels, values, comments = [], [], []
    file = Path(aspect_ratios_dir, filename)

    if not file.exists():
        return labels, values, comments

    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments

    for line in lines:
        if line.startswith("#"):
            continue

        label, width, height= line.strip().split(",")
        comment = ""
        if "#" in height:
            height, comment = height.split("#")
            
        resolution = (width, height)

        labels.append(label)
        values.append(resolution)
        comments.append(comment)

    return labels, values, comments

class AspectRatioScript(scripts.Script):
    def read_aspect_ratios(self):
        (
            self.aspect_ratio_labels,
            aspect_ratios,
            self.aspect_ratio_comments,
        ) = parse_aspect_ratios_file("aspect_ratios.txt")
        self.aspect_ratios = list(map(float, aspect_ratios))
        
        # TODO: check for duplicates
        
        # TODO: check for invalid values

        # TODO: use comments as tooltips
        # see https://github.com/alemelis/sd-webui-ar/issues/5

    def read_resolutions(self):
        self.res_labels, res, self.res_comments = parse_resolutions_file("resolutions.txt")
        self.res = [list(map(int, r)) for r in res]

    def title(self):
        return "Aspect Ratio picker"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        self.read_aspect_ratios()
        with gr.Row(elem_id="img2img_row_aspect_ratio"):
            btns = [
                ARButton(ar=ar, value=label)
                for ar, label in zip(
                    self.aspect_ratios,
                    self.aspect_ratio_labels,
                )
            ]

            with contextlib.suppress(AttributeError):
                for b in btns:
                    b.click(
                        b.apply,
                        inputs=[self.w, self.h],
                        outputs=[self.w, self.h],
                    )

        self.read_resolutions()
        with gr.Row(elem_id="img2img_row_resolutions"):
            btns = [
                ResButton(res=res, value=label)
                for res, label in zip(self.res, self.res_labels)
            ]

            with contextlib.suppress(AttributeError):
                for b in btns:
                    b.click(
                        b.reset,
                        outputs=[self.w, self.h],
                    )

    # https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/7456#issuecomment-1414465888
    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_width":
            self.w = component
        if kwargs.get("elem_id") == "txt2img_height":
            self.h = component
