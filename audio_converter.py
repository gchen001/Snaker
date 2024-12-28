"""
音频格式转换工具

功能：
- 将MP3文件转换为WAV格式
- 支持单个文件转换
- 支持整个目录批量转换
- 支持拖拽文件转换
"""

import os
from pydub import AudioSegment
import sys
import json

def load_config():
    """加载配置文件"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return None

def convert_to_wav(input_path, output_path=None):
    """
    将音频文件转换为WAV格式
    
    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径（可选）
    """
    try:
        # 如果没有指定输出路径，则在原目录生成同名wav文件
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.wav'
        
        # 加载音频文件
        audio = AudioSegment.from_file(input_path)
        
        # 转换并保存为WAV格式
        audio.export(output_path, format='wav')
        print(f"转换��功: {input_path} -> {output_path}")
        return True
    except Exception as e:
        print(f"转换失败: {input_path}")
        print(f"错误信息: {str(e)}")
        return False

def convert_directory(input_dir, output_dir=None):
    """
    转换目录中的所有音频文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录（可选）
    """
    if output_dir is None:
        output_dir = input_dir
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    success_count = 0
    fail_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.mp3', '.m4a', '.ogg', '.flac')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + '.wav')
            
            if convert_to_wav(input_path, output_path):
                success_count += 1
            else:
                fail_count += 1
    
    print(f"\n转换完成:")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")

def convert_for_game():
    """转换游戏所需的音频文件"""
    config = load_config()
    if not config:
        return
    
    sound_dir = config['audio']['directory']
    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)
    
    # 获取所有需要的音效文件名
    sound_files = config['audio']['sounds']
    
    # 检查每个音效文件
    for sound_name, wav_filename in sound_files.items():
        # 查找对应的mp3文件
        mp3_filename = os.path.splitext(wav_filename)[0] + '.mp3'
        mp3_path = os.path.join(sound_dir, mp3_filename)
        wav_path = os.path.join(sound_dir, wav_filename)
        
        # 如果存在mp3文件但不存在wav文件，进行转换
        if os.path.exists(mp3_path) and not os.path.exists(wav_path):
            print(f"正在转换: {mp3_filename}")
            convert_to_wav(mp3_path, wav_path)

def main():
    """主函数"""
    # 如果有命令行参数（拖拽文件）
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            if os.path.isfile(path):
                convert_to_wav(path)
            elif os.path.isdir(path):
                convert_directory(path)
    else:
        # 交互式模式
        print("音频格式转换工具")
        print("1. 转换单个文件")
        print("2. 转换整个目录")
        print("3. 转换游戏音效文件")
        print("4. 退出")
        
        choice = input("请选择操作 (1-4): ")
        
        if choice == '1':
            path = input("请输入文件路径: ")
            if os.path.isfile(path):
                convert_to_wav(path)
            else:
                print("文件不存在!")
        
        elif choice == '2':
            path = input("请输入目录路径: ")
            if os.path.isdir(path):
                convert_directory(path)
            else:
                print("目录不存在!")
        
        elif choice == '3':
            convert_for_game()
        
        elif choice == '4':
            return
        
        else:
            print("无效的选择!")

if __name__ == '__main__':
    main() 