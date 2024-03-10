import contextlib
from pathlib import Path

import gradio as gr

import modules.scripts as scripts
from modules.ui_components import ToolButton # 导入ToolButton 系统组件样式

from math import gcd

aspect_ratios_dir = scripts.basedir()

calculator_symbol = "\U0001F5A9" # 计算器符号
switch_values_symbol = "\U000021C5" # 交换符号
get_dimensions_symbol = "\u2B07\ufe0f" # 获取尺寸符号
get_image_dimensions_symbol = "\U0001F5BC" # 获取图片尺寸符号


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

    def apply(self, w, h): # 是一个类方法，接受两个参数w和h，表示宽度和高度。根据self.ar的值，函数会根据不同的条件对宽度和高度进行调整。
        if self.ar > 1.0:  # fix height, change width   固定高度，改变宽度。函数会根据self.ar计算出新的宽度w，并计算出新的高度h。
            h = 512
            w = self.ar * h
        elif self.ar < 1.0:  # fix width, change height 固定宽度，改变高度。函数会根据self.ar计算出新的高度h，并计算出新的宽度w。
            w = 512
            h = w / self.ar
        else:  # set minimum dimension to both 设置两个值的最小尺寸。函数会找到w和h中的最小值，然后将w和h都设置为该最小值。
            min_dim = min([w, h])
            w, h = min_dim, min_dim

        return list(map(round, [w, h])) # 函数会将调整后的宽度和高度都四舍五入到最接近的整数，并以列表的形式返回。

    def reset(self, w, h): # 用于更新UI界面上的宽高数值滑块。是一个类方法，接受两个参数w和h。它返回一个列表，列表中包含两个元素，这两个元素都是self.res的值。
        return [self.res, self.res]


def parse_aspect_ratios_file(filename): # 该函数用于解析预设的宽高比例文件。
    labels, values, comments = [], [], [] # 定义三个空列表：labels、values和comments。这些列表将用于存储标签、值和注释。
    file = Path(aspect_ratios_dir, filename)

    # 首先，函数会检查文件是否存在，如果不存在则返回三个空列表。
    if not file.exists():
        return labels, values, comments # 返回三个空列表：显示的标签，值，注解
    
    # 如果文件存在，函数会打开文件并读取所有行。
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        return labels, values, comments # 返回三个空列表：显示的标签、值和注解。
    
    # 排除以 "#" 开头的注释行和不包含逗号的行。
    for line in lines:
        if line.startswith("#"): # 如果行以#开头，则使用continue语句跳过该行；
            continue

        if ',' not in line: # 如果行不包含逗号，则同样使用continue语句跳过该行。
            continue

        # 对于每行，函数会尝试将其拆分为标签和值，并将注解保存在变量 comment 中。
        try:
            label, value = line.strip().split(",")
            comment = ""
            if "#" in value: # 如果值中包含 "#" 符号，则将值和注释拆分为两个部分。
                value, comment = value.split("#")
        # 如果拆分失败，则跳过该行并打印错误信息。该函数是一个异常处理语句，用于处理在读取宽高比例文件时可能出现的ValueError异常。        
        except ValueError:
            print(f"skipping badly formatted line in aspect ratios file: {line}") # 跳过格式错误的宽高比例文件行，错误信息中会包含出现异常的行号和内容。
            continue
        # 将标签、值和注解添加到相应的列表中。
        labels.append(label)
        values.append(eval(value))
        comments.append(comment)

    return labels, values, comments # 返回三个列表：显示的标签、值和注解。


