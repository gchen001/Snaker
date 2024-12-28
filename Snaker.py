"""
贪吃蛇游戏主程序

这个游戏实现了以下功能：
1. 基础的贪吃蛇玩法
2. 穿墙功能
3. 排行榜系统
4. 可调节速度
5. 图形化界面
6. 配置文件支持

作者：[Your Name]
版本：1.0.0
日期：2024-01-xx
"""

import pygame
import random
import sqlite3
from pygame.locals import *
import os
import shutil
from resource_creator import create_all_resources
import json
from sound_creator import create_all_sounds
from datetime import datetime


class Config:
    """
    游戏配置管理类
    
    负责从配置文件加载并管理所有游戏配置，包括：
    - 窗口设置
    - 游戏参数
    - 界面布局
    - 颜色定义
    - 方向常量
    - 资源路径
    - 音频设置
    """
    
    @classmethod
    def load(cls):
        """从config.json加载配置"""
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # 窗口设置
        cls.WINDOW_WIDTH = config['window']['width']
        cls.WINDOW_HEIGHT = config['window']['height']
        cls.GRID_SIZE = config['window']['grid_size']
        cls.GRID_WIDTH = cls.WINDOW_WIDTH // cls.GRID_SIZE
        cls.GRID_HEIGHT = cls.WINDOW_HEIGHT // cls.GRID_SIZE
        cls.WINDOW_TITLE = config['window']['title']
        
        # 游戏设置
        cls.MIN_SPEED = config['game']['min_speed']
        cls.MAX_SPEED = config['game']['max_speed']
        cls.DEFAULT_SPEED = config['game']['default_speed']
        
        # 颜色定义
        cls.WHITE = tuple(config['colors']['white'])
        cls.RED = tuple(config['colors']['red'])
        cls.GREEN = tuple(config['colors']['green'])
        cls.BLACK = tuple(config['colors']['black'])
        cls.DARK_GREEN = tuple(config['colors']['dark_green'])
        cls.LIGHT_GREEN = tuple(config['colors']['light_green'])
        cls.DARK_BG = tuple(config['colors']['dark_bg'])
        cls.GRID_COLOR = tuple(config['colors']['grid_color'])
        cls.GRAY = tuple(config['colors']['gray'])
        
        # 方向常量
        cls.UP = tuple(config['directions']['up'])
        cls.DOWN = tuple(config['directions']['down'])
        cls.LEFT = tuple(config['directions']['left'])
        cls.RIGHT = tuple(config['directions']['right'])
        
        # 资源设置
        cls.RESOURCE_DIR = config['resources']['directory']
        cls.DB_NAME = config['resources']['db_name']
        
        # UI配置
        cls.UI = config['ui']
        
        # 音频配置
        cls.AUDIO = config['audio']
        
        # 语录配置
        cls.quotes = config['quotes']

# 在程序开始时加载配置
Config.load()

# 初始化游戏
pygame.init()

# 初始化显示窗口
screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇')

# 设置中文字体
try:
    game_font = pygame.font.SysFont(
        Config.UI['fonts']['default']['name'], 
        Config.UI['fonts']['sizes']['score']
    )
except:
    game_font = pygame.font.SysFont(
        Config.UI['fonts']['default']['fallback'], 
        Config.UI['fonts']['sizes']['score']
    )

# 在初始化部分添加图片加载
def load_image(name, size=None):
    try:
        image = pygame.image.load(os.path.join(Config.RESOURCE_DIR, name))
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except:
        print(f"无法加载图片: {name}")  # 修复中文编码
        return None

