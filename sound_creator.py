import pygame
import numpy as np
import os
from scipy.io import wavfile  # 用于保存WAV文件

def create_sine_wave(frequency, duration, volume=0.5, sample_rate=44100):
    """创建正弦波音效"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = np.sin(2 * np.pi * frequency * t)
    # 创建立体声
    stereo = np.vstack((wave, wave)).T
    return (stereo * volume * 32767).astype(np.int16)

def save_sound(array, filename, sample_rate=44100):
    """保存音效为WAV文件"""
    try:
        wavfile.write(filename, sample_rate, array)
    except Exception as e:
        print(f"保存音效失败: {filename}, 错误: {str(e)}")

def create_button_sound():
    """创建按键音效（短促的高音）"""
    duration = 0.1
    wave = create_sine_wave(880, duration, 0.3)  # A5音
    # 添加淡出效果
    fade = np.linspace(1, 0, len(wave))
    return (wave * fade[:, np.newaxis]).astype(np.int16)

def create_eat_sound():
    """创建吃食物音效（上升的音调）"""
    duration = 0.15
    t = np.linspace(0, duration, int(44100 * duration))
    frequency = np.linspace(440, 880, len(t))  # A4到A5
    wave = np.sin(2 * np.pi * frequency * t)
    stereo = np.vstack((wave, wave)).T
    # 添加淡出效果
    fade = np.linspace(1, 0, len(wave))
    return (stereo * fade[:, np.newaxis] * 32767 * 0.3).astype(np.int16)

def create_death_sound():
    """创建死亡音效（下降的音调）"""
    duration = 0.5
    t = np.linspace(0, duration, int(44100 * duration))
    frequency = np.linspace(880, 220, len(t))  # A5到A3
    wave = np.sin(2 * np.pi * frequency * t)
    stereo = np.vstack((wave, wave)).T
    # 添加淡出效果
    fade = np.linspace(1, 0, len(wave))
    return (stereo * fade[:, np.newaxis] * 32767 * 0.4).astype(np.int16)

def create_background_music():
    """创建背景音乐（简单的循环音乐）"""
    duration = 4.0  # 4秒循环
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 创建基础旋律
    melody = np.sin(2 * np.pi * 440 * t)  # A4
    melody += 0.5 * np.sin(2 * np.pi * 550 * t)  # C#5
    melody += 0.3 * np.sin(2 * np.pi * 660 * t)  # E5
    
    # 添加简单的节奏变化
    rhythm = np.sin(2 * np.pi * 2 * t)
    rhythm = np.where(rhythm > 0, 1, 0.5)
    
    wave = melody * rhythm
    stereo = np.vstack((wave, wave)).T
    return (stereo * 32767 * 0.3).astype(np.int16)

def create_all_sounds(config):
    """创建所有游戏音效"""
    print("正在创建音效...")
    
    # 确保音效目录存在
    sound_dir = config.AUDIO['directory']
    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)
    
    try:
        # 创建并保存按键音效
        button_sound = create_button_sound()
        save_sound(button_sound, os.path.join(sound_dir, config.AUDIO['sounds']['button']))
        print("已创建按键音效")
        
        # 创建并保存吃食物音效
        eat_sound = create_eat_sound()
        save_sound(eat_sound, os.path.join(sound_dir, config.AUDIO['sounds']['eat']))
        print("已创建吃食物音效")
        
        # 创建并保存死亡音效
        death_sound = create_death_sound()
        save_sound(death_sound, os.path.join(sound_dir, config.AUDIO['sounds']['death']))
        print("已创建死亡音效")
        
        # # 创建并保存背景音乐
        # background_music = create_background_music()
        # save_sound(background_music, os.path.join(sound_dir, config.AUDIO['sounds']['background']))
        # print("已创建背景音乐")
        
        return True
    except Exception as e:
        print(f"创建音效时出错: {str(e)}")
        return False

if __name__ == '__main__':
    # 测试音效生成
    pygame.init()
    from config import Config  # 假设你有一个config.py文件
    create_all_sounds(Config)
    pygame.quit() 