import os
import sys
import subprocess
import platform

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 9):
        print("错误: 需要Python 3.9或更高版本")
        return False
    return True

def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    
    # 读取requirements.txt
    if os.path.exists("requirements.txt"):
        subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    else:
        print("错误: 找不到requirements.txt文件")
        return False

def create_resources():
    """创建资源文件"""
    print("正在创建资源文件...")
    
    # 创建示例动画
    if os.path.exists("create_sample_animation.py"):
        subprocess.call([sys.executable, "create_sample_animation.py"])
    
    # 创建示例音效
    if os.path.exists("create_sample_sound.py"):
        subprocess.call([sys.executable, "create_sample_sound.py"])
    
    return True

def setup_autostart():
    """设置开机自启动"""
    system = platform.system()
    
    if system == "Windows":
        if os.path.exists("setup_autostart.bat"):
            print("正在设置开机自启动...")
            subprocess.call(["cmd.exe", "/c", "setup_autostart.bat"])
            return True
    elif system in ["Darwin", "Linux"]:
        if os.path.exists("setup_autostart.sh"):
            print("正在设置开机自启动...")
            os.chmod("setup_autostart.sh", 0o755)
            subprocess.call(["./setup_autostart.sh"])
            return True
    
    print("无法设置开机自启动，找不到相关脚本")
    return False

def main():
    """主函数"""
    print("===== BreakReminder 安装程序 =====")
    
    # 检查Python版本
    if not check_python_version():
        input("按Enter键退出...")
        return
    
    # 安装依赖包
    if not install_dependencies():
        input("按Enter键退出...")
        return
    
    # 创建资源文件
    create_resources()
    
    # 询问是否构建可执行文件
    build_choice = input("是否构建可执行文件? (y/n): ").strip().lower()
    if build_choice == 'y':
        if os.path.exists("build.py"):
            print("正在构建可执行文件...")
            subprocess.call([sys.executable, "build.py"])
        else:
            print("错误: 找不到build.py文件")
    
    # 询问是否设置开机自启动
    autostart_choice = input("是否设置开机自启动? (y/n): ").strip().lower()
    if autostart_choice == 'y':
        setup_autostart()
    
    print("\n===== 安装完成 =====")
    print("您可以通过运行break_reminder.py启动程序")
    if build_choice == 'y':
        print("或者运行dist/BreakReminder/BreakReminder.exe")
    
    input("按Enter键退出...")

if __name__ == "__main__":
    main() 