# Python贪吃蛇游戏

一个基于 Pygame 开发的现代化贪吃蛇游戏。具有精美的图形界面、音效系统、排行榜、配置系统等特性，支持键盘控制和自定义设置。

## 功能特点

- 🐍 精美的图形界面，支持多种皮肤和背景
- 🎮 经典的贪吃蛇玩法，支持穿墙
- 🎵 可自定义的背景音乐和音效系统
- 📊 本地排行榜系统，支持滚动显示
- ⚙️ 动态速度调节（5-20档可调）
- 🎨 半透明UI界面，支持鼠标和键盘操作
- 💾 完整的JSON配置系统
- 🔍 游戏内帮助系统
- 📝 随机退出语录系统，并记录历史
- 🎯 支持暂停/继续功能

## 安装说明

1. 克隆仓库

```bash
git clone https://github.com/yourusername/snake-game.git
cd snake-game
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 运行游戏

```bash
python Snaker.py
```

## 系统要求

- Python 3.6+
- Pygame 2.0+
- NumPy
- SciPy
- Pydub (用于音频转换)

## 游戏控制

| 按键 | 功能 |
|------|------|
| 方向键 | 控制蛇的移动 |
| K键 | 显示/隐藏排行榜 |
| 1键 | 加速 |
| 2键 | 减速 |
| 3键 | 游戏结束时重新开始 |
| 空格键 | 开启/关闭背景音乐 |
| S键 | 显示按键说明 |
| ESC键 | 退出游戏 |

## 项目结构

```
snake-game/
├── Snaker.py          # 主游戏文件
├── config.json        # 游戏配置文件
├── config.md          # 配置说明文档
├── resource_creator.py # 资源生成器
├── sound_creator.py   # 音效生成器
├── audio_converter.py # 音频格式转换工具
├── requirements.txt   # 项目依赖
├── resources/         # 游戏资源目录
│   ├── background.jpg
│   ├── head_*.png
│   ├── body.png
│   └── food.png
├── sounds/           # 音效文件目录
│   ├── background.wav
│   ├── button.wav
│   ├── death.wav
│   └── eat.wav
└── README.md         # 项目说明文档
```


## 主要特性说明

### 配置系统

- 所有游戏参数都可在 `config.json` 中配置
- 支持热重载，无需重新编译
- 详细的配置说明文档 `config.md`

### 音效系统

- 支持背景音乐和多种音效
- 可通过 `sound_creator.py` 生成自定义音效
- 支持 `audio_converter.py` 转换外部音频

### 排行榜系统

- SQLite数据库存储
- 支持鼠标滚轮滚动
- 显示时间戳和分数
- 突出显示最新得分

### 资源系统

- 自动生成游戏素材
- 支持失败时的降级显示
- 统一的资源管理器

### 添加新功能

1. 在 `config.json` 中添加相关配置
2. 在 `Config` 类中添加配置加载代码
3. 实现功能逻辑
4. 更新配置文档

### 自定义音效

1. 修改 `sound_creator.py` 中的音效生成代码
2. 或使用 `audio_converter.py` 转换自定义音频文件

### 修改游戏素材

1. 更新 `resource_creator.py` 中的生成代码
2. 或直接替换 resources 目录中的文件

## 版本历史

- 1.0.0 (2024-12)
  - 初始版本发布
  - 完整的游戏功能
  - 配置系统
  - 音效系统
  - 排行榜系统
  - 帮助系统
  - 退出语录系统


## 致谢

- Pygame 社区提供的游戏开发框架
- NumPy 和 SciPy 提供的科学计算支持
- Pydub 提供的音频处理功能