def parse_resolutions_file(filename, resolution_type):
    # 该函数的功能是解析一个分辨率文件，将文件中的每一行解析为一个分辨率，并将解析结果存储在三个列表中：labels（标签）、values（分辨率）和comments（注释）。函数的输入参数是一个文件名，函数返回一个包含解析结果的元组。
    labels, values, comments = [], [], [] # 定义三个空列表：labels、values和comments。这些列表将用于存储标签、值和注释。
    #file = Path(aspect_ratios_dir, filename)
    file = Path(aspect_ratios_dir, resolution_type + "_resolutions.txt")

    if not file.exists():
        return labels, values, comments # 函数首先检查文件是否存在，如果不存在则返回空的labels、values和comments列表。

    with open(file, "r", encoding="utf-8") as f: # 然后，函数打开文件并逐行读取文件内容。
        lines = f.readlines()

    if not lines:
        return labels, values, comments # 如果文件为空，则返回空的labels、values和comments列表。

    for line in lines:
        if line.startswith("#"): # 对于每一行，函数首先检查是否以"#"开头，如果是则跳过该行。
            continue

        if '*' not in line: # 然后，函数检查该行是否包含*号，如果不包含则跳过该行。
            continue

        try:
            comment = ""  # 在这里定义comment为空字符串
            width, height = line.strip().split("*")  # 尝试将该行按照井号分割为宽高两个部分：width, height。
            if "#" in width: # 如果#在前半部分，跳过
                print(f"skipping line with '#' in the first part in resolutions file: {line}")
                continue
            if "#" in height: # 如果#在后半部分，继续分割
                height, comment = height.split("#")
        #    label, comment = line.strip().split("#")  # 尝试将该行按照井号分割为两个部分：label和comment。
        #    width, height = label.strip().split("*")  # 然后，将label按照星号分割为两个部分：width和height。

        except ValueError:
            print(f"skipping badly formatted line in resolutions file: {line}") # 如果分割失败，则打印错误信息并跳过该行。跳过格式错误的分辨率文件行
            continue

        resolution = (width, height) # 如果分割成功，则将label添加到labels列表中，将resolution添加到values列表中，将comment添加到comments列表中。

        # label = f"{width}x{height}"
        label = add_ratio(width, height)

        labels.append(label)
        values.append(resolution)
        comments.append(comment)

    return labels, values, comments # 最后，函数返回包含解析结果的元组。


# TODO: write a generic function handling both cases 待办事项：编写一个通用的函数，处理分别写入多个文件的情况

def write_aspect_ratios_file(filename): # 该函数的功能是将多个宽高比信息的列表写入到指定的文件中。函数接受一个参数filename，表示要写入的文件名。
    # 定义了一个列表aspect_ratios，其中包含了常用SD1.5宽高比例的信息。
    aspect_ratios = [ 
        "1:1, 1.0 # 1:1 ratio based on minimum dimension\n",
        "2:3, 2/3 # \n",
        "3:2, 3/2 # Set width based on 3:2 ratio to height\n",
        "3:4, 3/4 # \n",
        "4:3, 4/3 # Set width based on 4:3 ratio to height\n",
        "16:9, 16/9 # Set width based on 16:9 ratio to height",
    ]
    with open(filename, "w", encoding="utf-8") as f: # 使用with open语句打开指定的文件，并以utf-8编码写入aspect_ratios列表中的内容。
        f.writelines(aspect_ratios) # 最后，使用f.writelines(aspect_ratios)将列表中的内容写入文件中。


