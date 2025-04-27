import os
import numpy as np
import wave
import struct

def create_sample_sound():
    """创建一个简单的提示音效"""
    # 确保sounds文件夹存在
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    
    # 音频参数
    sample_rate = 44100  # 采样率 (Hz)
    duration = 1.0       # 音频长度 (秒)
    
    # 创建音频数据
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    
    # 生成一个简单的音调效果（上升的"叮"声）
    freq_start = 500.0   # 起始频率 (Hz)
    freq_end = 1500.0    # 结束频率 (Hz)
    
    # 线性增加频率
    freq = freq_start + (freq_end - freq_start) * t / duration
    
    # 生成正弦波
    sine_wave = np.sin(2 * np.pi * freq * t)
    
    # 添加衰减效果
    envelope = np.exp(-4 * t / duration)
    audio_data = sine_wave * envelope
    
    # 标准化音量
    audio_data = audio_data / np.max(np.abs(audio_data))
    
    # 转换为WAV格式
    save_path = "sounds/notification.wav"
    with wave.open(save_path, 'w') as wav_file:
        # 设置参数
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # 写入音频数据
        for sample in audio_data:
            wav_file.writeframes(struct.pack('h', int(sample * 32767.0)))
    
    print(f"创建示例音效: {save_path}")

if __name__ == "__main__":
    create_sample_sound() 