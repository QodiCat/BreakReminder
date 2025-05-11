import os
import sys
import time
import json
import threading
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image, ImageTk, ImageSequence
import pygame
import pystray
from pystray import MenuItem as item
from plyer import notification
import cv2
from src.focus_recorder import FocusRecorder

# 初始化pygame用于播放提醒音效
pygame.mixer.init()

# 默认配置
DEFAULT_CONFIG = {
    "work_time": 40,  # work time (minutes)
    "break_time": 8,  # break time (minutes)
    "animation_folder": "animations",  # animation folder
    "animation_speed": 100,  # animation speed (milliseconds)
    "sound_enabled": True,  # whether to enable sound
    "sound_file": "sounds/test.mp3",  # sound file path
    "auto_start": True,  # whether to auto start
    "minimize_to_tray": True,  # whether to minimize to tray
    "show_notifications": True,  # whether to show notifications
    "media_type": "gif",  # 媒体类型: gif, video, music, none
    "video_file": "videos/sample.mp4",  # 视频文件路径
    "music_file": "sounds/test.mp3"  # 音乐文件路径
}

class BreakReminderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("休息提醒")
        self.root.geometry("450x700")  # 增加窗口高度
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
        
        # 初始化专注记录器
        self.focus_recorder = FocusRecorder()
        self.focus_start_time = None
        self.current_focus_goal = None
        
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
        
        # 创建一个标签页控件
        main_tabview = ctk.CTkTabview(self.main_frame)
        main_tabview.pack(fill="both", expand=True, pady=5)
        
        # 添加主页面和历史记录两个标签页
        main_tab = main_tabview.add("主页面")
        history_tab = main_tabview.add("历史记录")
        
        # === 主页面标签页 ===
        # 专注目标输入框
        focus_frame = ctk.CTkFrame(main_tab)
        focus_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(focus_frame, text="专注目标:", anchor="w").pack(side="left", padx=5)
        self.focus_goal_entry = ctk.CTkEntry(focus_frame, width=200)
        self.focus_goal_entry.pack(side="right", padx=5, fill="x", expand=True)
        
        # 状态框架
        status_frame = ctk.CTkFrame(main_tab)
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
        control_frame = ctk.CTkFrame(main_tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # 开始/暂停按钮
        self.start_button = ctk.CTkButton(control_frame, text="开始", command=self.toggle_timer)
        self.start_button.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        
        # 重置按钮
        self.reset_button = ctk.CTkButton(control_frame, text="重置", command=self.reset_timer)
        self.reset_button.pack(side="right", padx=5, pady=5, expand=True, fill="x")
        
        # 设置框架
        settings_frame = ctk.CTkFrame(main_tab)
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # 创建一个标签页控件
        tabview = ctk.CTkTabview(settings_frame)
        tabview.pack(fill="x", pady=5)
        
        # 添加基本设置和媒体设置两个标签页
        basic_tab = tabview.add("基本设置")
        media_tab = tabview.add("媒体设置")
        
        # === 基本设置标签页 ===
        # 工作时间设置
        work_frame = ctk.CTkFrame(basic_tab)
        work_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(work_frame, text="工作时间 (分钟):", anchor="w").pack(side="left", padx=5)
        
        self.work_time_var = tk.StringVar(value=str(self.config["work_time"]))
        work_time_entry = ctk.CTkEntry(work_frame, width=50, textvariable=self.work_time_var)
        work_time_entry.pack(side="right", padx=5)
        
        # 休息时间设置
        break_frame = ctk.CTkFrame(basic_tab)
        break_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(break_frame, text="休息时间 (分钟):", anchor="w").pack(side="left", padx=5)
        
        self.break_time_var = tk.StringVar(value=str(self.config["break_time"]))
        break_time_entry = ctk.CTkEntry(break_frame, width=50, textvariable=self.break_time_var)
        break_time_entry.pack(side="right", padx=5)
        
        # 声音开关
        sound_frame = ctk.CTkFrame(basic_tab)
        sound_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(sound_frame, text="启用声音:", anchor="w").pack(side="left", padx=5)
        
        self.sound_var = tk.BooleanVar(value=self.config["sound_enabled"])
        sound_switch = ctk.CTkSwitch(sound_frame, text="", variable=self.sound_var, onvalue=True, offvalue=False)
        sound_switch.pack(side="right", padx=5)
        
        # 自动开始开关
        auto_start_frame = ctk.CTkFrame(basic_tab)
        auto_start_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(auto_start_frame, text="自动开始:", anchor="w").pack(side="left", padx=5)
        
        self.auto_start_var = tk.BooleanVar(value=self.config["auto_start"])
        auto_start_switch = ctk.CTkSwitch(auto_start_frame, text="", variable=self.auto_start_var, onvalue=True, offvalue=False)
        auto_start_switch.pack(side="right", padx=5)
        
        # 最小化到托盘开关
        tray_frame = ctk.CTkFrame(basic_tab)
        tray_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(tray_frame, text="最小化到托盘:", anchor="w").pack(side="left", padx=5)
        
        self.tray_var = tk.BooleanVar(value=self.config["minimize_to_tray"])
        tray_switch = ctk.CTkSwitch(tray_frame, text="", variable=self.tray_var, onvalue=True, offvalue=False)
        tray_switch.pack(side="right", padx=5)
        
        # === 媒体设置标签页 ===
        # 媒体类型选择
        media_type_frame = ctk.CTkFrame(media_tab)
        media_type_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(media_type_frame, text="休息时媒体类型:", anchor="w").pack(side="left", padx=5)
        
        self.media_type_var = tk.StringVar(value=self.config["media_type"])
        media_types = ["gif", "video", "music", "none"]
        media_combobox = ctk.CTkComboBox(media_type_frame, values=media_types, variable=self.media_type_var, command=self.on_media_type_change)
        media_combobox.pack(side="right", padx=5)
        
        # GIF动画文件夹设置
        self.gif_frame = ctk.CTkFrame(media_tab)
        self.gif_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.gif_frame, text="GIF动画文件夹:", anchor="w").pack(side="left", padx=5)
        
        self.animation_folder_var = tk.StringVar(value=self.config["animation_folder"])
        animation_folder_entry = ctk.CTkEntry(self.gif_frame, textvariable=self.animation_folder_var, width=150)
        animation_folder_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        browse_anim_btn = ctk.CTkButton(self.gif_frame, text="浏览", width=60, command=self.browse_animation_folder)
        browse_anim_btn.pack(side="right", padx=5)
        
        # 视频文件设置
        self.video_frame = ctk.CTkFrame(media_tab)
        self.video_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.video_frame, text="视频文件:", anchor="w").pack(side="left", padx=5)
        
        self.video_file_var = tk.StringVar(value=self.config["video_file"])
        video_file_entry = ctk.CTkEntry(self.video_frame, textvariable=self.video_file_var, width=150)
        video_file_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        browse_video_btn = ctk.CTkButton(self.video_frame, text="浏览", width=60, command=self.browse_video_file)
        browse_video_btn.pack(side="right", padx=5)
        
        # 音乐文件设置
        self.music_frame = ctk.CTkFrame(media_tab)
        self.music_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.music_frame, text="音乐文件:", anchor="w").pack(side="left", padx=5)
        
        self.music_file_var = tk.StringVar(value=self.config["music_file"])
        music_file_entry = ctk.CTkEntry(self.music_frame, textvariable=self.music_file_var, width=150)
        music_file_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        browse_music_btn = ctk.CTkButton(self.music_frame, text="浏览", width=60, command=self.browse_music_file)
        browse_music_btn.pack(side="right", padx=5)
        
        # 保存设置按钮
        save_button = ctk.CTkButton(self.main_frame, text="保存设置", command=self.save_settings)
        save_button.pack(pady=10)
        
        # 根据当前媒体类型显示/隐藏相关设置
        self.on_media_type_change(self.config["media_type"])
        
        # === 历史记录标签页 ===
        # 创建日期选择框架
        date_frame = ctk.CTkFrame(history_tab)
        date_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(date_frame, text="选择日期:", anchor="w").pack(side="left", padx=5)
        self.date_entry = ctk.CTkEntry(date_frame, width=100)
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        refresh_btn = ctk.CTkButton(date_frame, text="刷新", width=60, command=self.refresh_history)
        refresh_btn.pack(side="right", padx=5)
        
        # 创建记录显示区域
        self.history_frame = ctk.CTkScrollableFrame(history_tab)
        self.history_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 初始化显示今天的记录
        self.refresh_history()
    
    def toggle_timer(self):
        """开始或暂停计时器"""
        if self.timer_running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """开始计时器"""
        if not self.timer_running:
            self.timer_running = True
            self.start_button.configure(text="暂停")
            self.status_label.configure(text="工作中...")
            
            # 记录专注开始时间
            self.focus_start_time = datetime.datetime.now()
            self.current_focus_goal = self.focus_goal_entry.get() or "未设置目标"
            
            self.work_countdown()
    
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
        
        # 媒体类型
        media_type = self.config.get("media_type", "gif")
        
        # 仅在非音乐模式下，且启用声音时播放提示音
        if media_type != "music" and self.config["sound_enabled"] and os.path.exists(self.config["sound_file"]):
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
        """结束休息
           结束休息后不要自动开始工作倒计时
        """
        if self.animation_window:
            self.animation_window.destroy()
            self.animation_window = None
        
        # 停止播放音乐
        pygame.mixer.music.stop()
        
        self.is_break_time = False
        self.remaining_work_time = self.config["work_time"] * 60
        self.time_label.configure(text=self.format_time(self.remaining_work_time))
        self.progress_bar.set(0)
        
        
        # 记录专注结束时间
        if self.focus_start_time:
            end_time = datetime.datetime.now()
            duration_minutes = (end_time - self.focus_start_time).total_seconds() / 60
            
            # 添加专注记录
            self.focus_recorder.add_focus_record(
                focus_goal=self.current_focus_goal,
                start_time=self.focus_start_time,
                end_time=end_time,
                duration_minutes=int(duration_minutes)
            )
            
            # 重置专注时间
            self.focus_start_time = None
            self.current_focus_goal = None
        
        
    
    def show_animation_window(self):
        """显示动画窗口"""
        # 创建新窗口
        self.animation_window = tk.Toplevel(self.root)
        self.animation_window.title("休息时间！")
        self.animation_window.attributes('-topmost', True)  # 窗口始终置顶
        
        # 禁止用户关闭窗口
        self.animation_window.protocol("WM_DELETE_WINDOW", self.prevent_animation_close)
        
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
        
        # 根据选择的媒体类型显示不同内容
        media_type = self.config.get("media_type", "gif")
        
        if media_type == "gif":
            # 显示GIF动画
            self.show_gif_animation()
        elif media_type == "video":
            # 播放视频
            self.play_video()
        elif media_type == "music":
            # 播放音乐并显示默认文本
            self.play_music()
            self.show_default_animation()
        else:
            # 显示默认文本
            self.show_default_animation()
        
        # 添加结束休息按钮
        end_button = ctk.CTkButton(self.animation_window, text="结束休息", command=self.end_break)
        end_button.pack(pady=20)
    
    def show_gif_animation(self):
        """显示GIF动画"""
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
    
    def play_video(self):
        """播放视频"""
        video_file = self.config.get("video_file", "")
        
        if not os.path.exists(video_file):
            messagebox.showwarning("警告", f"视频文件不存在: {video_file}")
            self.show_default_animation()
            return
        
        try:
            # 创建视频播放框架
            video_frame = ctk.CTkFrame(self.animation_window)
            video_frame.pack(expand=True, fill="both", padx=20, pady=20)
            
            # 创建播放控制框架
            control_frame = ctk.CTkFrame(self.animation_window)
            control_frame.pack(fill="x", padx=20, pady=5)
            
            # 播放/暂停按钮
            self.is_video_playing = True
            self.play_pause_btn = ctk.CTkButton(control_frame, text="暂停", width=80, command=self.toggle_video)
            self.play_pause_btn.pack(side="left", padx=10)
            
            # 创建用于显示视频的标签
            self.video_label = tk.Label(video_frame, bg="black")
            self.video_label.pack(expand=True, fill="both")
            
            # 使用pygame初始化音频
            pygame.init()
            pygame.mixer.init()
            
            # 加载并播放视频音频
            try:
                pygame.mixer.music.load(video_file)
                pygame.mixer.music.play(-1)  # -1表示循环播放
                self.audio_playing = True
            except Exception as e:
                print(f"加载音频失败: {e}")
                self.audio_playing = False
            
            # 打开视频文件
            self.cap = cv2.VideoCapture(video_file)
            
            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开视频文件")
                self.show_default_animation()
                return
            
            # 获取视频属性
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.delay = int(1000 / self.fps)
            
            # 计算视频宽高比
            self.video_aspect_ratio = self.frame_width / self.frame_height
            
            
            # 开始播放视频
            self.update_video()
            
        except Exception as e:
            messagebox.showerror("错误", f"播放视频时出错: {str(e)}")
            self.show_default_animation()
    
    def update_video(self):
        """更新视频帧"""
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            return
        
        if not self.is_video_playing:
            # 如果暂停，则延迟更新
            self.animation_window.after(100, self.update_video)
            return
        
        ret, frame = self.cap.read()
        
        if ret:
            # 将BGR格式转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 获取窗口当前大小
            video_width = self.video_label.winfo_width()
            video_height = self.video_label.winfo_height()
            
            if video_width > 1 and video_height > 1:
                # 调整帧的大小以适应窗口
                frame_rgb = cv2.resize(frame_rgb, (video_width, video_height))
            
            # 将OpenCV图像转换为PIL图像
            img = Image.fromarray(frame_rgb)
            
            # 将PIL图像转换为Tkinter可以显示的格式
            img_tk = ImageTk.PhotoImage(image=img)
            
            # 更新标签上的图像
            self.video_label.configure(image=img_tk)
            self.video_label.image = img_tk  # 保持引用
            
            # 安排下一帧的更新
            self.animation_window.after(self.delay, self.update_video)
        else:
            # 视频结束，重新开始播放
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.animation_window.after(self.delay, self.update_video)
    
    def toggle_video(self):
        """切换视频播放/暂停状态"""
        self.is_video_playing = not self.is_video_playing
        
        if self.is_video_playing:
            self.play_pause_btn.configure(text="暂停")
        else:
            self.play_pause_btn.configure(text="播放")
    
    def play_music(self):
        """播放音乐"""
        music_file = self.config.get("music_file", "")
        
        if os.path.exists(music_file):
            try:
                # 停止当前播放的音乐
                pygame.mixer.music.stop()
                
                # 加载并播放新音乐文件
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.play(-1)  # -1表示循环播放
            except Exception as e:
                print(f"播放音乐时出错: {e}")
    
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
            
            # 更新媒体设置
            self.config["media_type"] = self.media_type_var.get()
            self.config["animation_folder"] = self.animation_folder_var.get()
            self.config["video_file"] = self.video_file_var.get()
            self.config["music_file"] = self.music_file_var.get()
            
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

    def on_media_type_change(self, media_type):
        """根据选择的媒体类型显示或隐藏相关设置"""
        # 隐藏所有媒体设置框
        self.gif_frame.pack_forget()
        self.video_frame.pack_forget()
        self.music_frame.pack_forget()
        
        # 根据选择的媒体类型显示相应设置
        if media_type == "gif":
            self.gif_frame.pack(fill="x", pady=5)
        elif media_type == "video":
            self.video_frame.pack(fill="x", pady=5)
        elif media_type == "music":
            self.music_frame.pack(fill="x", pady=5)

    def browse_animation_folder(self):
        """浏览并选择动画文件夹"""
        folder = filedialog.askdirectory(initialdir=self.animation_folder_var.get())
        if folder:
            self.animation_folder_var.set(folder)

    def browse_video_file(self):
        """浏览并选择视频文件"""
        filetypes = [("视频文件", "*.mp4 *.avi *.mkv *.mov")]
        file = filedialog.askopenfilename(initialdir=os.path.dirname(self.video_file_var.get()), 
                                           filetypes=filetypes)
        if file:
            self.video_file_var.set(file)

    def browse_music_file(self):
        """浏览并选择音乐文件"""
        filetypes = [("音频文件", "*.mp3 *.wav *.ogg")]
        file = filedialog.askopenfilename(initialdir=os.path.dirname(self.music_file_var.get()), 
                                           filetypes=filetypes)
        if file:
            self.music_file_var.set(file)

    def prevent_animation_close(self):
        """阻止动画窗口关闭"""
        messagebox.showinfo("提示", "休息时间内不能关闭此窗口，请等待休息结束或点击'结束休息'按钮")
        return

    def refresh_history(self):
        """刷新历史记录显示"""
        # 清空现有记录
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        # 获取选择的日期
        date = self.date_entry.get()
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("错误", "日期格式无效，请使用YYYY-MM-DD格式")
            return
        
        # 获取记录
        records = self.focus_recorder.get_records_by_date(date)
        
        if not records:
            ctk.CTkLabel(self.history_frame, text="没有找到记录").pack(pady=10)
            return
        
        # 显示记录
        for record in records:
            record_frame = ctk.CTkFrame(self.history_frame)
            record_frame.pack(fill="x", pady=5, padx=5)
            
            # 专注目标
            ctk.CTkLabel(record_frame, text=f"目标: {record['focus_goal']}", 
                        font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=2)
            
            # 时间信息
            start_time = datetime.datetime.fromisoformat(record['start_time'])
            end_time = datetime.datetime.fromisoformat(record['end_time'])
            
            time_info = f"开始: {start_time.strftime('%H:%M:%S')} - 结束: {end_time.strftime('%H:%M:%S')}"
            ctk.CTkLabel(record_frame, text=time_info).pack(anchor="w", padx=5, pady=2)
            
            # 专注时长
            duration_info = f"专注时长: {record['duration_minutes']} 分钟"
            ctk.CTkLabel(record_frame, text=duration_info).pack(anchor="w", padx=5, pady=2)
            
            # 添加分隔线
            separator = ctk.CTkFrame(record_frame, height=1, fg_color="gray")
            separator.pack(fill="x", padx=5, pady=5)

def setup_folders():
    """设置必要的文件夹"""
    folders = ["assets/animations", "assets/sounds", "assets/images", "assets/videos"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