def write_resolutions_file(filename, resolution_type): # 该函数的功能是将一个包含多个分辨率的列表写入到指定的文件中。
    # 定义一个名为resolutions的列表，其中包含了多个字符串元素。每个字符串代表一种图像分辨率配置，
    if resolution_type == "SD15":
        resolutions = [
            # ... SD1.5 分辨率的列表 ...
            "#1024*1024 # 1:1 square SDXL方形。这一行是格式示例，以下列表不建议修改，推荐修改使用自定义分辨率的文件",
            "512*512",
            "512*768",
            "768*512",
            "768*1024",
            "1024*768",
            "1024*1024",
        ]
    elif resolution_type == "Custom":
        resolutions = [
            # ... 自定义分辨率的列表 ...
            "#1024*1024 # 1:1 square SDXL方形。这一行是格式示例，推荐修改使用",
            "640*480",
            "480*640",
            "1280*720",
            "720*1280",
            "1920*1080",
            "1080*1920",
        ]
    elif resolution_type == "SDXL":
        resolutions = [
            # ... SDXL分辨率的列表 ...
            "#1024*1024 # 1:1 square SDXL方形。这一行是格式示例，以下列表不建议修改，推荐修改使用自定义分辨率的文件",
            "704*1408",
            "704*1344",
            "768*1344",
            "768*1280",
            "832*1216",
            "832*1152",
            "896*1152",
            "896*1088",
            "960*1088",
            "960*1024",
            "1024*960",
            "1088*960",
            "1088*896",
            "1152*896",
            "1152*832",
            "1216*832",
            "1280*768",
            "1344*768",
            "1344*704",
            "1407*704",
            "1472*704",
            "1536*640",
            "1600*640",
            "1664*576", 
            ]
    else:
        raise ValueError("Unsupported resolution type")
        
    filename = Path(aspect_ratios_dir, f"{resolution_type}_resolutions.txt") # 根据 resolution_type 生成对应的文件名
    with open(filename, "w", encoding="utf-8") as f:
        for res in resolutions:
            f.write("%s\n" % res)
    #with open(filename, "w", encoding="utf-8") as f: # 使用with open语句打开指定的文件，并以utf-8编码写入resolutions列表中的内容。
        #f.writelines(resolutions) #调用文件对象f的writelines()方法，将resolutions列表中的所有字符串依次写入到已打开的文件中。


def write_js_titles_file(button_titles):
    filename = Path(aspect_ratios_dir, "javascript", "button_titles.js")
    content = [
        "// Do not put custom titles here. This file is overwritten each time the WebUI is started.\n" # 不要在这里添加自定义标题。每次启动WebUI时，都会覆盖此文件
    ]
    content.append("ar_button_titles = {\n")
    counter = 0
    while counter < len(button_titles[0]):
        content.append(
            f'    "{button_titles[0][counter]}" : "{button_titles[1][counter]}",\n'
        )
        counter = counter + 1
    content.append("}")

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(content)

def add_ratio(width, height):
    a, b = int(width), int(height)
    g = gcd(a, b)
    c, d = 1, 1
    if g < 8:
        if (a, b) == (768, 1366):
            c, d = 9, 16
        elif (a, b) == (915, 1144):
            c, d = 4, 5
        elif (a, b) == (1182, 886):
            c, d = 4, 3
        elif (a, b) == (1366, 768):
            c, d = 16, 9
        elif (a, b) == (1564, 670):
            c, d = 21, 9
    else:
        c, d = a // g, b // g
    return f'{a}x{b} | {c}:{d}'

def get_reduced_ratio(n, d): # 该函数的功能是根据给定的两个整数n和d，计算并返回一个缩放比例。用在尺寸计算器显示比例
    n, d = list(map(int, (n, d))) # 首先，将n和d转换为整数类型。

    if n == d:
        return "1:1"

    if n < d:
        div = gcd(d, n) # 计算n和d的最大公约数，并将其赋值给变量div。
    else:
        div = gcd(n, d) # 如果n大于等于d，则计算d和n的最大公约数，并将其赋值给变量div。

    w = int(n) // div # w是n除以div的整数商
    h = int(d) // div # h是d除以div的整数商。

    if w == 8 and h == 5: # 如果w等于8且h等于5，则将w的值修改为16，h的值修改为10。
        w = 16
        h = 10

    return f"{w}:{h}" # 最后，将w和h的值以字符串的形式返回，格式为"w:h"。


def solve_aspect_ratio(w, h, n, d): # 用于计算缩放后的宽高比数值
    # 根据输入的参数，如果宽度不为0且不为None，则返回宽度除以(n / d)的值，四舍五入到最接近的整数。
    if w != 0 and w:
        return round(w / (n / d))
    # 如果高度不为0且不为None，则返回高度乘以(n / d)的值，四舍五入到最接近的整数。
    elif h != 0 and h:
        return round(h * (n / d))
    # 如果宽度和高度都为0或None，则返回0。
    else:
        return 0


