# 炎龙骑士团II DAT文件数据结构分析

## 概述

本文档描述了炎龙骑士团II资源文件中各个DAT文件的头部数据结构及其加载解析流程。所有文件都采用类似的索引表+数据块的存储模式，但具体的索引结构有所不同。

---

## 通用数据结构

### DataBlock结构
```python
class DataBlock:
    startOffset: int  # 数据块起始偏移
    length: int       # 数据块长度
```

### 通用文件头格式
大部分DAT文件都以6字节的头部开始：
- **字节 0-1**: 未知/保留
- **字节 2-5**: 第一个数据块的起始偏移（通常为6，即跳过头部）

---

## 1. FDICON.B24 - 人物图标

### 文件结构
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 索引表 (1681项)   |  每项4字节 uint32 共6724字节
| [偏移量0]        |
| [偏移量1]        |
| ...              |
| [偏移量1680]     |
+------------------+ <- 6730
| 数据区           |
| [图标0数据]       |
| [图标1数据]       |
| ...              |
+------------------+
```

### 索引结构
- **索引数量**: 1681个图标
- **索引位置**: 从偏移6开始，每4字节一个uint32
- **数据块计算**: `DataBlock(array[i], array[i+1] - array[i])`
- **最后一块**: `DataBlock(array[1680], 文件长度 - array[1680])`

### 解析流程
```
load_fdicon_file() 
  -> 读取文件到fileDatas
  -> AnalysisICON()
      -> 循环读取索引表 (num = 6; num <= 6726; num += 4)
      -> 创建1681个DataBlock
  -> generate_icon_images()
      -> 使用makeShapBMP(24, 24, ...)生成24x24图标
```

---

## 2. FDTXT.DAT - 文本资源

### 文件结构（二级索引）
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 主索引表 (35项)   |  每项4字节 uint32 共140字节
| [偏移量0]        |
| [偏移量1]        |
| ...              |
| [偏移量34]       |
+------------------+
| 子块数量区       |  每个主分类起始处有子块数量
| 子块偏移表       |  每个主分类有多个4字节偏移量
+------------------+
```

### 索引结构
- **主分类数量**: 35个
- **主索引表**: 从偏移6开始，每4字节一个uint32
- **子块数量**: 在每个主分类的起始位置读取short值 `/ 2`
- **子块偏移表**: 每个主分类有N个子块偏移量

### 解析流程
```
load_fdtxt_file()
  -> 读取文件到fileDatas
  -> AnalysisTXT()
      -> 读取35个主偏移量到array
      -> 对每个主分类:
          -> 读取子块数量 (array[i]位置的short / 2)
          -> 读取子块偏移量数组
          -> 创建DataBlock数组
  -> generate_fdtxt_files()
      -> 对每个子块调用makeWord()解析文本
```

---

## 3. DATO.DAT - 人物表情

### 文件结构（二级索引）
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 主索引表 (137项)  |  每项4字节 uint32 共548字节
| [人物0偏移]       |
| [人物1偏移]       |
| ...              |
| [人物136偏移]    |
+------------------+
| 表情数据区        |  每个人物4个表情
+------------------+
```

### 索引结构
- **人物数量**: 137个
- **每个人物**: 4个表情
- **主索引表**: 从偏移6开始
- **子块结构**: 每个人物的4个表情偏移量

### 解析流程
```
load_dato_file()
  -> 读取文件到fileDatas
  -> AnalysisDATO()
      -> 读取137个人物偏移量
      -> 对每个人物:
          -> 读取4个表情的偏移量
          -> 创建4个DataBlock
  -> generate_dato_images()
      -> 使用makeFaceBMP()生成面部图像
```

---

## 4. BG.DAT - 战斗背景

### 文件结构
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 索引表 (57项)     |  每项4字节 uint32 共228字节
| [背景0偏移]       |
| [背景1偏移]       |
| ...              |
| [背景56偏移]     |
+------------------+ <- 234
```

### 索引结构
- **背景数量**: 57个
- **索引表**: 从偏移6开始，每4字节一个uint32
- **数据块**: `DataBlock(array[i], array[i+1] - array[i])`
- **最后一块**: `DataBlock(array[56], 文件长度 - array[56])`

### 解析流程
```
load_bg_file()
  -> 读取文件到fileDatas
  -> AnalysisBG()
      -> 读取57个背景偏移量
      -> 创建57个DataBlock
  -> generate_bg_images()
      -> 使用makeBgBMP()生成背景图像
```

---

## 5. TAI.DAT - 战斗动作图像

### 文件结构
与BG.DAT完全相同的结构：
- **动作数量**: 57个
- **索引表**: 从偏移6开始，每4字节一个uint32

### 解析流程
```
load_tai_file()
  -> 读取文件到fileDatas
  -> AnalysisTAI()
      -> 读取57个动作偏移量
      -> 创建57个DataBlock
  -> generate_tai_images()
      -> 使用makeTAIBMP()生成动作图像
```

---

## 6. FIGANI.DAT - 战斗动作序列

