import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_sample_animation():
    """创建一个简单的休息提醒动画GIF"""
    # 确保animations文件夹存在
    if not os.path.exists("animations"):
        os.makedirs("animations")
    
    # 动画参数
    width, height = 500, 300
    frames = 20
    background_color = (50, 100, 255)
    text_color = (255, 255, 255)
    
    # 创建帧
    images = []
    for i in range(frames):
        # 创建图像
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # 动态大小
        size = 20 + int(10 * np.sin(2 * np.pi * i / frames))
        
        # 尝试加载内置字体
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            # 如果找不到指定字体，使用默认字体
            font = ImageFont.load_default()
        
        # 绘制文本
        messages = [
            "该休息了!",
            "请起身活动一下!",
            "放松眼睛，看看远处!",
            "活动一下手腕和颈部!",
            "喝口水，放松一下!"
        ]
        
        # 在不同位置绘制文本
        for j, msg in enumerate(messages):
            # 计算文本位置（中心对齐）
            y_position = height // 2 - len(messages) * 30 // 2 + j * 40
            # 添加一些动态效果
            x_offset = int(10 * np.sin(2 * np.pi * (i / frames + j / len(messages))))
            x_position = width // 2 + x_offset - 100  # 估计文本宽度
            
            # 绘制文本
            draw.text((x_position, y_position), msg, fill=text_color, font=font)
        
        # 应用模糊效果
        img = img.filter(ImageFilter.GaussianBlur(radius=1.0 * abs(np.sin(i / frames * np.pi))))
        
        # 添加到动画帧
        images.append(img)
    
    # 保存为GIF
    images[0].save(
        "animations/rest_reminder.gif",
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=100,  # 每帧持续100毫秒
        loop=0  # 无限循环
    )
    
    print("创建示例动画GIF: animations/rest_reminder.gif")

if __name__ == "__main__":
    create_sample_animation() 