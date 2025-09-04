# 炎龙骑士团II资源分析器

一个用Python编写的炎龙骑士团II游戏资源提取工具，支持多种DAT文件格式的分析和图像提取。

## 功能特性

### 📦 支持的文件格式

- **FDOTHER.DAT** - 混合资源文件（形状、字体、面部、界面元素等）
- **FDICON.B24** - 人物图标资源（1680个24x24像素图标）
- **DATO.DAT** - 人物表情资源（137个角色×4种表情）
- **BG.DAT** - 战斗背景资源（56个战斗背景）

### 🚀 主要功能

- 自动识别文件类型并应用相应的解码算法
- 支持RLE压缩格式解码
- 多种调色板支持
- 批量处理功能
- 智能错误处理和数据验证

## 使用方法

### 安装依赖

```bash
pip install pillow
```

### 基本用法

```bash
# 分析单个文件
python fd2_analyzer.py FDOTHER.DAT -o output_images

# 批量处理目录中的所有支持文件
python fd2_analyzer.py -b game_data_directory -o all_images

# 查看帮助
python fd2_analyzer.py --help
```

### 输出文件命名规则

- FDOTHER: `fdother_[类型]_[主索引]_[子索引].png`
- FDICON: `icon_[索引].png`
- DATO: `face_[角色]_[表情].png`
- BG: `bg_[索引].png`

## 技术特性

- **Python 3.x** 兼容
- **PIL/Pillow** 图像处理
- **无外部依赖** 的二进制解析
- **模块化设计** 便于扩展
- **完整的错误处理** 和日志记录

## 项目结构

```
FD2ResViewer/
├── fd2_analyzer.py      # 主分析器（推荐使用）
├── main.py             # 核心分析类
├── README.md           # 项目说明
├── README_Extensions.md # 功能扩展说明
├── .gitignore          # Git忽略文件
└── 资源文件/
    ├── colorPanel      # 调色板1
    ├── colornew        # 调色板2
    ├── colornew2       # 调色板3
    └── SingleBitBMPHeader # BMP头文件
```

## 开发信息

这个项目是基于C#原版FD2ResourcesViewer移植到Python的版本，保持了原始功能的同时增加了新的特性：

- 支持命令行批量处理
- 更好的错误处理
- 模块化的代码结构
- 跨平台兼容性

## 许可证

本项目用于学习和研究目的。游戏资源文件的版权归原游戏开发商所有。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！