### 文件结构（二级索引）
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 主索引表 (409项)  |  每项4字节 uint32
| [动作0偏移]       |
| [动作1偏移]       |
| ...              |
| [动作408偏移]    |
+------------------+
| 动作数据区        |
| [动作0帧数据]     |  每个动作帧数不固定
+------------------+
```

### 索引结构
- **动作数量**: 409个
- **主索引表**: 从偏移6开始，每4字节一个uint32
- **子块（帧）数量**: 在每个动作起始位置读取byte
- **子块偏移表**: 每个动作有N个帧偏移量

### 解析流程
```
load_figani_file()
  -> 读取文件到fileDatas
  -> AnalysisFIGANI()
      -> 读取409个动作偏移量
      -> 对每个动作:
          -> 读取帧数量 (偏移量array[i]处的byte)
          -> 读取各帧偏移量
          -> 创建DataBlock数组
  -> generate_figani_images()
      -> 使用makeFightBMP()生成帧图像
```

---

## 7. FDSHAP.DAT - 形状资源

### 文件结构（二级索引）
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 主索引表 (67项)   |  每项4字节 uint32
| [形状0偏移]       |
| [形状1偏移]       |
| ...              |
| [形状66偏移]     |
+------------------+
| 形状数据区        |
| [形状0子块]       |  每个形状有多个子块
+------------------+
```

### 索引结构
- **形状数量**: 67个
- **主索引表**: 从偏移6开始，每4字节一个uint32
- **子块数量**: 在每个形状起始位置+4偏移处读取short
- **子块偏移表**: 从起始位置+6开始，每4字节一个uint32

### 解析流程
```
load_fdshap_file()
  -> 读取文件到fileDatas
  -> AnalysisFDSHAP()
      -> 读取67个形状偏移量
      -> 对每个形状:
          -> 读取子块数量 (偏移+4处的short)
          -> 读取各子块偏移量 (从偏移+6开始)
          -> 创建DataBlock数组
  -> generate_fdshap_images()
      -> 使用makeShapBMP(24, 24, ...)生成24x24形状图像
```

---

## 8. FDFIELD.DAT - 地图资源

### 文件结构
与BG.DAT相同的简单索引结构：
- **地图数量**: 100个
- **索引表**: 从偏移6开始，每4字节一个uint32

### 解析流程
```
load_fdfield_file()
  -> 读取文件到fileDatas
  -> AnalysisFDFIELD()
      -> 读取100个地图偏移量
      -> 创建100个DataBlock
  -> generate_fdfield_images()
      -> 使用makeFieldBMP()生成地图图像
      -> 依赖FDSHAP.DAT的图块数据
```

---

## 9. FDOTHER.DAT - 混合资源

### 文件结构
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| 索引表 (104项)    |  每项4字节 uint32
| [分类0偏移]       |
| [分类1偏移]       |
| ...              |
| [分类103偏移]    |
+------------------+ <- 422
| 分类数据区        |
| [分类0数据]       |  分类内部结构各异
| [分类1数据]       |
| ...              |
+------------------+
```

### 索引结构
- **分类数量**: 104个
- **索引表**: 从偏移6开始，每4字节一个uint32

### 分类内部结构（按subIndex区分）
| subIndex | 内部结构 | 图像生成方法 |
|----------|---------|-------------|
| 1, 14 | 偏移表结构，子块数量在+6处 | makeShapBMP |
| 2 | 偏移表结构，子块数量在起始处/4 | makeBMP |
| 4 | 固定32字节分块 | makeFontBMP |
| 5, 6, 9, 96 | 偏移表结构，子块数量在+6处 | makeFaceBMP/makeBMP/makeShapBMP |
| 7, 12, 13, 63 | 特殊偏移表结构 | makeShapBMP/makeFaceBMP/makeBMP |
| 10, 15 | 宽度高度+数据 | makeFaceBMP |
| 11, 16, 17, 46, 47, 56, 59-62, 69-75, 97, 98, 100 | 宽度高度+数据 | makeShapBMP |
| 55 | 宽度高度+数据 | makeBMP |
| 79 | 特殊偏移表结构 | makeBMP |

### 解析流程
```
load_fdother_file()
  -> 读取文件到fileDatas
  -> AnalysisOTHER()
      -> 读取104个分类偏移量
      -> 创建104个DataBlock
  -> 对每个subIndex调用AnalysisOtherSubs()
      -> 根据subIndex类型解析子块结构
  -> 对每个subIndex调用AnalysisOtherSubsImage()
      -> 根据类型生成对应图像
