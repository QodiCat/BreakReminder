import customtkinter as ctk
from src.break_reminder import BreakReminderApp, setup_folders

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