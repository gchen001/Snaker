import pygame
import os

def create_background(config):
    """创建游戏背景图片"""
    background = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    background.fill((3, 3, 5))  # 接近纯黑的背景
    
    # 添加极暗的网格纹理
    for x in range(0, config.WINDOW_WIDTH, config.GRID_SIZE):
        pygame.draw.line(background, config.GRID_COLOR, (x, 0), (x, config.WINDOW_HEIGHT))
    for y in range(0, config.WINDOW_HEIGHT, config.GRID_SIZE):
        pygame.draw.line(background, config.GRID_COLOR, (0, y), (config.WINDOW_WIDTH, y))
    
    return background

def create_snake_body(config):
    """创建蛇身图片"""
    body = pygame.Surface((config.GRID_SIZE-4, config.GRID_SIZE-4), pygame.SRCALPHA)
    pygame.draw.circle(body, (100, 240, 100), 
                      ((config.GRID_SIZE-4)//2, (config.GRID_SIZE-4)//2), 
                      (config.GRID_SIZE-4)//2-1)
    pygame.draw.circle(body, (140, 255, 140), 
                      ((config.GRID_SIZE-4)//3, (config.GRID_SIZE-4)//3), 3)
    return body

def create_food(config):
    """创建食物图片"""
    food = pygame.Surface((config.GRID_SIZE, config.GRID_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(food, (255, 60, 60), 
                      (config.GRID_SIZE//2, config.GRID_SIZE//2), 
                      config.GRID_SIZE//2-1)
    pygame.draw.ellipse(food, (120, 255, 120), 
                       (config.GRID_SIZE//2-2, 2, 4, 6))
    pygame.draw.circle(food, (255, 255, 255, 200), 
                      (config.GRID_SIZE//3, config.GRID_SIZE//3), 3)
    return food

def create_snake_head(config, direction_name):
    """创建蛇头图片"""
    head = pygame.Surface((config.GRID_SIZE, config.GRID_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(head, (120, 255, 120), 
                      (config.GRID_SIZE//2, config.GRID_SIZE//2), 
                      config.GRID_SIZE//2-1)
    
    eye_positions = {
        "up": [(6, 6), (14, 6)],
        "down": [(6, 14), (14, 14)],
        "left": [(6, 6), (6, 14)],
        "right": [(14, 6), (14, 14)]
    }
    
    for eye_pos in eye_positions[direction_name]:
        pygame.draw.circle(head, config.WHITE, eye_pos, 3)
        pygame.draw.circle(head, config.BLACK, eye_pos, 1.5)
    return head

def create_all_resources(config):
    """创建所有游戏资源"""
    try:
        if not os.path.exists(config.RESOURCE_DIR):
            os.makedirs(config.RESOURCE_DIR)
            
        # 创建并保存背景
        background = create_background(config)
        pygame.image.save(background, os.path.join(config.RESOURCE_DIR, "background.jpg"))
        
        # 创建并保存蛇身
        body = create_snake_body(config)
        pygame.image.save(body, os.path.join(config.RESOURCE_DIR, "body.png"))
        
        # 创建并保存食物
        food = create_food(config)
        pygame.image.save(food, os.path.join(config.RESOURCE_DIR, "food.png"))
        
        # 创建并保存各个方向的蛇头
        directions = ["up", "down", "left", "right"]
        for direction in directions:
            head = create_snake_head(config, direction)
            pygame.image.save(head, os.path.join(config.RESOURCE_DIR, f"head_{direction}.png"))
        
        return True
    except Exception as e:
        print(f"创建游戏素材时出错: {str(e)}")
        return False 