class AspectRatioScript(scripts.Script): # 定义这个插件脚本的类
    def read_aspect_ratios(self):
        ar_file = Path(aspect_ratios_dir, "aspect_ratios.txt") # 读取一个名为"aspect_ratios.txt"的比例文件

        if not ar_file.exists():
            write_aspect_ratios_file(ar_file) # 如果文件不存在，则会调用write_aspect_ratios_file函数创建该文件。

        (
            self.aspect_ratio_labels,
            aspect_ratios,
            self.aspect_ratio_comments,
        ) = parse_aspect_ratios_file("aspect_ratios.txt") # 调用 parse_aspect_ratios_file 函数将其解析为三个变量：self.aspect_ratio_labels、aspect_ratios和self.aspect_ratio_comments。

        self.aspect_ratios = list(map(float, aspect_ratios)) # 将aspect_ratios列表中的每个元素转换为浮点数

        #待办事项：

        # TODO: check for duplicates 检查重复值

        # TODO: check for invalid values 检查无效值

        # TODO: use comments as tooltips 鼠标悬浮提示

        # see https://github.com/alemelis/sd-webui-ar/issues/5

    def read_resolutions(self, resolution_type):
        res_file = Path(aspect_ratios_dir, f"{resolution_type}_resolutions.txt") # # 根据 resolution_type 读取对应的分辨率文件，并将其解析为三个变量：res_labels、res和res_comments

        if not res_file.exists():
            write_resolutions_file(res_file, resolution_type) # 如果文件不存在，则会调用 write_resolutions_file 函数创建该文件。

        self.res_labels, res, self.res_comments = parse_resolutions_file( # 调用 parse_resolutions_file 函数将其解析为三个变量：res_labels、res和res_comments
            f"{resolution_type}_resolutions.txt", resolution_type
        )
        self.res = [list(map(int, r)) for r in res] # 将 res 列表中的每个元素转换为整数列表。

    def title(self):
        return "Aspect Ratio picker-xhox"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(open=True, label=self.title()): #可折叠面板，用于显示插件脚本的标题，折叠默认打开

            with gr.Column(
                elem_id=f'{"img" if is_img2img else "txt"}2img_container_aspect_ratio'
            ):
                
                with gr.Accordion(open=False, label='常用SD1.5宽高比例', visible=False): # 常用SD1.5宽高比例 标题，可折叠面板，准备删除
                    self.read_aspect_ratios() #读取宽高比例文件

                    with gr.Row( 
                        elem_id=f'{"img" if is_img2img else "txt"}2img_row_aspect_ratio'
                    ):
                        # Aspect Ratio buttons 宽高比例按钮。创建了一个ARButton的列表，其中每个按钮代表一个不同的宽高比例。
                        btns = [
                            ARButton(ar=ar, value=label)
                            for ar, label in zip(
                                self.aspect_ratios,
                                self.aspect_ratio_labels,
                            )
                        ]

                        with contextlib.suppress(AttributeError): # 使用contextlib.suppress来捕获可能发生的AttributeError异常
                            # 遍历ARButton列表，根据is_img2img的值设置不同的分辨率，并为每个按钮添加点击事件，当按钮被点击时，会调用apply函数，并传递输入和输出的分辨率。
                            for b in btns:
                                if is_img2img:
                                    resolution = [self.i2i_w, self.i2i_h]
                                else:
                                    resolution = [self.t2i_w, self.t2i_h]

                                b.click(
                                    b.apply,
                                    inputs=resolution,
                                    outputs=resolution,
                                )

                arc_title_heading = gr.Markdown(value="SD1.5 resolutions") # SD1.5 常用分辨率 标题
                self.read_resolutions(resolution_type="SD15") # 读取SD1.5分辨率文件
                for i in range(0, len(self.res), 6):
                    with gr.Row(elem_id=f'{"img" if is_img2img else "txt"}2img_row_resolutions'):                    

                        # Resolution buttons 分辨率按钮
                        btns = [
                            ResButton(res=res, value=label)
                            for res, label in zip(self.res[i:i+6], self.res_labels[i:i+6])
                        ]
                        with contextlib.suppress(AttributeError): # 使用contextlib.suppress来抑制可能发生的AttributeError异常，并且遍历按钮列表。
                            # 对于每个按钮，根据条件设置分辨率（resolution），然后调用按钮的click方法，传入一个回调函数（b.reset）和输出分辨率（outputs）。
                            for b in btns:
                                if is_img2img:
                                    resolution = [self.i2i_w, self.i2i_h]
                                else:
                                    resolution = [self.t2i_w, self.t2i_h]

                                b.click(
                                    b.reset,
                                    outputs=resolution,
                                )


                arc_title_heading = gr.Markdown(value="SDXL base resolutions") # SDXL 官方分辨率 标题
                self.read_resolutions(resolution_type="SDXL") #读取SDXL分辨率文件

                # 该函数是一个for循环，用于遍历一个列表（self.res）中的元素，并且每次遍历6个元素。在每次遍历中，使用gr.Row创建一个行元素，并且根据条件设置行元素的id。然后，根据条件创建一组按钮（btns），每个按钮都包含一个分辨率（res）和一个标签（label）。
                for i in range(0, len(self.res), 6):
                    with gr.Row(elem_id=f'{"img" if is_img2img else "txt"}2img_row_resolutions'):                    

                        # Resolution buttons 分辨率按钮
                        btns = [
                            ResButton(res=res, value=label)
                            for res, label in zip(self.res[i:i+6], self.res_labels[i:i+6])
                        ]
                        with contextlib.suppress(AttributeError): # 使用contextlib.suppress来抑制可能发生的AttributeError异常，并且遍历按钮列表。
                            # 对于每个按钮，根据条件设置分辨率（resolution），然后调用按钮的click方法，传入一个回调函数（b.reset）和输出分辨率（outputs）。
                            for b in btns:
                                if is_img2img:
                                    resolution = [self.i2i_w, self.i2i_h]
                                else:
                                    resolution = [self.t2i_w, self.t2i_h]

                                b.click(
                                    b.reset,
                                    outputs=resolution,
                                )

                with gr.Accordion(open=False, label='Custom resolutions'): # 自定义分辨率 标题，可折叠面板，默认折叠
                    self.read_resolutions(resolution_type="Custom") # 读取自定义分辨率文件
                    for i in range(0, len(self.res), 6):
                        with gr.Row(elem_id=f'{"img" if is_img2img else "txt"}2img_row_resolutions'):                    

                            # Resolution buttons 分辨率按钮
                            btns = [
                                ResButton(res=res, value=label)
                                for res, label in zip(self.res[i:i+6], self.res_labels[i:i+6])
                            ]
                            with contextlib.suppress(AttributeError): # 使用contextlib.suppress来抑制可能发生的AttributeError异常，并且遍历按钮列表。
                                # 对于每个按钮，根据条件设置分辨率（resolution），然后调用按钮的click方法，传入一个回调函数（b.reset）和输出分辨率（outputs）。
                                for b in btns:
                                    if is_img2img:
                                        resolution = [self.i2i_w, self.i2i_h]
                                    else:
                                        resolution = [self.t2i_w, self.t2i_h]

                                    b.click(
                                        b.reset,
                                        outputs=resolution,
                                    )

                    # 移除按钮的定义
                    # Toggle calculator display button 切换显示计算器的按钮
                    # arc_hide_calculator = gr.Button(
                        # value="Calc",
                        # visible=True,
                        # variant="primary",
                        # elem_id="arc_hide_calculator_button",
                    # )
                    # arc_show_calculator = gr.Button(
                        # value="Calc",
                        # visible=False,
                        # variant="secondary",
                        # elem_id="arc_show_calculator_button",
                    # )

                    # Write button_titles.js with labels and comments read from aspect ratios and resolutions files 编写一个名为button_titles.js的文件，其中的标签和注释是从宽高比和分辨率文件中读取的
                    button_titles = [self.aspect_ratio_labels + self.res_labels]
                    button_titles.append(self.aspect_ratio_comments + self.res_comments)
                    write_js_titles_file(button_titles)

                    # dummy components needed for JS function JS函数所需的虚拟组件 
                    dummy_text1 = gr.Text(visible=False)
                    dummy_text2 = gr.Text(visible=False)
                    dummy_text3 = gr.Text(visible=False)
                    dummy_text4 = gr.Text(visible=False)

                    # Aspect Ratio Calculator 宽高比计算器
                    with gr.Column(
                        visible=True, variant="panel", elem_id="arc_panel"
                    ) as arc_panel:
                        arc_title_heading = gr.Markdown(value=" Aspect Ratio Calculator") # 宽高比计算器标题
                        with gr.Row():
                            with gr.Column(min_width=150):
                                arc_width1 = gr.Number(label="Width 1")
                                arc_height1 = gr.Number(label="Height 1")

                            with gr.Column(min_width=150):
                                arc_desired_width = gr.Number(label="Width 2")
                                arc_desired_height = gr.Number(label="Height 2")

                            with gr.Column(min_width=150):
                                arc_ar_display = gr.Markdown(value="Aspect Ratio:")
                                with gr.Row(
                                    elem_id=f'{"img" if is_img2img else "txt"}2img_arc_tool_buttons'
                                ):
                                    # Switch resolution values button 交换分辨率宽与高值按钮
                                    arc_swap = ToolButton(value=switch_values_symbol)
                                    arc_swap.click(
                                        lambda w, h, w2, h2: (h, w, h2, w2),
                                        inputs=[
                                            arc_width1,
                                            arc_height1,
                                            arc_desired_width,
                                            arc_desired_height,
                                        ],
                                        outputs=[
                                            arc_width1,
                                            arc_height1,
                                            arc_desired_width,
                                            arc_desired_height,
                                        ],
                                    )

                                    with contextlib.suppress(AttributeError):
                                        # For img2img tab 图生图标签页生效
                                        if is_img2img:
                                            # Get slider dimensions button 获取滑块尺寸按钮
                                            resolution = [self.i2i_w, self.i2i_h]
                                            arc_get_img2img_dim = ToolButton(
                                                value=get_dimensions_symbol
                                            )
                                            arc_get_img2img_dim.click(
                                                lambda w, h: (w, h),
                                                inputs=resolution,
                                                outputs=[arc_width1, arc_height1],
                                            )

                                            # Javascript function to select image element from current img2img tab JavaScript函数，用于从当前img2img选项卡中选择图像元素
                                            current_tab_image = """
                                                function current_tab_image(...args) {
                                                    const tab_index = get_img2img_tab_index();
                                                    // Get current tab's image (on Batch tab, use image from img2img tab)
                                                    if (tab_index == 5) {
                                                        image = args[0];
                                                    } else {
                                                        image = args[tab_index];
                                                    }
                                                    // On Inpaint tab, select just the image and drop the mask
                                                    if (tab_index == 2 && image !== null) {
                                                        image = image["image"];
                                                    }
                                                    return [image, null, null, null, null];
                                                }

                                            """

                                            # Get image dimensions 获取图像尺寸
                                            def get_dims(
                                                img: list,
                                                dummy_text1,
                                                dummy_text2,
                                                dummy_text3,
                                                dummy_text4,
                                            ):
                                                if img:
                                                    width = img.size[0]
                                                    height = img.size[1]
                                                    return width, height
                                                else:
                                                    return 0, 0

                                            # Get image dimensions button 获取图像尺寸按钮
                                            arc_get_image_dim = ToolButton(
                                                value=get_image_dimensions_symbol
                                            )
                                            arc_get_image_dim.click(
                                                fn=get_dims,
                                                inputs=self.image,
                                                outputs=[arc_width1, arc_height1],
                                                _js=current_tab_image,
                                            )

                                        else:
                                            # For txt2img tab 文生图标签页生效
                                            # Get slider dimensions button 获取滑块尺寸按钮
                                            resolution = [self.t2i_w, self.t2i_h]
                                            arc_get_txt2img_dim = ToolButton(
                                                value=get_dimensions_symbol
                                            )
                                            arc_get_txt2img_dim.click(
                                                lambda w, h: (w, h),
                                                inputs=resolution,
                                                outputs=[arc_width1, arc_height1],
                                            )

                            # Update aspect ratio display on change 使用 change事件 更新比例显示
                            arc_width1.change(
                                lambda w, h: (f"Aspect Ratio: **{get_reduced_ratio(w,h)}**"),
                                inputs=[arc_width1, arc_height1],
                                outputs=[arc_ar_display],
                            )
                            arc_height1.change(
                                lambda w, h: (f"Aspect Ratio: **{get_reduced_ratio(w,h)}**"),
                                inputs=[arc_width1, arc_height1],
                                outputs=[arc_ar_display],
                            )

                        with gr.Row():
                            # Calculate and Apply buttons 计算和应用按钮
                            arc_calc_height = gr.Button(value="Calculate Height",scale=1)
                            arc_calc_height.click(
                                lambda w2, w1, h1: (solve_aspect_ratio(w2, 0, w1, h1)),
                                inputs=[arc_desired_width, arc_width1, arc_height1],
                                outputs=[arc_desired_height],
                            )
                            arc_calc_width = gr.Button(value="Calculate Width", scale=1)
                            arc_calc_width.click(
                                lambda h2, w1, h1: (solve_aspect_ratio(0, h2, w1, h1)),
                                inputs=[arc_desired_height, arc_width1, arc_height1],
                                outputs=[arc_desired_width],
                            )
                            arc_apply_params = gr.Button(value="Apply")
                            with contextlib.suppress(AttributeError):
                                if is_img2img:
                                    resolution = [self.i2i_w, self.i2i_h]
                                else:
                                    resolution = [self.t2i_w, self.t2i_h]

                                arc_apply_params.click(
                                    lambda w2, h2: (w2, h2),
                                    inputs=[arc_desired_width, arc_desired_height],
                                    outputs=resolution,
                                )

                    # 移除按钮的定义
                    # Show calculator pane (and reset number input values)  显示计算器面板（以及重置数字输入值），点击事件
                    # arc_show_calculator.click(
                        # lambda: [
                            # gr.update(visible=True),
                            # gr.update(visible=False),
                            # gr.update(visible=True),
                            # gr.update(value=512),
                            # gr.update(value=512),
                            # gr.update(value=0),
                            # gr.update(value=0),
                            # gr.update(value="Aspect Ratio: **1:1**"),
                        # ],
                        # None,
                        # [
                            # arc_panel,
                            # arc_show_calculator,
                            # arc_hide_calculator,
                            # arc_width1,
                            # arc_height1,
                            # arc_desired_width,
                            # arc_desired_height,
                            # arc_ar_display,
                        # ],
                    # )
                    # Hide calculator pane 隐藏计算器面板
                    # arc_hide_calculator.click(
                        # lambda: [
                            # gr.update(visible=False),
                            # gr.update(visible=True),
                            # gr.update(visible=False),
                        # ],
                        # None,
                        # [arc_panel, arc_show_calculator, arc_hide_calculator],
                    # )

    # https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/7456#issuecomment-1414465888
    def after_component(self, component, **kwargs):
        if kwargs.get("elem_id") == "txt2img_width":
            self.t2i_w = component
        if kwargs.get("elem_id") == "txt2img_height":
            self.t2i_h = component

        if kwargs.get("elem_id") == "img2img_width":
            self.i2i_w = component
        if kwargs.get("elem_id") == "img2img_height":
            self.i2i_h = component

        if kwargs.get("elem_id") == "img2img_image":
            self.image = [component]
        if kwargs.get("elem_id") == "img2img_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img2maskimg":
            self.image.append(component)
        if kwargs.get("elem_id") == "inpaint_sketch":
            self.image.append(component)
        if kwargs.get("elem_id") == "img_inpaint_base":
            self.image.append(component)