class ScoreDB:
    """
    分数数据库管理类
    
    管理游戏分数的存储和检索，提供：
    - 分数保存
    - 排行榜查询
    - 数据库初始化
    """
    
    def __init__(self):
        """初始化数据库连接"""
        self.db_name = Config.DB_NAME
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 使用TEXT类型存储时间字符串
            c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (player_name TEXT, score INTEGER, date TEXT)''')
            conn.commit()
    
    def save_score(self, score):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 使用本地时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            c.execute("""
                INSERT INTO scores (player_name, score, date) 
                VALUES (?, ?, ?)
            """, ("Player", score, current_time))
            conn.commit()
    
    def get_leaderboard(self):
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            c.execute("""
                SELECT player_name, score, date
                FROM scores 
                ORDER BY score DESC 
                LIMIT 100
            """)
            return c.fetchall()
    
    def get_last_score_rank(self):
        """获取最后一次得分的排名"""
        with sqlite3.connect(self.db_name) as conn:
            c = conn.cursor()
            # 获取最新记录的分数
            c.execute("SELECT score FROM scores ORDER BY date DESC LIMIT 1")
            last_score = c.fetchone()
            if last_score:
                # 计算该分数的排名
                c.execute("""
                    SELECT COUNT(*) + 1 
                    FROM scores 
                    WHERE score > ?
                """, (last_score[0],))
                return last_score[0], c.fetchone()[0]
        return None, None

class ResourceManager:
    """
    游戏资源管理类（单例模式）
    
    统一管理游戏资源：
    - 背景图片
    - 蛇头图片（四个方向）
    - 蛇身图片
    - 食物图片
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """获取ResourceManager的单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if ResourceManager._instance is not None:
            raise Exception("This class is a singleton!")
        ResourceManager._instance = self
        self.background_image = None
        self.snake_head_images = {}
        self.snake_body_image = None
        self.food_image = None
        self.init_resources()
    
    def init_resources(self):
        """初始化游戏资源
        
        源处理流程：
        1. 清理旧资源文件夹（如果存在）
        2. 使用resource_creator创建新的资源：
           - 背景图片
           - 四个方向的蛇头图片
           - 蛇身图片
           - 食物图片
        3. 加载所有创建的图片资源
        """
        if os.path.exists(Config.RESOURCE_DIR):
            shutil.rmtree(Config.RESOURCE_DIR)
        create_all_resources(Config)  # 使用resource_creator.py中的函数
        
        # 检查音效文件夹是否存在
        sound_dir = Config.AUDIO['directory']
        if not os.path.exists(sound_dir):
            create_all_sounds(Config)  # 只在音效文件夹不存在时创建音效
        self.load_images()
    
    def load_images(self):
        self.background_image = load_image("background.jpg", (Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        self.snake_head_images = {
            Config.UP: load_image("head_up.png", (Config.GRID_SIZE, Config.GRID_SIZE)),
            Config.DOWN: load_image("head_down.png", (Config.GRID_SIZE, Config.GRID_SIZE)),
            Config.LEFT: load_image("head_left.png", (Config.GRID_SIZE, Config.GRID_SIZE)),
            Config.RIGHT: load_image("head_right.png", (Config.GRID_SIZE, Config.GRID_SIZE))
        }
        self.snake_body_image = load_image("body.png", (Config.GRID_SIZE-4, Config.GRID_SIZE-4))
        self.food_image = load_image("food.png", (Config.GRID_SIZE, Config.GRID_SIZE))

# 创建全局资源管理器实例
resource_manager = ResourceManager.get_instance()

class Snake:
    """
    蛇的实体类
    
    实现蛇的：
    - 移动逻辑
    - 碰撞检测
    - 生长机制
    - 图形渲染
    """
    
    def __init__(self):
        """初始化蛇的属性"""
        self.reset()
        
    def reset(self):
        self.length = 1
        self.positions = [(Config.GRID_WIDTH // 2, Config.GRID_HEIGHT // 2)]
        self.direction = random.choice([Config.UP, Config.DOWN, Config.LEFT, Config.RIGHT])
        self.color = Config.GREEN
        self.score = 0
        self.last_direction = self.direction
        self.game_over = False  # 添加游戏结束标志

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        """
        更新蛇的位置状态
        
        实现了以下功能：
        1. 保存当前方向，用于防止180度转向
        2. 计算新的头部位置，支持穿墙
        3. 检测是否撞到自己
        4. 更新蛇身位置
        
        Returns:
            bool: True表示移动成功，False表示游戏结束
        """
        self.last_direction = self.direction
        
        # 获���前头部位置
        cur = self.get_head_position()
        x, y = self.direction
        # 使用取模运算实现穿墙
        new = ((cur[0] + x) % Config.GRID_WIDTH, (cur[1] + y) % Config.GRID_HEIGHT)
        
        # 检查是否撞到自己（从第三个身体节点开始检查，因为不可能撞到紧跟头部的两个节点）
        if new in self.positions[2:]:
            return False
            
        # 在头部插入新位置，如果长度超出则删除尾部
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def draw(self, surface):
        resources = ResourceManager.get_instance()
        for i, p in enumerate(self.positions):
            if i == 0:  # 蛇头
                head_image = resources.snake_head_images.get(self.direction)
                if head_image:
                    surface.blit(head_image, 
                               (p[0] * Config.GRID_SIZE, p[1] * Config.GRID_SIZE))
            else:  # 蛇身
                if resources.snake_body_image:
                    surface.blit(resources.snake_body_image, 
                               (p[0] * Config.GRID_SIZE + 2, p[1] * Config.GRID_SIZE + 2))
                else:
                    # 如果片加载失败，使用原来的矩形���制
                    rect = pygame.Rect(
                        p[0] * Config.GRID_SIZE + 2,
                        p[1] * Config.GRID_SIZE + 2,
                        Config.GRID_SIZE - 4,
                        Config.GRID_SIZE - 4
                    )
                    pygame.draw.rect(surface, Config.DARK_GREEN, rect, border_radius=5)

class Food:
    """
    食物类
    
    管理食物的：
    - 位置生成
    - 图形渲染
    """
    
    def __init__(self):
        """初始化食物属性"""
        self.position = (0, 0)
        self.color = Config.RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, Config.GRID_WIDTH-1),
                        random.randint(0, Config.GRID_HEIGHT-1))

    def draw(self, surface):
        resources = ResourceManager.get_instance()
        if resources.food_image:
            surface.blit(resources.food_image, 
                        (self.position[0] * Config.GRID_SIZE, 
                         self.position[1] * Config.GRID_SIZE))
        else:
            # 如果图片加载失败，使用原来的矩形绘制
            pygame.draw.rect(surface, self.color,
                           (self.position[0] * Config.GRID_SIZE,
                            self.position[1] * Config.GRID_SIZE,
                            Config.GRID_SIZE, Config.GRID_SIZE))

def draw_leaderboard(screen, score_db, scroll_position=0):
    """绘制排行榜（支持滚动）
    
    Args:
        screen: pygame显示表面
        score_db: 分数数据库实例
        scroll_position: 滚动位置（像素）
    """
    leaderboard = score_db.get_leaderboard()
    last_score, last_rank = score_db.get_last_score_rank()
    config = Config.UI['leaderboard']
    
    # 计算内容总高度
    content_height = config['title_spacing'] + len(leaderboard) * config['spacing'] + 40
    
    # 创建完整的排行榜表面
    full_surface = pygame.Surface((config['width'], content_height))
    full_surface.fill(tuple(config['background_color']))
    
    # 绘制标题
    title_font = pygame.font.SysFont(
        Config.UI['fonts']['default']['name'],
        Config.UI['fonts']['sizes']['leaderboard_title']
    )
    title = title_font.render("排行榜", True, Config.WHITE)
    title_x = (config['width'] - title.get_width()) // 2
    full_surface.blit(title, (title_x, 20))
    
    # 绘制排行榜内容
    item_font = pygame.font.SysFont(
        Config.UI['fonts']['default']['name'],
        Config.UI['fonts']['sizes']['leaderboard_item']
    )
    
    y = config['title_spacing'] + 20
    
    for i, (name, score, date) in enumerate(leaderboard, 1):
        is_last_score = last_score is not None and score == last_score and i == last_rank
        
        rank_text = f"#{i}"
        score_text = f"{score}分"
        date_text = date[5:16]
        
        rank_x = config['item_padding']
        score_x = config['width'] - config['item_padding'] - item_font.size(score_text)[0]
        date_x = (config['width'] - item_font.size(date_text)[0]) // 2
        
        color = Config.WHITE
        if is_last_score:
            color = (255, 140, 0)
        elif i == 1:
            color = (255, 215, 0)
        elif i == 2:
            color = (192, 192, 192)
        elif i == 3:
            color = (205, 127, 50)
        
        rank = item_font.render(rank_text, True, color)
        score = item_font.render(score_text, True, color)
        date = item_font.render(date_text, True, Config.GRAY if not is_last_score else color)
        
        full_surface.blit(rank, (rank_x, y))
        full_surface.blit(score, (score_x, y))
        full_surface.blit(date, (date_x, y))
        
        y += config['spacing']
    
    # 创建可视区域
    visible_height = config['height']
    visible_surface = pygame.Surface((config['width'], visible_height))
    visible_surface.fill(tuple(config['background_color']))
    
    # 限���滚动范围
    max_scroll = max(0, content_height - visible_height)
    scroll_position = max(0, min(scroll_position, max_scroll))
    
    # 将完整表面的可视部分绘制到可视区域
    visible_surface.blit(full_surface, (0, -scroll_position))
    
    # 设置透明度
    visible_surface.set_alpha(config['opacity'])
    
    # 绘制到屏幕
    screen.blit(visible_surface, (config['x_offset'], config['y_offset']))
    
    return scroll_position  # 返回实际的滚动位置

class GameState:
    """
    游戏状态管理类
    
    维护游戏的：
    - 运行状态
    - 暂停状态
    - 游戏速度
    - 结束状态
    - 方向队列
    """
    
    def __init__(self):
        """初始化游戏状态"""
        self.running = True
        self.paused = False
        self.game_speed = Config.DEFAULT_SPEED
        self.show_game_over = False
        self.direction_queue = []
        self.leaderboard_scroll = 0  # 添加排行榜滚动位置

class Dialog:
    """
    对话框类
    
    提供：
    - 确认对话框显示
    - 用户交互处理
    - 按钮响应
    """
    
    def __init__(self, screen):
        """初始化对话框"""
        self.screen = screen
        self.config = Config.UI['dialog']
        self.showing = False
        self.result = None
        self.selected_button = 0  # 0: 确定按钮, 1: 取消按钮
        self.audio = AudioManager.get_instance()  # 添加音频管理器实例
        
        # 计算对话框位置
        self.x = (Config.WINDOW_WIDTH - self.config['width']) // 2
        self.y = (Config.WINDOW_HEIGHT - self.config['height']) // 2
        
        # 计算按钮位置
        button_y = self.y + self.config['height'] - self.config['button_height'] - 20
        self.yes_button = pygame.Rect(
            self.x + self.config['button_spacing'],
            button_y,
            self.config['button_width'],
            self.config['button_height']
        )
        self.no_button = pygame.Rect(
            self.x + self.config['width'] - self.config['button_width'] - self.config['button_spacing'],
            button_y,
            self.config['button_width'],
            self.config['button_height']
        )
    
    def show(self):
        self.showing = True
        self.result = None
        self.selected_button = 0  # 默认选中"确定"按钮
    
    def hide(self):
        self.showing = False
    
    def handle_event(self, event):
        """处理对话框事件
        
        处理以下输入：
        1. 鼠标点击确定/取消按钮
        2. 键盘Enter键（确定当前选择）
        3. 键盘ESC键（取消）
        4. 方向键左右（切换选择）
        """
        if not self.showing:
            return False
            
        if event.type == MOUSEBUTTONDOWN:
            if self.yes_button.collidepoint(event.pos):
                self.result = True
                return True
            elif self.no_button.collidepoint(event.pos):
                self.result = False
                return True
        elif event.type == MOUSEMOTION:
            # 鼠标悬停时更新选中状态
            if self.yes_button.collidepoint(event.pos):
                self.selected_button = 0
            elif self.no_button.collidepoint(event.pos):
                self.selected_button = 1
        elif event.type == KEYDOWN:
            if event.key in (K_RETURN, K_KP_ENTER):  # Enter键确认当前选择
                self.result = (self.selected_button == 0)
                return True
            elif event.key == K_ESCAPE:  # ESC键取消
                self.result = False
                return True
            elif event.key in (K_LEFT, K_RIGHT):  # 左右键切换选择
                self.selected_button = 1 - self.selected_button  # 在0和1之间切换
                self.audio.play_sound('button')  # 播放切换音效
        return False
    
    def draw(self):
        if not self.showing:
            return
            
        # 绘制半透明背景
        overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # 绘制对话框背景
        dialog_surface = pygame.Surface((self.config['width'], self.config['height']))
        dialog_surface.fill(tuple(self.config['background_color']))
        dialog_surface.set_alpha(self.config['opacity'])
        self.screen.blit(dialog_surface, (self.x, self.y))
        
        # 绘制文本
        font = pygame.font.SysFont(
            Config.UI['fonts']['default']['name'],
            self.config['text_size']
        )
        text = font.render(self.config['text'], True, Config.WHITE)
        text_x = self.x + (self.config['width'] - text.get_width()) // 2
        text_y = self.y + 30
        self.screen.blit(text, (text_x, text_y))
        
        # 绘制按钮
        buttons = [(self.yes_button, self.config['yes_text'], 0), 
                  (self.no_button, self.config['no_text'], 1)]
        
        for button, text, index in buttons:
            # 根据是否选中使用不同颜色
            color = Config.WHITE if self.selected_button == index else Config.GRAY
            pygame.draw.rect(self.screen, color, button, border_radius=5)
            button_text = font.render(text, True, 
                                    Config.BLACK if self.selected_button == index else Config.WHITE)
            text_x = button.x + (button.width - button_text.get_width()) // 2
            text_y = button.y + (button.height - button_text.get_height()) // 2
            self.screen.blit(button_text, (text_x, text_y))

class AudioManager:
    """
    音效管理类（单例模式）
    
    负责：
    - 背景音乐播放
    - 音效播放
    - 音量控制
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if AudioManager._instance is not None:
            raise Exception("This class is a singleton!")
        AudioManager._instance = self
        
        # 初始化音频系统
        pygame.mixer.init()
        
        # 加载音效
        self.sounds = {}
        sound_dir = Config.AUDIO['directory']
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            
        # 加载所有音效
        for sound_name, sound_file in Config.AUDIO['sounds'].items():
            try:
                sound_path = os.path.join(sound_dir, sound_file)
                if sound_name == 'background':
                    pygame.mixer.music.load(sound_path)
                    pygame.mixer.music.set_volume(Config.AUDIO['volume'])
                else:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(Config.AUDIO['volume'])
            except:
                print(f"无法加载音效: {sound_file}")
        
        self.background_music_enabled = True  # 添加背景音乐开关状态
    
    def toggle_background_music(self):
        """切换背景音乐开关状态"""
        self.background_music_enabled = not self.background_music_enabled
        if self.background_music_enabled:
            self.play_background()
        else:
            self.stop_background()
    
    def play_background(self):
        """播放背景音乐（循环）"""
        try:
            if self.background_music_enabled:  # 只在启用状态下播放
                pygame.mixer.music.play(-1)
        except:
            print("无法播放背景音乐")
    
    def stop_background(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
    
    def play_sound(self, sound_name):
        """播放指定音效"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_death_sound(self):
        """播放死亡音效并暂停背景音乐"""
        self.stop_background()
        if 'death' in self.sounds:
            self.sounds['death'].play()
            # 设置定时器在死亡音效结束后恢复背景音乐
            pygame.time.set_timer(
                pygame.USEREVENT + 1,
                Config.AUDIO['durations']['death']
            )

class QuoteManager:
    """语录管理类"""
    def __init__(self):
        self.quotes = Config.quotes['items']
        self.quote_file = Config.quotes['file']
    
    def get_random_quote(self):
        """获取随机语录"""
        quote = random.choice(self.quotes)
        self._log_quote(quote)
        return quote
    
    def _log_quote(self, quote):
        """记录语录使用历史"""
        try:
            with open(self.quote_file, 'a', encoding='utf-8') as f:
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{time}] {quote}\n")
        except Exception as e:
            print(f"记录语录失败: {str(e)}")

class Game:
    """
    游戏主类
    
    负责：
    - 游戏主循环
    - 输入处理
    - 状态更新
    - 画面渲染
    """
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption('贪吃蛇')
        self.clock = pygame.time.Clock()
        
        self.state = GameState()
        self.resources = ResourceManager.get_instance()
        self.score_db = ScoreDB()
        self.snake = Snake()
        self.food = Food()
        self.dialog = Dialog(self.screen)
        self.audio = AudioManager.get_instance()
        self.audio.play_background()
        self.show_key_help = False  # 添加按键说明显示状态
        self.quote_manager = QuoteManager()
        self.exit_quote = None
        self.exit_timer = 0
    
    def draw_key_help(self):
        """绘制按键说明"""
        config = Config.UI['key_help']
        
        # 创建半透明背景
        help_surface = pygame.Surface((config['width'], config['height']))
        help_surface.fill(tuple(config['background_color']))
        help_surface.set_alpha(config['opacity'])
        
        # 计算位置（居中显示）
        x = (Config.WINDOW_WIDTH - config['width']) // 2
        y = (Config.WINDOW_HEIGHT - config['height']) // 2
        
        # 绘制标题
        title_font = pygame.font.SysFont(
            Config.UI['fonts']['default']['name'],
            config['title_size']
        )
        title = title_font.render(config['title'], True, Config.WHITE)
        title_x = x + (config['width'] - title.get_width()) // 2
        
        # 绘制内容
        text_font = pygame.font.SysFont(
            Config.UI['fonts']['default']['name'],
            config['text_size']
        )
        
        # 绘制到屏幕
        self.screen.blit(help_surface, (x, y))
        self.screen.blit(title, (title_x, y + 20))
        
        # 绘制每一行说明文本
        text_y = y + 70
        for item in config['items']:
            text = text_font.render(item, True, Config.WHITE)
            text_x = x + 30
            self.screen.blit(text, (text_x, text_y))
            text_y += config['spacing']
    
    def handle_input(self):
        """处理用户输入
        
        处理逻辑：
        1. 如果对话框显示中，优先处理对话框事件
        2. 处理游戏退出事件（关闭窗口或ESC键）
        3. 处理游戏结束状态下的重新开始事件
        4. 处理游戏进行中的各种输入：
           - 方向控制（防止180度转向）
           - 暂停/继续
           - 速度调节
        """
        for event in pygame.event.get():
            if self.dialog.showing:
                if self.dialog.handle_event(event):
                    if self.dialog.result:
                        if not self.snake.game_over and self.snake.score > 0:
                            self.score_db.save_score(self.snake.score)
                        self.show_exit_quote()  # 显示退出语录
                    self.dialog.hide()
                continue
                
            if event.type == QUIT:
                self.dialog.show()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.dialog.show()
                if self.state.show_game_over:
                    if event.key == K_3:  # 按3键重新开始
                        self.snake.reset()
                        self.state.show_game_over = False
                        self.state.game_speed = Config.DEFAULT_SPEED
                else:
                    new_direction = None
                    if event.key == K_UP and self.snake.direction != Config.DOWN:
                        new_direction = Config.UP
                    elif event.key == K_DOWN and self.snake.direction != Config.UP:
                        new_direction = Config.DOWN
                    elif event.key == K_LEFT and self.snake.direction != Config.RIGHT:
                        new_direction = Config.LEFT
                    elif event.key == K_RIGHT and self.snake.direction != Config.LEFT:
                        new_direction = Config.RIGHT
                    elif event.key == K_k:
                        self.state.paused = not self.state.paused
                    elif event.key == K_1 and self.state.game_speed < Config.MAX_SPEED:
                        self.state.game_speed += 1
                    elif event.key == K_2 and self.state.game_speed > Config.MIN_SPEED:
                        self.state.game_speed -= 1
                    elif event.key == K_SPACE:  # 空格键切换背景音乐
                        self.audio.toggle_background_music()
                        self.audio.play_sound('button')  # 播放按键音效
                    elif event.key == K_s:  # S键切换按键说明显示
                        self.show_key_help = not self.show_key_help
                        self.audio.play_sound('button')
                    
                    if new_direction and (not self.state.direction_queue or 
                                        new_direction != self.state.direction_queue[-1]):
                        self.state.direction_queue.append(new_direction)
                # 按键音效
                if event.key in [K_1, K_2, K_3, K_k]:
                    self.audio.play_sound('button')
            elif event.type == pygame.USEREVENT + 1:  # 死亡音效结束
                self.audio.play_background()
            # 处理鼠标滚轮事件
            elif event.type == pygame.MOUSEWHEEL:
                if self.state.paused or self.state.show_game_over:
                    # 向上滚动为正，向下滚动为负
                    self.state.leaderboard_scroll -= event.y * 30  # 30是滚动速度
    
    def update(self):
        """更新游戏状态
        
        更新逻辑：
        1. 检查游戏是否暂停或结束
        2. 处理方向队列，确保平滑转向：
           - 每次只处理队列中的第一个方向
           - 确保不会180度转向
        3. 更新蛇的位置
        4. 检查是否吃到食物：
           - 增加长度
           - 更新分数
           - 生成新的食物位置
        5. 处理游戏结束：
           - 保存分数
           - 显示结束画面
        """
        if not self.state.paused and not self.state.show_game_over:
            # 处理方向队列
            if self.state.direction_queue and len(self.state.direction_queue) > 0:
                next_direction = self.state.direction_queue[0]
                if ((next_direction[0], next_direction[1]) != 
                    (-self.snake.direction[0], -self.snake.direction[1])):
                    self.snake.direction = next_direction
                    self.state.direction_queue.pop(0)
            
            if self.snake.update():
                if self.snake.get_head_position() == self.food.position:
                    self.snake.length += 1
                    self.snake.score += 1
                    self.food.randomize_position()
                    self.audio.play_sound('eat')
            else:
                self.score_db.save_score(self.snake.score)
                self.state.show_game_over = True
                self.snake.game_over = True
                self.audio.play_death_sound()
    
    def render(self):
        """渲染游戏画面"""
        if not self.state.paused and not self.state.show_game_over:
            if self.resources.background_image:
                self.screen.blit(self.resources.background_image, (0, 0))
            else:
                self.screen.fill(Config.DARK_BG)
            
            self.snake.draw(self.screen)
            self.food.draw(self.screen)

            # 显示分数和速度
            score_font = pygame.font.SysFont(
                Config.UI['fonts']['default']['name'],
                Config.UI['fonts']['sizes']['score']
            )
            score_text = score_font.render(
                f'分数: {self.snake.score} 速度: {self.state.game_speed}', 
                True, Config.WHITE
            )
            self.screen.blit(score_text, (10, 10))
        
        elif self.state.show_game_over:
            self.screen.fill(Config.DARK_BG)
            # 更新滚动位置并绘制排行榜
            self.state.leaderboard_scroll = draw_leaderboard(
                self.screen, 
                self.score_db, 
                self.state.leaderboard_scroll
            )
            
            # 显示重新开始提示
            gameover_font = pygame.font.SysFont(
                Config.UI['fonts']['default']['name'],
                Config.UI['fonts']['sizes']['game_over']
            )
            restart_text = gameover_font.render("按 3 重新开始游戏", True, Config.WHITE)
            self.screen.blit(restart_text, (Config.WINDOW_WIDTH//2 - 100, Config.WINDOW_HEIGHT - 50))
        
        elif self.state.paused:
            # 更新滚动位置并绘制排行榜
            self.state.leaderboard_scroll = draw_leaderboard(
                self.screen, 
                self.score_db, 
                self.state.leaderboard_scroll
            )

        # 在对话框之前绘制按键说明提示
        hint_font = pygame.font.SysFont(
            Config.UI['fonts']['default']['name'],
            Config.UI['fonts']['sizes']['score']
        )
        hint_text = hint_font.render("按S键显示按键说明", True, Config.WHITE)
        self.screen.blit(hint_text, (10, Config.WINDOW_HEIGHT - 30))
        
        # 如果需要显示按键说明
        if self.show_key_help:
            self.draw_key_help()
        
        if self.dialog.showing:
            self.dialog.draw()

        # 如果有退出语录，显示它
        if self.exit_quote:
            # 创建半透明背景
            overlay = pygame.Surface((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(200)
            self.screen.blit(overlay, (0, 0))
            
            # 显示语录
            quote_font = pygame.font.SysFont(
                Config.UI['fonts']['default']['name'],
                Config.quotes['font_size']
            )
            quote_text = quote_font.render(self.exit_quote, True, Config.WHITE)
            x = (Config.WINDOW_WIDTH - quote_text.get_width()) // 2
            y = (Config.WINDOW_HEIGHT - quote_text.get_height()) // 2
            self.screen.blit(quote_text, (x, y))

    def show_exit_quote(self):
        """显示退出语录"""
        if not self.exit_quote:
            self.exit_quote = self.quote_manager.get_random_quote()
            self.exit_timer = pygame.time.get_ticks()
    
    def run(self):
        """运行游戏主循环"""
        while self.state.running:
            self.handle_input()
            self.update()
            self.render()
            pygame.display.update()
            
            # 检查是否需要退出
            if self.exit_quote:
                current_time = pygame.time.get_ticks()
                if current_time - self.exit_timer >= Config.quotes['display_time']:
                    self.state.running = False
            
            self.clock.tick(self.state.game_speed)
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()