# Movie Translate

<div align="center">

**Movie Translate** - AI驱动的视频翻译与配音工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-username/movie-translate)

</div>

## 🎬 项目简介

Movie Translate 是一个基于人工智能的视频翻译和配音工具，支持多种语言的视频内容翻译和语音合成。

### ✨ 核心功能

- **多格式支持** - 支持MP4、AVI、MKV等主流视频格式
- **语音识别** - 高精度的语音转文字功能
- **智能翻译** - 支持多种语言间的翻译
- **角色识别** - 自动识别不同角色声音
- **语音合成** - 高质量的语音克隆和合成
- **视频合成** - 自动合成翻译后的音视频
- **批量处理** - 支持多个视频文件批量处理
- **图形界面** - 基于CustomTkinter的现代化界面

## 🖥️ 系统要求

### 基本要求

- **Python**: 3.8+
- **操作系统**: Windows 10/11, macOS 10.14+, Linux
- **内存**: 推荐8GB以上

- **存储**: 推荐20GB可用空间
（用于模型文件和缓存）

### 推荐配置

- **GPU**: 支持CUDA的NVIDIA显卡（可选，用于加速处理）
- **内存**: 16GB以上
- **存储**: SSD固态硬盘

## 🚀 安装指南

### 1. 克隆项目

```bash
git clone https://github.com/your-username/movie-translate.git
cd movie-translate
```

### 2. 安装 uv 并创建虚拟环境

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或使用 pip 安装
pip install uv

# 创建虚拟环境
uv venv
# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
# 安装项目依赖
uv pip install -r requirements.txt

# (可选) 安装开发依赖
uv pip install -r requirements-dev.txt
```

### 4. 配置API密钥

```bash
# 复制配置模板
cp config.example.json config.json

# 编辑config.json文件，添加您的API密钥
{
  "api_keys": {
    "baidu_speech_app_id": "your_baidu_app_id",
    "baidu_speech_api_key": "your_baidu_api_key",
    "baidu_speech_secret_key": "your_baidu_secret_key",
    "deepseek_api_key": "your_deepseek_api_key",
    "minimax_api_key": "your_minimax_api_key",
    "minimax_group_id": "your_minimax_group_id"
  }
}
```

### 5. 启动应用

```bash
uv run python src/movie_translate/ui/main_app.py
```

## 🎯 使用流程

### 1. 文件导入

- **视频文件**: 支持拖拽和文件选择器导入
- **批量导入**: 可一次选择多个视频文件
- **格式验证**: 自动验证视频格式兼容性

### 2. 语言设置

- **源语言**: 自动检测或手动选择源语言
- **目标语言**: 选择翻译目标语言
- **方言支持**: 部分语言支持方言选择

### 3. 角色识别

- **自动识别**: 自动识别视频中的不同角色
- **手动调整**: 可手动调整角色分配
- **声音匹配**: 为每个角色匹配合适的声音

### 4. 处理步骤

#### 步骤1: 音频提取
- 提取视频中的音频轨道
- 保存为高质量WAV格式

#### 步骤2: 语音识别
- 使用SenseVoice进行语音转文字
- 生成带时间戳的字幕文件

#### 步骤3: 文字翻译
- 将识别的文字翻译为目标语言
- 使用DeepSeek、GLM或Google翻译

#### 步骤4: 语音合成
- 使用角色声音进行语音克隆
- 使用F5-TTS或MiniMax等模型

#### 步骤5: 视频合成
- 将翻译后的音频与视频合成
- 保持原有的时间同步

#### 步骤6: 导出结果
- 导出最终的视频文件
- 可选择不同质量和格式

### 5. 进度监控

- **实时进度**: 显示当前处理进度
- **日志记录**: 详细的处理日志
- **错误处理**: 智能错误处理和恢复

### 6. 结果查看

- **预览功能**: 预览处理结果（位于`output/`目录）
- **质量检查**: 检查翻译和配音质量
- **批量管理**: 管理批量处理的结果

## ⚙️ 配置说明

### 基础配置

```json
{
  "audio": {
    "sample_rate": 16000,
    "channels": 1,
    "format": "wav",
    "quality": "high"
  },
  "cache": {
    "enabled": true,
    "max_size_gb": 10.0,
    "cleanup_days": 7
  },
  "processing": {
    "max_retries": 3,
    "timeout_seconds": 300,
    "parallel_workers": 2
  }
}
```

### 服务配置

```json
{
  "service": {
    "speech_recognition": "sense_voice",
    "translation": "deepseek",
    "voice_clone": "f5_tts",
    "fallback_to_local": true
  }
}
```

## 🔧 高级功能

### 1. 批量处理

- 支持批量视频文件处理
- 统一的参数配置
- 并行处理优化

### 2. 断点续传

- 智能断点续传功能
- 处理中断后自动恢复
- 避免重复处理

### 3. 缓存管理

- 智能缓存系统
- 支持中间结果缓存
- 自动清理过期缓存

### 4. 性能优化

- GPU加速支持
- 多线程并行处理
- 内存使用优化

## 📁 项目结构

### 目录结构

```
movie-translate/
├── src/
│   └── movie_translate/
│       ├── core/              # 核心模块
│       │   ├── config.py      # 配置管理
│       │   ├── logger.py      # 日志系统
│       │   ├── cache_manager.py # 缓存管理
│       │   └── error_handler.py # 错误处理
│       ├── models/            # 数据模型
│       │   ├── database_models.py # 数据库模型
│       │   ├── schemas.py     # 数据模式
│       │   └── repositories.py # 数据仓库
│       ├── services/          # 业务服务
│       │   ├── audio_processing.py # 音频处理
│       │   ├── speech_recognition.py # 语音识别
│       │   ├── translation.py # 翻译服务
│       │   ├── character_identification.py # 角色识别
│       │   ├── voice_cloning.py # 语音克隆
│       │   └── video_synthesis.py # 视频合成
│       ├── ui/                # 用户界面
│       │   ├── main_app.py    # 主应用
│       │   ├── step_navigator.py # 步骤导航
│       │   ├── file_import.py # 文件导入
│       │   ├── character_manager.py # 角色管理
│       │   ├── settings_panel.py # 设置面板
│       │   ├── progress_display.py # 进度显示
│       │   └── recovery_dialog.py # 恢复对话框
│       └── api/               # API接口
│           ├── main.py        # FastAPI主程序
│           ├── endpoints/     # API端点
│           └── websocket.py   # WebSocket接口
├── tests/                     # 测试文件
├── resources/                 # 资源文件
├── output/                    # 输出文件
├── requirements.txt           # 依赖文件
├── config.example.json        # 配置模板
└── README.md                 # 说明文档
```

### 开发环境

1. **安装开发依赖**
```bash
uv pip install -r requirements-dev.txt
```

2. **运行测试**
```bash
pytest tests/
```

3. **代码格式化**
```bash
black src/
flake8 src/
mypy src/
```

### API文档

启动API服务后，可访问 `http://localhost:8000/docs` 查看API文档

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   - 检查config.json中的API密钥是否正确
   - 确认API密钥权限和配额

