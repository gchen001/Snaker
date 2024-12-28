import PyInstaller.__main__
import os
import shutil

def build_exe():
    """打包游戏为exe文件"""
    
    # 确保dist目录为空
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # PyInstaller参数
    args = [
        'Snaker.py',                     # 主程序文件
        '--name=贪吃蛇',                  # exe名称
        '--icon=snake.ico',              # 图标
        '--noconsole',                   # 不显示控制台
        '--add-data=config.json;.',      # 添加配置文件
        '--add-data=resources;resources', # 添加资源文件夹
        '--add-data=sounds;sounds',      # 添加音效文件夹
        '--onefile',                     # 打包为单个文件
        '--clean',                       # 清理临时文件
        '--windowed',                    # Windows下运行
    ]
    
    # 运行打包
    PyInstaller.__main__.run(args)
    
    print("打包完成！exe文件在 dist 目录中")

if __name__ == '__main__':
    build_exe() 