```

---

## 10. ANI.DAT - 动画资源

### 文件结构（AFM动画单元）
```
+------------------+ <- 0
| 文件头部 (6字节)   |
+------------------+ <- 6
| AFM偏移表         |  每项4字节 uint32，读到0为止
| [AFM0偏移]        |
| [AFM1偏移]        |
| ...               |
| [0] (结束)        |
+------------------+
| AFM0数据          |
| "AFM - Animation File Manager..."  |
| "Empty Title."                    |
| [帧数据1]                         |
| [帧数据2]                         |
+------------------+
| AFM1数据          |
| ...               |
+------------------+
```

### 索引结构
- **AFM单元数量**: 不固定，读到 offset=0 为止（最多20个）
- **偏移表**: 从偏移6开始，每4字节一个uint32，直到遇到0
- **AFM有效性验证**: 检查 `offset + 165` 处的 frame_count 是否在 1-999 范围内

### AFM动画单元内部结构
- **偏移 +165~+166**: `frame_count`（帧数量，ushort）
- **偏移 +173**: 帧数据开始

### 帧格式（命令驱动）
帧数据使用命令驱动的解码方式，每个命令占1字节：

| 命令 | 名称 | 数据格式 | 功能 |
|------|------|----------|------|
| 0x00 | 填充调色板 | `[颜色:BYTE]` | 用单色填充整个调色板 |
| 0x01 | 复制调色板 | `[768字节数据]` | 直接复制768字节调色板数据 |
| 0x02 | RLE解码调色板 | RLE压缩数据 | RLE解码到调色板 |
| 0x04 | 填充像素 | `[字节:BYTE]` | 用单色填充64000像素缓冲区 |
| 0x05 | 复制像素 | `[64000字节数据]` | 直接复制像素数据 |
| 0x06 | RLE解码像素 | RLE压缩数据 | RLE解码到像素缓冲区 |
| 0x07 | 点绘制 | `[count:WORD][(offset:WORD,color:BYTE)×count]` | 绘制单个像素点 |
| 0x08 | 填充段 | `[count:WORD][(offset:WORD,size:BYTE,color:BYTE)×count]` | 填充连续像素段 |
| 0x09 | 复制数据 | `[count:WORD][(dst:WORD,size:BYTE,data)×count]` | 复制任意数据块 |

### RLE解码格式（命令0x02/0x06）
- **字节值 0xC0-0xFF**: `count = value & 0x3F`，下一字节为颜色，重复count次
- **字节值 0x00-0x3F**: 直接作为颜色值写入

### 图像规格
- **固定分辨率**: 320×200 像素
- **调色板**: 256色（768字节），DOS 6位转8位（值×4）
- **像素缓冲区**: 64000 字节

### 解析流程
```
load_ani_file()
  -> 读取文件到fileDatas
  -> AnalysisANI()
      -> 从偏移6开始读取uint32偏移量列表
      -> 验证每个AFM的frame_count有效性
      -> 存储有效AFM偏移量
  -> generate_ani_images()
      -> 对每个AFM调用AfmDecoder.decode_afm()
          -> 按命令逐帧解码
          -> 转换为GIF动画
```

---

## 图像数据格式

### makeFaceBMP/makeBgBMP/makeTAIBMP/makeFightBMP
用于人物表情、战斗背景、战斗动作等：
- **偏移0-1**: 宽度 (short)
- **偏移2-3**: 高度 (short)
- **偏移4+**: 压缩图像数据

### makeShapBMP
用于形状资源和图标：
- 无预定义宽度高度（固定尺寸）
- 数据格式同makeFaceBMP

### ANI动画（AfmDecoder）
ANI.DAT 使用命令驱动的 AfmDecoder 解码器，不再使用 makeANIBMP：
- **分辨率**: 固定 320×200
- **解码方式**: 命令驱动（见上方 ANI.DAT 章节）

---

## RLE压缩格式

图像数据使用改进的RLE压缩：

| 字节值范围 | 含义 |
|-----------|------|
| 0-63 | 单像素重复，绘制(值+1)次 |
| 64-127 | 连续绘制，绘制(值-64)次后x坐标+1 |
| 128-191 | 像素重复，下一个字节重复(值-128+1)次 |
| 192-255 | 跳过像素，跳过(值-192+1)个 |

---

## 文件依赖关系

```
FDFIELD.DAT 依赖 FDSHAP.DAT
  ├── FDFIELD地图数据使用FDSHAP的24x24图块拼贴
  └── 必须先解析FDSHAP.DAT生成shaps数组
```

---

## 解析入口函数

| DAT文件 | 加载函数 | 解析函数 | 图像生成函数 |
|---------|---------|---------|-------------|
| FDICON.B24 | load_fdicon_file() | AnalysisICON() | generate_icon_images() |
| FDTXT.DAT | load_fdtxt_file() | AnalysisTXT() | generate_fdtxt_files() |
| DATO.DAT | load_dato_file() | AnalysisDATO() | generate_dato_images() |
| BG.DAT | load_bg_file() | AnalysisBG() | generate_bg_images() |
| TAI.DAT | load_tai_file() | AnalysisTAI() | generate_tai_images() |
| FIGANI.DAT | load_figani_file() | AnalysisFIGANI() | generate_figani_images() |
| FDSHAP.DAT | load_fdshap_file() | AnalysisFDSHAP() | generate_fdshap_images() |
| FDFIELD.DAT | load_fdfield_file() | AnalysisFDFIELD() | generate_fdfield_images() |
| FDOTHER.DAT | load_fdother_file() | AnalysisOTHER() | generate_fdother_images() |
| ANI.DAT | load_ani_file() | AnalysisANI() | generate_ani_images() |
