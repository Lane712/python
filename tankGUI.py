import os
import time
import logging
import numpy as np
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from PIL import Image,ImageTk

## 配置日志文件
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("tank_logging.log",encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter(
    "[%(asctime)s][%(levelname)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
))
logger.addHandler(stream_handler)

## 幻影坦克处理函数
def light(pic):
    """将图像转换为灰度图并提升亮度"""
    pic = pic.convert('L')
    return pic.point(lambda p: (p >> 1) + 128)  # 使用 point 方法加速处理

def dark(pic):
    """将图像转换为灰度图并降低亮度"""
    pic = pic.convert('L')
    return pic.point(lambda p: p >> 1)  # 使用 point 方法加速处理

def fill_size(outpic, inpic):
    """调整两张图像的大小，扩展部分用黑/白色填充"""
    w_out, h_out = outpic.size
    w_in, h_in = inpic.size
    w, h = max(w_out, w_in), max(h_out, h_in)
    ssoutpic = Image.new('L', (w, h), 0xFF)  # 背景填充为白色
    ssinpic = Image.new('L', (w, h), 0x00)  # 背景填充为黑色
    ssoutpic.paste(outpic, ((w - w_out) // 2, (h - h_out) // 2))  # 居中粘贴
    ssinpic.paste(inpic, ((w - w_in) // 2, (h - h_in) // 2))  # 居中粘贴
    return ssoutpic, ssinpic

def adjust_size(outpic, inpic):
    # 获取两张图片的尺寸
    w_out, h_out = outpic.size
    w_in, h_in = inpic.size
    # 确保图片高度相同
    if h_out < h_in:
        scale_factor = h_out / h_in
        new_size = (int(w_in * scale_factor), h_out)
        inpic = inpic.resize(new_size, Image.LANCZOS)
        w_in, h_in = inpic.size
    elif h_out > h_in:
        scale_factor = h_in / h_out
        new_size = (int(w_out * scale_factor), h_in)
        outpic = outpic.resize(new_size, Image.LANCZOS)
        w_out, h_out = outpic.size
    # 确保里图片宽度不大于表图片
    if w_out < w_in:
        scale_factor = w_out / w_in
        new_size = (w_out, int(h_in * scale_factor))
        inpic = inpic.resize(new_size, Image.LANCZOS)
        w_in, h_in = inpic.size

    w, h = max(w_out, w_in), max(h_out, h_in)
    ssoutpic = Image.new('L', (w, h), 0xFF)  # 背景填充为白色
    ssinpic = Image.new('L', (w, h), 0x00)  # 背景填充为黑色
    ssoutpic.paste(outpic, ((w - w_out) // 2, (h - h_out) // 2))  # 居中粘贴
    ssinpic.paste(inpic, ((w - w_in) // 2, (h - h_in) // 2))  # 居中粘贴
    return ssoutpic, ssinpic

def tank(outpic, inpic):
    """根据两张图像生成带有透明度的新图像"""
    out_array = np.array(outpic, dtype=np.float32)
    in_array = np.array(inpic, dtype=np.float32)
    alpha = np.clip(255 - (out_array - in_array), 0, 255)  # 计算透明度
    # 避免除以零：将 alpha 中的零值替换为 1
    safe_alpha = np.where(alpha == 0, 1, alpha)
    # 使用 safe_alpha 进行计算
    lightness = np.where(alpha == 0, 0, (in_array / safe_alpha * 255)).astype(np.uint8)  # 计算亮度
    tank_out = Image.fromarray(np.dstack((lightness, alpha)).astype(np.uint8), mode='LA')  # 创建新图像
    return tank_out

## 主界面
class MainApp:
    def __init__(self,root):
        self.root = root
        self.out_image_path = ""
        self.in_image_path = ""
        self.output_path = ""
        self.output_time = int(time.time())
        self.tank_out_image = Image
        self.auto_save = tk.BooleanVar()
        self.has_generated = False
        # self.resize_pending = False
        # self.image_lock = threading.Lock()

        self.creat_widgets()
        # self.add_event()

    def creat_widgets(self):
        self.root.title("Tank Shadow GUI")
        self.root.geometry("640x480")
        self.root.minsize(width=480,height=360)

        self.load_out_image_button = ttk.Button(self.root, text="选择表图片",command=self.load_out_image)
        self.load_out_image_button.grid(row=1, column=0, sticky=tk.EW)
        self.out_image_label = ttk.Label(self.root)
        self.out_image_label.grid(row=2,column=0,columnspan=2)

        self.load_in_image_button = ttk.Button(self.root, text="选择里图片", command=self.load_in_image)
        self.load_in_image_button.grid(row=3, column=0, sticky=tk.EW)
        self.in_image_label = ttk.Label(self.root)
        self.in_image_label.grid(row=4,column=0,columnspan=2)

        self.generate_button = ttk.Button(self.root, text="合成", command=self.generate)
        self.generate_button.grid(row=5, column=0, sticky=tk.EW)
        self.output_image_label = ttk.Label(self.root)
        self.output_image_label.grid(row=6, column=0,columnspan=2)

        self.save_button = ttk.Button(self.root, text="另存为", command=self.save_image)
        self.save_button.grid(row=5, column=1,sticky=tk.EW)

        self.auto_save_checkbutton = ttk.Checkbutton(self.root,text="自动保存", onvalue=True, offvalue=False, variable=self.auto_save)
        self.auto_save_checkbutton.grid(row=7,column=0)
    
    # ## 添加事件
    # def add_event(self):
    #     root.bind("<Configure>",self.on_window_resize)
    # ## 窗口改变函数
    # def on_window_resize(self, event):
    #     if not self.resize_pending:
    #         self.resize_pending = True
    #         self.root.after(100, self.resize_image_display)
    # ## 图片随窗口大小改变而改变
    # def resize_image_display(self):
    #     with self.image_lock:
    #         self.resize_pending = False
    #         self.show_image(self.in_image_path, self.in_image_label)
    #         self.show_image(self.out_image_path, self.out_image_label)

    ## 加载表图片
    def load_out_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.out_image_path = file_path
            self.show_image(self.out_image_path, self.out_image_label)
            self.has_generated = False
            logging.info(f"Load out_image {self.out_image_path}")
    ## 加载里图片
    def load_in_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.in_image_path = file_path
            self.show_image(self.in_image_path, self.in_image_label)
            self.has_generated = False
            logging.info(f"Load in_image {self.in_image_path}")
    ## 展示图片
    def show_image(self, image_path, image_display):
        image = Image.open(image_path)
        image.thumbnail((self.root.winfo_width()/2, self.root.winfo_height()/2))
        photo = ImageTk.PhotoImage(image)
        image_display.config(image=photo)
        image_display.image = photo

    ## 文件检查
    def file_check(self):
        is_ok = True
        if not os.path.exists(self.out_image_path):
            logging.error(f"Out_image doesn't exist! path:{self.out_image_path}")
            is_ok = False
        if not os.path.exists(self.in_image_path):
            logging.error(f"In_image doesn't exist! path:{self.in_image_path}")
            is_ok = False
        return is_ok
    ## 保存图片
    def save_image(self):
        if not self.has_generated:
            messagebox.showerror(title="提示",message=f"图片未合成！")
            return
        output = filedialog.asksaveasfilename(title="另存为", initialfile=f"tank_out_{self.output_time}.png", filetypes=[("默认格式",".png"),("压缩格式",".webp")])
        if output:
            self.tank_out_image.save(output)
            logging.info(f"Sava at {output}")
    ## 合成
    def generate(self):
        if not self.file_check():
            # logging.info("Generate quit! Errors are before.")
            return
        if self.has_generated:
            logging.info(f"Do not generate twice!")
            messagebox.showinfo(title="提示",message="重复生成！")
            return
        try:
            out_image = Image.open(self.out_image_path)
            in_image = Image.open(self.in_image_path)
            # 处理图片
            light_out = light(out_image)
            dark_in = dark(in_image)
            newp1, newp2 = adjust_size(light_out, dark_in)
            self.tank_out_image = tank(newp1, newp2)
            self.output_time = int(time.time())
            self.output_path = f"tank_out_{self.output_time}.png"
            self.has_generated = True
            logging.info(f"Success in generating!")
            # 保存图片
            if self.auto_save.get():
                self.tank_out_image.save(self.output_path)
                logging.info(f"Auto save at {self.output_path}")
        except Exception as e:
            logging.error(f"{e}")
       
## 主程序入口
if __name__ == '__main__':
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
