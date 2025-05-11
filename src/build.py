import os
import shutil
import subprocess
import sys
import platform

def clean_build_folders():
    """清理构建文件夹"""
    folders_to_clean = ['build', 'dist']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            print(f"清理 {folder} 文件夹...")
            shutil.rmtree(folder)

def copy_resources():
    """复制资源文件到打包目录"""
    # 确保资源文件夹存在
    folders = ["animations", "sounds", "images"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        # 如果dist文件夹中没有该资源文件夹，则创建
        dist_folder = os.path.join("dist", "BreakReminder", folder)
        if not os.path.exists(dist_folder):
            os.makedirs(dist_folder)
        
        # 复制文件
        if os.path.exists(folder):
            for file in os.listdir(folder):
                src_file = os.path.join(folder, file)
                dst_file = os.path.join(dist_folder, file)
                if os.path.isfile(src_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"复制 {src_file} 到 {dst_file}")

def create_default_resources():
    """创建默认资源文件"""
    # 创建默认图标
    if not os.path.exists("images"):
        os.makedirs("images")
    
    if not os.path.exists("images/icon.png"):
        # 使用PIL创建一个简单的图标
        try:
            from PIL import Image, ImageDraw
            
            # 创建一个蓝色背景的图标
            img = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(img)
            
            # 画一个简单的闹钟形状
            draw.ellipse((10, 10, 54, 54), outline='white', width=2)
            draw.line((32, 32, 32, 15), fill='white', width=2)
            draw.line((32, 32, 45, 32), fill='white', width=2)
            
            # 保存
            img.save("images/icon.png")
            print("创建默认图标")
        except:
            print("无法创建默认图标，请手动添加图标到 images/icon.png")
    
    # 创建默认声音
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    
    # 注意：创建默认声音文件需要特定的库，这里仅创建一个空文件
    if not os.path.exists("sounds/notification.wav"):
        try:
            # 尝试使用pygame创建一个简单的声音文件
            import pygame
            import numpy as np
            
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            arr = np.sin(2 * np.pi * np.arange(44100) * 440 / 44100).astype(np.float32)
            sound = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
            pygame.sndarray.save(sound, "sounds/notification.wav")
            print("创建默认声音文件")
        except:
            # 如果无法创建，复制一个空文件
            with open("sounds/notification.wav", "wb") as f:
                f.write(b"")
            print("创建空声音文件，请手动添加声音到 sounds/notification.wav")

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 确定系统类型
    system = platform.system()
    
    # PyInstaller命令
    cmd = [
        "pyinstaller",
        "--name=BreakReminder",
        "--onedir",
        "--windowed",
        "--clean",
    ]
    
    # 添加图标（如果存在）
    if os.path.exists("images/icon.ico"):
        cmd.append(f"--icon=images/icon.ico")
    elif os.path.exists("images/icon.png"):
        # 转换png为ico (在Windows下)
        if system == "Windows":
            try:
                from PIL import Image
                img = Image.open("images/icon.png")
                ico_path = "images/icon.ico"
                img.save(ico_path)
                cmd.append(f"--icon={ico_path}")
                print("PNG图标已转换为ICO格式")
            except:
                print("无法转换PNG图标到ICO格式")
    
    # 添加主脚本
    cmd.append("break_reminder.py")
    
    # 执行PyInstaller
    subprocess.call(cmd)
    
    # 复制资源文件
    copy_resources()
    
    print("构建完成！")

def create_autostart_setup():
    """创建自启动设置脚本"""
    system = platform.system()
    
    if system == "Windows":
        with open("setup_autostart.bat", "w") as f:
            f.write("""@echo off
echo 设置 BreakReminder 开机自启动...

:: 获取当前目录
set "CURRENT_DIR=%~dp0"
set "EXE_PATH=%CURRENT_DIR%dist\\BreakReminder\\BreakReminder.exe"

:: 创建开机启动快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\\CreateShortcut.vbs"
echo sLinkFile = oWS.SpecialFolders("Startup") ^& "\\BreakReminder.lnk" >> "%TEMP%\\CreateShortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.TargetPath = "%EXE_PATH%" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.WorkingDirectory = "%CURRENT_DIR%dist\\BreakReminder" >> "%TEMP%\\CreateShortcut.vbs"
echo oLink.Save >> "%TEMP%\\CreateShortcut.vbs"
cscript //nologo "%TEMP%\\CreateShortcut.vbs"
del "%TEMP%\\CreateShortcut.vbs"

echo 完成！BreakReminder 将在下次启动系统时自动运行。
pause
""")
        print("创建Windows自启动设置脚本: setup_autostart.bat")
    
    elif system == "Darwin":  # macOS
        with open("setup_autostart.sh", "w") as f:
            f.write("""#!/bin/bash
echo "设置 BreakReminder 开机自启动..."

# 获取当前目录
CURRENT_DIR=$(pwd)
APP_PATH="$CURRENT_DIR/dist/BreakReminder/BreakReminder"

# 创建启动项配置文件
PLIST_PATH="$HOME/Library/LaunchAgents/com.user.breakreminder.plist"

cat > "$PLIST_PATH" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.breakreminder</string>
    <key>ProgramArguments</key>
    <array>
        <string>$APP_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOL

# 加载启动项
launchctl load "$PLIST_PATH"

echo "完成！BreakReminder 将在下次登录时自动运行。"
""")
        # 添加可执行权限
        os.chmod("setup_autostart.sh", 0o755)
        print("创建macOS自启动设置脚本: setup_autostart.sh")
    
    elif system == "Linux":
        with open("setup_autostart.sh", "w") as f:
            f.write("""#!/bin/bash
echo "设置 BreakReminder 开机自启动..."

# 获取当前目录
CURRENT_DIR=$(pwd)
APP_PATH="$CURRENT_DIR/dist/BreakReminder/BreakReminder"

# 创建桌面条目
DESKTOP_FILE="$HOME/.config/autostart/breakreminder.desktop"

mkdir -p "$HOME/.config/autostart"

cat > "$DESKTOP_FILE" << EOL
[Desktop Entry]
Type=Application
Name=BreakReminder
Comment=休息提醒工具
Exec=$APP_PATH
Terminal=false
Categories=Utility;
EOL

echo "完成！BreakReminder 将在下次登录时自动运行。"
""")
        # 添加可执行权限
        os.chmod("setup_autostart.sh", 0o755)
        print("创建Linux自启动设置脚本: setup_autostart.sh")

def create_readme():
    """创建README文件"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write("""# BreakReminder - 休息提醒工具

一个简单实用的 Windows 桌面工具，可以在工作一段时间后弹出精美的动画提醒您休息一下。

## 功能特点

- ✅ 可自定义工作和休息时间长度
- ✅ 支持炫酷动画和音效提醒
- ✅ 系统托盘图标，最小化到系统托盘
- ✅ 支持开机自启动
- ✅ 简洁美观的用户界面

## 安装使用

1. 下载最新版本的 BreakReminder.zip
2. 解压到任意位置
3. 运行 BreakReminder.exe

## 设置开机自启动

运行 `setup_autostart.bat` 脚本来设置开机自启动。

## 自定义动画和声音

- 将您喜欢的动画GIF或图片放入 `animations` 文件夹
- 将您喜欢的声音文件放入 `sounds` 文件夹并命名为 `notification.wav`

## 注意事项

- 本程序需要 Windows 7 或更高版本
- 首次运行时可能会被防火墙拦截，请允许访问

## 常见问题

**Q: 为什么没有显示动画？**
A: 请确保 `animations` 文件夹中有有效的图片或GIF文件。

**Q: 如何彻底退出程序？**
A: 右键点击系统托盘图标，选择"退出"。

## 开源许可

本项目基于 MIT 许可证开源。
""")
    print("创建README.md文件")

def main():
    """主函数"""
    # 清理之前的构建
    clean_build_folders()
    
    # 创建默认资源
    create_default_resources()
    
    # 构建可执行文件
    build_executable()
    
    # 创建自启动设置脚本
    create_autostart_setup()
    
    # 创建README文件
    create_readme()
    
    print("\n构建过程完成！")
    print("----------------------------")
    print("您可以在 dist/BreakReminder 文件夹中找到可执行文件。")
    print("运行 setup_autostart.bat（Windows）或 setup_autostart.sh（macOS/Linux）设置开机自启动。")

if __name__ == "__main__":
    main() 