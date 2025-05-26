# BreakReminder - 休息提醒工具

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



https://zhuanlan.zhihu.com/p/14262381962

pyinstaller 打包
pyinstaller --onefile --windowed main.py --icon=assets/images/icon.ico --add-data "config.json;."  --hidden-import=customtkinter --hidden-import=PIL --hidden-import=PIL._tkinter_finder --hidden-import=pygame --hidden-import=pystray --hidden-import=plyer --hidden-import=cv2 --collect-all=customtkinter --collect-all=PIL --collect-all=PIL._tkinter_finder --collect-all=pygame --collect-all=pystray --collect-all=plyer --collect-all=cv2
 