import contextlib
from pathlib import Path

import gradio as gr

import modules.scripts as scripts
from modules.ui_components import ToolButton

aspect_ratios_dir = scripts.basedir()


class ARButton(ToolButton):
    def __init__(self, ar=1.0, **kwargs):
        super().__init__(**kwargs)

        self.ar = ar

    def apply(self, w, h):
        if self.ar > 1.0:  # fix height, change width
            w = self.ar*h
        elif self.ar < 1.0:  # fix width, change height
            h = self.ar*w
        else:  # set minimum dimension to both
            min_dim = min([w, h])
            w, h = min_dim, min_dim

        return list(map(round, [w, h]))


class AspectRatioScript(scripts.Script):
    aspect_ratios = [1, 3/2, 4/3, 16/9]
    aspect_ratio_labels = ["1:1", "3:2", "4:3", "16:9"]

    def read_aspect_ratios(self):
        aspect_ratios_file = Path(aspect_ratios_dir, "aspect_ratios.txt")

        if not aspect_ratios_file.exists():
            return

        with open(aspect_ratios_file, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            if line.startswith('#'):
                continue

            label, ratio = line.strip().split(',')
            if '#' in ratio:
                ratio = ratio.split('#')[0]
            ratio = float(ratio)

            if label in self.aspect_ratio_labels or ratio in self.aspect_ratios:
                continue

            self.aspect_ratios.append(ratio)
            self.aspect_ratio_labels.append(label)

    def title(self):
        return "Aspect Ratio picker"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        self.read_aspect_ratios()
        with gr.Row(elem_id="img2img_row_aspect_ratio"):
            btns = [ARButton(ar=ar, value=label) for ar, label in zip(
                self.aspect_ratios, self.aspect_ratio_labels)]

            with contextlib.suppress(AttributeError):
                for b in btns:
                    b.click(b.apply, inputs=[self.w, self.h], outputs=[
                            self.w, self.h])

    # https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/7456#issuecomment-1414465888
    def after_component(self, component, **kwargs):
        if kwargs.get('elem_id') == 'txt2img_width':
            self.w = component
        if kwargs.get('elem_id') == 'txt2img_height':
            self.h = component
