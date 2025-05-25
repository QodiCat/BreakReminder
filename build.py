import os
import shutil
import subprocess
import sys
import json

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    if os.path.exists('BreakReminder.spec'):
        os.remove('BreakReminder.spec')

def create_debug_config():
    """创建调试配置文件"""
    debug_config = {
        "debug": True,
        "log_file": "debug.log",
        "config_path": "config.json"
    }
    with open("debug_config.json", "w", encoding="utf-8") as f:
        json.dump(debug_config, f, indent=4)

def build_executable():
    """构建可执行文件"""
    # 确保在项目根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 清理旧的构建文件
    clean_build_dirs()
    
    # 创建调试配置文件
    create_debug_config()
    
    # 构建命令
    build_cmd = [
        'pyinstaller',
        '--name=BreakReminder',
        '--windowed',  # 不显示控制台窗口
        '--icon=assets/images/icon.ico',  # 应用图标
        '--add-data=assets;assets',  # 添加资源文件
        '--add-data=config.json;.',  # 添加配置文件
        '--add-data=debug_config.json;.',  # 添加调试配置文件
        '--noconfirm',  # 不询问确认
        'main.py'  # 主程序入口
    ]
    
    # 执行构建
    try:
        subprocess.run(build_cmd, check=True)
        print("构建成功！可执行文件位于 dist/BreakReminder 目录中")
    except subprocess.CalledProcessError as e:
        print(f"构建失败：{e}")
        sys.exit(1)

if __name__ == '__main__':
    build_executable()
