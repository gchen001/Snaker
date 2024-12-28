from PIL import Image, ImageDraw

def create_icon():
    """创建蛇形图标"""
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制蛇身（渐变绿色）
    points = [
        (128, 50),   # 头部
        (100, 100),
        (150, 150),
        (80, 200),
        (128, 220)   # 尾部
    ]
    
    # 绘制平滑的曲线
    for i in range(len(points)-1):
        draw.line(
            [points[i], points[i+1]], 
            fill=(0, 200, 0, 255), 
            width=30
        )
    
    # 绘制蛇头
    draw.ellipse(
        [108, 30, 148, 70], 
        fill=(0, 255, 0, 255)
    )
    
    # 绘制眼睛
    draw.ellipse([120, 40, 125, 45], fill=(255, 255, 255, 255))
    draw.ellipse([135, 40, 140, 45], fill=(255, 255, 255, 255))
    
    # 保存为ico文件
    img.save('snake.ico', format='ICO', sizes=[(256, 256)])

if __name__ == '__main__':
    create_icon() 