# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

这是一个基于 Python 构建的 AI 驱动电影翻译和配音系统。系统自动处理视频文件：
1. 提取音频并执行语音识别
2. 将字幕翻译成中文
3. 识别不同的角色/声音
4. 克隆声音并生成中文配音
5. 将配音音频合成回原始视频

## 开发环境

- **编程语言**: Python 3.10+
- **包管理器**: UV (现代 Python 包管理器)
- **主要 UI 框架**: CustomTkinter / PySide6 用于桌面 GUI
- **后端服务**: FastAPI 用于本地 API 服务器
- **数据库**: SQLite 用于本地数据存储
- **机器学习**: PyTorch 及各种 AI 模型

## 主要依赖

### 核心框架
- `customtkinter>=5.2.0` - 现代桌面 GUI 框架
- `pyside6>=6.5.0` - 备选 UI 框架
- `fastapi>=0.100.0` - 本地 API 服务器
- `uvicorn>=0.23.0` - FastAPI 的 ASGI 服务器

### AI/ML 库
- `torch>=2.0.0` - 深度学习框架
- `transformers>=4.30.0` - Hugging Face 模型
- `openai>=1.0.0` - OpenAI API 集成
- `ffmpeg-python>=0.2.0` - 视频/音频处理

### 音频处理
- `pydub>=0.25.1` - 音频操作
- `soundfile>=0.12.0` - 音频文件 I/O
- `pyttsx3>=2.90` - 文本转语音

### 数据与存储
- `sqlalchemy>=2.0.0` - 数据库 ORM
- `alembic>=1.11.0` - 数据库迁移
- `redis>=4.6.0` - 缓存层
- `celery>=5.3.0` - 任务队列

### 开发工具
- `pytest>=7.4.0` - 测试框架
- `black>=23.0.0` - 代码格式化
- `flake8>=6.0.0` - 代码检查
- `mypy>=1.5.0` - 类型检查

## 常用命令

### 运行应用程序
```bash
# 运行主应用程序
python main.py

# 使用 UV 安装依赖
uv sync

# 使用 UV 运行
uv run python main.py
```

### 开发
```bash
# 运行测试
pytest

# 运行覆盖率测试
pytest --cov=.

# 格式化代码
black .

# 检查代码
flake8 .

# 类型检查
mypy .
```

### 包管理
```bash
# 添加新依赖
uv add <package-name>

# 移除依赖
uv remove <package-name>

# 更新依赖
uv sync --upgrade
```

## 架构概述

系统采用分层架构：

1. **桌面应用层** (CustomTkinter/PySide6)
   - 带文件拖放的主界面
   - 实时进度显示
   - 角色管理界面
   - 设置和配置

2. **本地服务层** (FastAPI)
   - 内部通信的 RESTful API
   - 实时更新的 WebSocket
   - 任务队列管理
   - 进度同步

3. **业务逻辑层**
   - 视频处理服务
   - 语音识别 (SenseVoice 本地 / 百度云端)
   - 翻译服务 (DeepSeek R1 / GLM-4.5)
   - 角色识别
   - 声音克隆 (F5-TTS 本地 / MiniMax 云端)

4. **数据存储层**
   - SQLite 用于结构化数据
   - 文件系统缓存用于中间结果
   - Redis 用于会话管理

## 处理流程

主要处理流程包含 6 个步骤：
1. **文件导入** - 视频/音频文件验证和准备
2. **音频处理** - 从视频中提取音频，格式转换
3. **语音识别** - 生成原始语言字幕
4. **翻译** - 将字幕转换为中文
5. **角色识别** - 识别不同的说话者和声音特征
6. **声音克隆与配音** - 使用克隆的声音生成中文音频

## 核心功能

### 用户体验
- 拖放文件上传
- 实时进度跟踪和步骤可视化
- 带中断/恢复功能的缓存管理
- 带声音预览的角色管理
- 灵活的错误处理和恢复

### 技术特性
- 混合处理 (本地模型 + 云端 API)
- 步骤级缓存以实现高效中断恢复
- 多格式支持 (MP4, AVI, MKV, MP3, WAV 等)
- 本地模型的 GPU 加速
- 自动质量评估

## 配置

### 模型选择
- **语音识别**: SenseVoice (本地) 或 百度语音 (云端)
- **翻译**: DeepSeek R1 (主要) 或 GLM-4.5 (备选)
- **声音克隆**: F5-TTS (本地) 或 MiniMax Audio (云端)

### API 集成
系统集成多个云端服务：
- 百度语音 API
- DeepSeek R1 API
- GLM-4.5 API
- MiniMax Audio API

API 密钥和配置通过设置界面进行管理。

## 开发注意事项

- 项目使用 UV 作为包管理器而非 pip
- 主入口点是 `main.py`
- 系统设计为使用本地模型离线工作
- 云端 API 用作后备或增强质量
- 缓存对性能和用户体验至关重要
- UI 采用桌面优先的设计原则