2. **内存不足**
   - 关闭其他程序释放内存
   - 增加虚拟内存设置
   - 减少并行处理数量

3. **处理超时**
   - 增加timeout设置
   - 检查网络连接
   - 优化处理参数

4. **视频格式不支持**
   - 使用FFmpeg转换视频格式
   - 确保视频文件完整

### 日志文件

- 应用日志: `~/.movie-translate/app.log`
- 错误日志: `~/.movie-translate/error_YYYYMMDD.log`
- 性能日志: `~/.movie-translate/performance_YYYYMMDD.log`

## 💡 性能优化

### 硬件优化

1. **推荐配置**
   - CPU: 多核处理器
   - 内存: 16GB以上
   - 存储: SSD固态硬盘

2. **可选配置**
   - 支持CUDA的NVIDIA显卡
   - 更多的内存和存储空间
   - 高性能网络连接

### 软件优化

1. **处理优化**
   - 调整batch_size参数
   - 使用GPU加速处理
   - 启用缓存: 6

2. **存储优化**
   - 定期清理缓存
   - 使用SSD存储
   - 优化数据库性能

## 🔒 安全说明

### 数据安全

- 请妥善保管API密钥
- 不要在公共网络分享敏感配置
- 定期更新依赖库以修复安全漏洞

### 隐私保护

- 处理的文件仅存储在本地
- 不会上传到外部服务器（API调用除外）
- 建议定期清理临时文件

## 🤝 贡献指南

### 如何贡献

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 代码规范

- 遵循PEP 8规范
- 编写清晰的注释
- 创建单元测试
- 保持代码整洁

## 📄 许可证

本项目采用MIT许可证，详情请参见[LICENSE](LICENSE)文件。

## 🙏 致谢

- **SenseVoice** - 语音识别服务
- **F5-TTS** - 语音合成服务
- **DeepSeek** - 翻译服务
- **MiniMax** - AI服务平台
- **CustomTkinter** - GUI框架

## 📞 联系方式

- **项目主页**: https://github.com/your-username/movie-translate
- **问题反馈**: https://github.com/your-username/movie-translate/issues
- **邮箱联系**: your-email@example.com

---

**Movie Translate** - 让视频翻译变得简单高效！🎬✨