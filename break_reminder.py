import os
import sys
import time
import json
import threading
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import pygame
import pystray
from pystray import MenuItem as item
from plyer import notification

# 初始化pygame用于播放提醒音效
pygame.mixer.init()

# 默认配置
DEFAULT_CONFIG = {
    "work_time": 1,  # work time (minutes)
    "break_time": 5,  # break time (minutes)
    "animation_folder": "animations",  # animation folder
    "animation_speed": 100,  # animation speed (milliseconds)
    "sound_enabled": True,  # whether to enable sound
    "sound_file": "sounds/test.mp3",  # sound file path
    "auto_start": True,  # whether to auto start
    "minimize_to_tray": True,  # whether to minimize to tray
    "show_notifications": True  # whether to show notifications
}

class BreakReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("休息提醒")
        self.root.geometry("400x570")
        self.root.resizable(False, False)
        
        # set theme
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # load config
        self.config = self.load_config()
        
        # initialize variables
        self.timer_running = False
        self.work_timer = None
        self.break_timer = None
        self.remaining_work_time = self.config["work_time"] * 60
        self.remaining_break_time = self.config["break_time"] * 60
        self.is_break_time = False
        self.animation_window = None
        
        # create icon for tray
        self.icon_image = Image.open("images/icon.png") if os.path.exists("images/icon.png") else self.create_default_icon()
        self.create_system_tray()
        
        # create UI
        self.create_ui()
        
        # 监听窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # 如果设置了自动开始，则启动计时器
        if self.config["auto_start"]:
            self.start_timer()
        # 加载音乐
       
    
    def create_default_icon(self):
        """创建默认图标"""
        img = Image.new('RGB', (64, 64), color='blue')
        return img
    
    def create_system_tray(self):
        """创建系统托盘图标"""
        menu = (
            item('显示', self.show_window),
            item('开始/暂停', self.toggle_timer),
            item('退出', self.quit_app)
        )
        self.tray_icon = pystray.Icon("break_reminder", self.icon_image, "休息提醒", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def create_ui(self):
        """创建用户界面"""
        # 创建标签框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 标题
        ctk.CTkLabel(self.main_frame, text="休息提醒", font=("Arial", 24, "bold")).pack(pady=10)
        
        # 状态框架
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # 状态标签
        self.status_label = ctk.CTkLabel(status_frame, text="准备就绪", font=("Arial", 16))
        self.status_label.pack(pady=5)
        
        # 时间显示
        self.time_label = ctk.CTkLabel(status_frame, text=self.format_time(self.remaining_work_time), font=("Arial", 36, "bold"))
        self.time_label.pack(pady=10)
        
        # 进度条
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # 控制按钮框架
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # 开始/暂停按钮
        self.start_button = ctk.CTkButton(control_frame, text="开始", command=self.toggle_timer)
        self.start_button.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        # 重置按钮
        self.reset_button = ctk.CTkButton(control_frame, text="重置", command=self.reset_timer)
        self.reset_button.pack(side="right", padx=5, pady=5, expand=True, fill="x")
        
        # 设置框架
        settings_frame = ctk.CTkFrame(self.main_frame)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # 工作时间设置
        work_frame = ctk.CTkFrame(settings_frame)
        work_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(work_frame, text="工作时间 (分钟):", anchor="w").pack(side="left", padx=5)
        
        self.work_time_var = tk.StringVar(value=str(self.config["work_time"]))
        work_time_entry = ctk.CTkEntry(work_frame, width=50, textvariable=self.work_time_var)
        work_time_entry.pack(side="right", padx=5)
        
        # 休息时间设置
        break_frame = ctk.CTkFrame(settings_frame)
        break_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(break_frame, text="休息时间 (分钟):", anchor="w").pack(side="left", padx=5)
        
        self.break_time_var = tk.StringVar(value=str(self.config["break_time"]))
        break_time_entry = ctk.CTkEntry(break_frame, width=50, textvariable=self.break_time_var)
        break_time_entry.pack(side="right", padx=5)
        
        # 声音开关
        sound_frame = ctk.CTkFrame(settings_frame)
        sound_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(sound_frame, text="启用声音:", anchor="w").pack(side="left", padx=5)
        
        self.sound_var = tk.BooleanVar(value=self.config["sound_enabled"])
        sound_switch = ctk.CTkSwitch(sound_frame, text="", variable=self.sound_var, onvalue=True, offvalue=False)
        sound_switch.pack(side="right", padx=5)
        
        # 自动开始开关
        auto_start_frame = ctk.CTkFrame(settings_frame)
        auto_start_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(auto_start_frame, text="自动开始:", anchor="w").pack(side="left", padx=5)
        
        self.auto_start_var = tk.BooleanVar(value=self.config["auto_start"])
        auto_start_switch = ctk.CTkSwitch(auto_start_frame, text="", variable=self.auto_start_var, onvalue=True, offvalue=False)
        auto_start_switch.pack(side="right", padx=5)
        
        # 最小化到托盘开关
        tray_frame = ctk.CTkFrame(settings_frame)
        tray_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(tray_frame, text="最小化到托盘:", anchor="w").pack(side="left", padx=5)
        
        self.tray_var = tk.BooleanVar(value=self.config["minimize_to_tray"])
        tray_switch = ctk.CTkSwitch(tray_frame, text="", variable=self.tray_var, onvalue=True, offvalue=False)
        tray_switch.pack(side="right", padx=5)
        
        # 保存设置按钮
        save_button = ctk.CTkButton(settings_frame, text="保存设置", command=self.save_settings)
        save_button.pack(pady=10)
        
    
    def toggle_timer(self):
        """开始或暂停计时器"""
        if self.timer_running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """开始计时器"""
        self.timer_running = True
        self.start_button.configure(text="暂停")
        self.status_label.configure(text="工作中..." if not self.is_break_time else "休息中...")
        
        # 启动工作计时器或休息计时器
        if not self.is_break_time:
            self.work_countdown()
        else:
            self.break_countdown()
    
    def pause_timer(self):
        """暂停计时器"""
        self.timer_running = False
        self.start_button.configure(text="开始")
        self.status_label.configure(text="已暂停")
        
        # 取消计时器
        if self.work_timer:
            self.root.after_cancel(self.work_timer)
            self.work_timer = None
        if self.break_timer:
            self.root.after_cancel(self.break_timer)
            self.break_timer = None
    
    def reset_timer(self):
        """重置计时器"""
        self.pause_timer()
        self.is_break_time = False
        self.remaining_work_time = self.config["work_time"] * 60
        self.remaining_break_time = self.config["break_time"] * 60
        self.time_label.configure(text=self.format_time(self.remaining_work_time))
        self.progress_bar.set(0)
        self.status_label.configure(text="准备就绪")
        self.start_button.configure(text="开始")
        
        # 关闭动画窗口如果存在
        if self.animation_window and self.animation_window.winfo_exists():
            self.animation_window.destroy()
            self.animation_window = None
    
    def work_countdown(self):
        """工作时间倒计时"""
        if not self.timer_running:
            return
            
        if self.remaining_work_time <= 0:
            self.start_break()
            return
            
        self.remaining_work_time -= 1
        self.time_label.configure(text=self.format_time(self.remaining_work_time))
        
        # 更新进度条
        progress = 1 - (self.remaining_work_time / (self.config["work_time"] * 60))
        self.progress_bar.set(progress)
        
        # 继续倒计时
        self.work_timer = self.root.after(1000, self.work_countdown)
    
    def break_countdown(self):
        """休息时间倒计时"""
        if not self.timer_running:
            return
            
        if self.remaining_break_time <= 0:
            self.end_break()
            return
            
        self.remaining_break_time -= 1
        self.time_label.configure(text=self.format_time(self.remaining_break_time))
        
        # 更新进度条
        progress = 1 - (self.remaining_break_time / (self.config["break_time"] * 60))
        self.progress_bar.set(progress)
        
        # 继续倒计时
        self.break_timer = self.root.after(1000, self.break_countdown)
    
    def start_break(self):
        """开始休息"""
        self.is_break_time = True
        self.remaining_break_time = self.config["break_time"] * 60
        self.status_label.configure(text="休息时间！")
        self.time_label.configure(text=self.format_time(self.remaining_break_time))
        self.progress_bar.set(0)
        
        # 播放声音
        if self.config["sound_enabled"] and os.path.exists(self.config["sound_file"]):
            pygame.mixer.music.load(self.config["sound_file"])
            pygame.mixer.music.play()
        
        # 显示系统通知
        if self.config["show_notifications"]:
            notification.notify(
                title="休息提醒",
                message=f"工作时间结束！休息 {self.config['break_time']} 分钟",
                app_name="休息提醒",
                timeout=2
            )
        
        # 显示动画窗口
        self.show_animation_window()
        
        # 开始休息倒计时
        self.break_countdown()
    
    def end_break(self):
        """结束休息"""
        self.is_break_time = False
        self.remaining_work_time = self.config["work_time"] * 60
        self.status_label.configure(text="准备开始工作")
        self.time_label.configure(text=self.format_time(self.remaining_work_time))
        self.progress_bar.set(0)
        self.timer_running = False
        self.start_button.configure(text="开始")
        
        # 关闭动画窗口如果存在
        if self.animation_window and self.animation_window.winfo_exists():
            self.animation_window.destroy()
            self.animation_window = None
        
        # 播放声音
        if self.config["sound_enabled"] and os.path.exists(self.config["sound_file"]):
            pygame.mixer.music.stop()
        
        # 显示系统通知
        if self.config["show_notifications"]:
            notification.notify(
                title="休息提醒",
                message=f"休息时间结束！请点击开始按钮继续工作",
                app_name="休息提醒",
                timeout=2
            )
        
        # 不再自动开始工作倒计时
        # self.work_countdown()
    
    def show_animation_window(self):
        """显示动画窗口"""
        # 创建新窗口
        self.animation_window = tk.Toplevel(self.root)
        self.animation_window.title("休息时间！")
        self.animation_window.attributes('-topmost', True)  # 窗口始终置顶
        
        # 获取屏幕宽度和高度
        screen_width = self.animation_window.winfo_screenwidth()
        screen_height = self.animation_window.winfo_screenheight()
        
        # 设置窗口大小为屏幕的80%
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 计算位置使窗口居中
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.animation_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 动画帧
        self.animation_frames = []
        animation_path = self.config.get("animation_folder", "animations")
        
        # 检查动画路径是否存在
        if os.path.exists(animation_path):
            animation_files = [f for f in os.listdir(animation_path) if f.endswith(('.gif', '.png', '.jpg', '.jpeg'))]
            if len(animation_files) > 0:
                # 如果有GIF动画，使用第一个GIF
                gif_files = [f for f in animation_files if f.endswith('.gif')]
                if gif_files:
                    self.play_gif_animation(os.path.join(animation_path, gif_files[0]))
                else:
                    # 否则使用静态图片
                    img_path = os.path.join(animation_path, animation_files[0])
                    self.show_static_image(img_path)
            else:
                # 如果没有找到图片，显示默认文本
                self.show_default_animation()
        else:
            # 如果动画文件夹不存在，显示默认文本
            self.show_default_animation()
        
        # 添加结束休息按钮
        end_button = ctk.CTkButton(self.animation_window, text="结束休息", command=self.end_break)
        end_button.pack(pady=20)
    
    def play_gif_animation(self, gif_path):
        """播放GIF动画"""
        try:
            # 加载GIF
            gif = Image.open(gif_path)
            frames = []
            
            for frame in ImageSequence.Iterator(gif):
                frame = frame.copy()
                frames.append(ImageTk.PhotoImage(frame))
            
            # 创建标签来显示GIF
            gif_label = tk.Label(self.animation_window)
            gif_label.pack(expand=True, fill="both")
            
            def update_frame(idx):
                frame = frames[idx]
                idx = (idx + 1) % len(frames)
                gif_label.configure(image=frame)
                self.animation_window.after(self.config.get("animation_speed", 100), update_frame, idx)
            
            update_frame(0)
        except Exception as e:
            print(f"加载GIF动画出错: {e}")
            self.show_default_animation()
    
    def show_static_image(self, img_path):
        """显示静态图片"""
        try:
            img = Image.open(img_path)
            photo = ImageTk.PhotoImage(img)
            
            img_label = tk.Label(self.animation_window, image=photo)
            img_label.image = photo  # 保持引用
            img_label.pack(expand=True, fill="both")
        except Exception as e:
            print(f"加载图片出错: {e}")
            self.show_default_animation()
    
    def show_default_animation(self):
        """显示默认动画（文本）"""
        message_label = ctk.CTkLabel(
            self.animation_window, 
            text="休息时间！\n\n请起身活动，放松眼睛\n\n剩余时间会在主窗口显示", 
            font=("Arial", 24, "bold")
        )
        message_label.pack(expand=True)
    
    def format_time(self, seconds):
        """格式化时间为分:秒的形式"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 确保所有必要的键都存在
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
            except:
                return DEFAULT_CONFIG.copy()
        else:
            return DEFAULT_CONFIG.copy()
    
    def save_config(self, config):
        """保存配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            return True
        except:
            return False
    
    def save_settings(self):
        """保存设置"""
        try:
            # 更新配置
            self.config["work_time"] = int(self.work_time_var.get())
            self.config["break_time"] = int(self.break_time_var.get())
            self.config["sound_enabled"] = self.sound_var.get()
            self.config["auto_start"] = self.auto_start_var.get()
            self.config["minimize_to_tray"] = self.tray_var.get()
            
            # 保存配置
            if self.save_config(self.config):
                messagebox.showinfo("成功", "设置已保存")
                
                # 重置计时器以应用新设置
                self.reset_timer()
            else:
                messagebox.showerror("错误", "保存设置失败")
        except Exception as e:
            messagebox.showerror("错误", f"保存设置时出错: {str(e)}")
    
    def show_window(self):
        """显示主窗口"""
        self.root.deiconify()
        self.root.lift()
    
    def hide_window(self):
        """隐藏主窗口"""
        self.root.withdraw()
    
    def on_close(self):
        """窗口关闭事件处理"""
        if self.config["minimize_to_tray"]:
            self.hide_window()
        else:
            self.quit_app()
    
    def quit_app(self):
        """退出应用"""
        # 停止计时器
        self.pause_timer()
        
        # 移除托盘图标
        self.tray_icon.stop()
        
        # 销毁根窗口
        self.root.destroy()
        
        # 退出程序
        sys.exit()

def setup_folders():
    """设置必要的文件夹"""
    folders = ["animations", "sounds", "images"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

def main():
    """主函数"""
    # 设置必要的文件夹
    setup_folders()
    
    # 创建根窗口
    root = ctk.CTk()
    
    # 创建应用实例
    app = BreakReminderApp(root)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main() 