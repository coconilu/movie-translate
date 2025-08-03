# 技术方案 - 电影翻译系统

## 1. 系统架构设计

### 1.1 整体架构 - Python全栈桌面应用
```
┌─────────────────────────────────────────────────────────────────┐
│                        桌面应用层 (Desktop App)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Python桌面应用 (CustomTkinter/PySide6)               │   │
│  │  • 主界面组件                                        │   │
│  │  • 文件拖拽上传                                        │   │
│  │  • 实时进度显示                                        │   │
│  │  • 角色管理界面                                        │   │
│  │  • 设置管理界面                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        本地服务层 (Local Service)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  FastAPI本地服务器                                      │   │
│  │  • RESTful API (本地通信)                              │   │
│  │  • WebSocket实时通信                                    │   │
│  │  • 任务队列管理                                        │   │
│  │  • 进度状态同步                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        业务逻辑层 (Service)                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  核心服务模块                                           │   │
│  │  • 视频处理服务                                        │   │
│  │  • 语音识别服务                                        │   │
│  │  • 翻译服务                                            │   │
│  │  • 角色识别服务                                        │   │
│  │  • 声音克隆服务                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据存储层 (Local Storage)                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  本地存储                                               │   │
│  │  • SQLite (关系数据)                                   │   │
│  │  • 文件系统缓存                                        │   │
│  │  • 本地模型存储                                        │   │
│  │  • 配置文件管理                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        外部服务层 (External)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  第三方API                                             │   │
│  │  • 语音识别API (SenseVoice, 百度语音)                 │   │
│  │  • 翻译API (DeepSeek, GLM-4.5)                        │   │
│  │  • 声音克隆API (本地模型)                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 本地服务架构
```
┌─────────────────────────────────────────────────────────────────┐
│                    桌面应用主进程                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Main Application (CustomTkinter/PySide6)               │   │
│  │  • UI事件处理                                          │   │
│  │  • 本地API调用                                         │   │
│  │  • 实时状态更新                                        │   │
│  │  • 文件操作管理                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    本地FastAPI服务                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Local FastAPI Server                                  │   │
│  │  • 路由: /api/v1/*                                   │   │
│  │  • 本地任务队列                                       │   │
│  │  • 文件系统管理                                       │   │
│  │  • 进度状态同步                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Media Service  │ │  Audio Service  │ │  Translation    │
│                 │ │                 │ │  Service        │
│ • 视频处理      │ │ • 音频提取      │ │ • 文本翻译      │
│ • 格式转换      │ │ • 音频处理      │ │ • 多语言支持    │
│ • 元数据提取    │ │ • 质量检测      │ │ • 术语库管理    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
                    │           │           │
                    ▼           ▼           ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Character      │ │  Voice Clone    │ │  Cache Service  │
│  Service        │ │  Service        │ │                 │
│ • 角色识别      │ │ • 音色建模      │ │ • 本地文件缓存  │
│ • 性别识别      │ │ • 语音合成      │ │ • 断点续传      │
│ • 特征提取      │ │ • 质量优化      │ │ • 数据清理      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 2. 项目结构

### 2.1 目录结构 - Python桌面应用
```
movie-translate/
├── app/                        # 桌面应用主程序
│   ├── __init__.py
│   ├── main.py                 # 应用入口
│   ├── ui/                     # UI界面
│   │   ├── __init__.py
│   │   ├── main_window.py      # 主窗口
│   │   ├── components/         # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── file_upload.py    # 文件上传组件
│   │   │   ├── progress_panel.py # 进度面板
│   │   │   ├── step_navigator.py # 步骤导航器
│   │   │   ├── character_manager.py # 角色管理器
│   │   │   ├── settings_panel.py # 设置面板
│   │   │   └── cache_manager.py # 缓存管理器
│   │   ├── dialogs/           # 对话框
│   │   │   ├── __init__.py
│   │   │   ├── error_dialog.py    # 错误对话框
│   │   │   ├── progress_dialog.py # 进度对话框
│   │   │   └── settings_dialog.py # 设置对话框
│   │   ├── styles/            # 样式配置
│   │   │   ├── __init__.py
│   │   │   ├── themes.py         # 主题配置
│   │   │   └── fonts.py          # 字体配置
│   │   └── utils/             # UI工具
│   │       ├── __init__.py
│   │       ├── file_dialog.py    # 文件对话框
│   │       └── message_box.py    # 消息框
│   ├── services/               # 本地API客户端
│   │   ├── __init__.py
│   │   ├── api_client.py       # API客户端
│   │   ├── websocket_client.py # WebSocket客户端
│   │   └── event_handler.py    # 事件处理器
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── process.py          # 处理状态模型
│   │   ├── character.py        # 角色模型
│   │   ├── settings.py         # 设置模型
│   │   └── cache.py            # 缓存模型
│   └── utils/                  # 应用工具
│       ├── __init__.py
│       ├── config.py           # 配置管理
│       ├── file_utils.py       # 文件工具
│       └── system_utils.py     # 系统工具
│
├── backend/                     # 本地后端服务
│   ├── __init__.py
│   ├── main.py                 # FastAPI服务入口
│   ├── config.py               # 服务配置
│   ├── api/                    # API路由
│   │   ├── __init__.py
│   │   ├── v1/                 # API版本1
│   │   │   ├── __init__.py
│   │   │   ├── video.py        # 视频相关API
│   │   │   ├── audio.py        # 音频相关API
│   │   │   ├── translation.py  # 翻译相关API
│   │   │   ├── character.py    # 角色相关API
│   │   │   ├── voice.py        # 声音相关API
│   │   │   ├── process.py      # 处理流程API
│   │   │   ├── cache.py        # 缓存管理API
│   │   │   └── system.py       # 系统状态API
│   │   └── websocket/          # WebSocket路由
│   │       ├── __init__.py
│   │       └── events.py       # 事件处理
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── video_service.py
│   │   ├── audio_service.py
│   │   ├── translation_service.py
│   │   ├── character_service.py
│   │   ├── voice_service.py
│   │   ├── step_manager.py     # 步骤管理服务
│   │   ├── cache_manager.py    # 缓存管理服务
│   │   ├── interrupt_handler.py # 中断处理服务
│   │   └── process_orchestrator.py # 处理编排服务
│   ├── models/                 # 数据模型
│   │   ├── __init__.py
│   │   ├── video.py
│   │   ├── audio.py
│   │   ├── translation.py
│   │   ├── character.py
│   │   ├── process.py          # 处理流程模型
│   │   └── cache.py            # 缓存模型
│   ├── schemas/                # 数据模式
│   │   ├── __init__.py
│   │   ├── video.py
│   │   ├── audio.py
│   │   ├── translation.py
│   │   ├── character.py
│   │   ├── process.py
│   │   └── cache.py
│   ├── utils/                  # 工具函数
│   │   ├── __init__.py
│   │   ├── file_utils.py
│   │   ├── audio_utils.py
│   │   ├── video_utils.py
│   │   └── system_utils.py
│   ├── database/                # 数据库操作
│   │   ├── __init__.py
│   │   ├── connection.py       # 数据库连接
│   │   ├── migrations.py       # 数据库迁移
│   │   └── models.py           # 数据库模型
│   └── tests/                  # 测试文件
│       ├── __init__.py
│       ├── test_services/
│       └── test_api/
│
├── ml-services/                # 机器学习服务
│   ├── speech_recognition/     # 语音识别
│   │   ├── sense_voice/        # SenseVoice模型（本地）
│   │   └── baidu/              # 百度语音API
│   ├── translation/            # 翻译服务
│   │   ├── deepseek/           # DeepSeek模型
│   │   ├── glm/                # GLM模型
│   │   └── google/             # Google翻译
│   ├── voice_cloning/          # 声音克隆
│   │   ├── models/             # 声音克隆模型
│   │   ├── training/           # 模型训练
│   │   └── synthesis/          # 语音合成
│   └── character_analysis/     # 角色分析
│       ├── gender_detection/   # 性别检测
│       ├── voice_feature/      # 音色特征
│       └── clustering/         # 角色聚类
│
├── database/                   # 数据库相关
│   ├── migrations/             # 数据库迁移
│   ├── seeds/                  # 初始数据
│   └── schema.sql              # 数据库结构
│
├── storage/                    # 文件存储
│   ├── uploads/                # 上传文件
│   ├── cache/                  # 缓存文件
│   ├── models/                 # 模型文件
│   └── output/                 # 输出文件
│
├── config/                     # 配置文件
│   ├── development.py          # 开发环境配置
│   ├── production.py           # 生产环境配置
│   └── models.yaml             # 模型配置
│
├── docker/                     # Docker配置
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
│
├── docs/                       # 文档
│   ├── api/                    # API文档
│   ├── deployment/             # 部署文档
│   └── user_guide/             # 用户指南
│
├── scripts/                    # 脚本文件
│   ├── setup.py                # 安装脚本
│   ├── migrate.py              # 数据迁移脚本
│   └── backup.py               # 备份脚本
│
├── tests/                      # 测试
│   ├── unit/                   # 单元测试
│   ├── integration/            # 集成测试
│   └── e2e/                    # 端到端测试
│
├── .env.example               # 环境变量示例
├── .gitignore
├── README.md
└── docker-compose.yml
```

## 3. 技术选型

### 3.1 桌面应用技术栈
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **UI框架** | CustomTkinter / PySide6 | 现代化桌面UI框架，跨平台支持 |
| **备选方案** | PyQt6, Tkinter | 成熟稳定的桌面应用框架 |
| **图形渲染** | Canvas / QPainter | 高性能图形绘制 |
| **多线程** | threading / asyncio | 支持后台任务处理 |
| **文件拖拽** | tkinterdnd2 / PySide6拖拽 | 原生拖拽支持 |
| **系统托盘** | pystray | 系统托盘图标支持 |
| **打包工具** | PyInstaller / Nuitka | 将Python应用打包为可执行文件 |

### 3.2 本地服务技术栈
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **框架** | FastAPI | 高性能异步框架，自动生成API文档 |
| **ORM** | SQLAlchemy | 成熟的ORM，支持异步 |
| **数据库** | SQLite | 轻量级本地数据库，无需额外服务 |
| **文件存储** | 本地文件系统 | 简单可靠的文件存储 |
| **任务队列** | ThreadPoolExecutor | 本地任务队列管理 |
| **进程通信** | WebSocket / HTTP | 本地进程间通信 |
| **API文档** | OpenAPI 3.0 | 自动生成API文档 |
| **日志** | Loguru | 简单易用的日志库 |

### 3.3 机器学习技术栈
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **语音识别** | SenseVoice (阿里) | 中文优化，本地部署，5090显卡加速 |
| **翻译模型** | DeepSeek R1 | 高质量翻译，支持上下文 |
| **备选方案** | GLM-4.5 | 中文优化，专业术语 |
| **声音克隆** | XTTS, VITS | 开源声音克隆模型 |
| **角色识别** | PyAnnote, VoiceID | 说话人识别和聚类 |
| **音频处理** | librosa, pydub | 音频分析和处理 |
| **深度学习框架** | PyTorch | 灵活的深度学习框架 |
| **GPU加速** | CUDA + cuDNN | GPU加速计算 |

### 3.4 桌面应用开发工具
| 技术类别 | 选择 | 理由 |
|---------|------|------|
| **打包工具** | PyInstaller | 将Python应用打包为可执行文件 |
| **安装程序** | Inno Setup (Windows) | Windows安装程序制作 |
| **图标制作** | GIMP / Inkscape | 图标和资源文件制作 |
| **版本管理** | Git | 版本控制 |
| **代码质量** | Black, isort, flake8 | 代码格式化和质量检查 |
| **测试** | pytest, pytest-qt | 完整的测试框架 |
| **调试工具** | pdb, VS Code调试器 | 代码调试 |

## 4. 核心模块设计

### 4.1 步骤管理模块
```python
# step_manager.py
class StepManager:
    def __init__(self):
        self.steps = [
            Step(name="文件导入", handler="file_import"),
            Step(name="音频处理", handler="audio_process"),
            Step(name="语音识别", handler="speech_recognition"),
            Step(name="翻译处理", handler="translation"),
            Step(name="角色识别", handler="character_recognition"),
            Step(name="配音生成", handler="voice_synthesis")
        ]
        self.current_step = 0
        self.step_states = {}
    
    async def execute_step(self, step_id: int, context: ProcessContext) -> StepResult:
        """执行指定步骤"""
        step = self.steps[step_id]
        handler = self.get_handler(step.handler)
        
        # 检查缓存
        cache_result = await self.cache_manager.get_step_cache(step_id, context)
        if cache_result:
            return cache_result
        
        # 执行步骤
        result = await handler.execute(context)
        
        # 保存缓存
        await self.cache_manager.save_step_cache(step_id, context, result)
        
        return result
    
    async def pause_step(self, step_id: int) -> bool:
        """暂停指定步骤"""
        # 实现暂停逻辑
        pass
    
    async def resume_step(self, step_id: int) -> bool:
        """恢复指定步骤"""
        # 实现恢复逻辑
        pass
    
    async def interrupt_step(self, step_id: int, save_progress: bool = True) -> bool:
        """中断指定步骤"""
        # 实现中断逻辑
        pass
```

### 4.2 缓存管理模块
```python
# cache_manager.py
class CacheManager:
    def __init__(self):
        self.cache_dir = "cache/"
        self.step_cache = {}
    
    async def save_step_cache(self, step_id: int, context: ProcessContext, result: StepResult):
        """保存步骤缓存"""
        cache_key = self._generate_cache_key(step_id, context)
        cache_path = os.path.join(self.cache_dir, f"step_{step_id}_{cache_key}")
        
        # 保存结果到缓存
        await self._save_to_cache(cache_path, result)
        
        # 更新缓存索引
        self.step_cache[cache_key] = {
            "step_id": step_id,
            "context": context,
            "cache_path": cache_path,
            "created_at": datetime.now(),
            "size": os.path.getsize(cache_path)
        }
    
    async def get_step_cache(self, step_id: int, context: ProcessContext) -> Optional[StepResult]:
        """获取步骤缓存"""
        cache_key = self._generate_cache_key(step_id, context)
        
        if cache_key in self.step_cache:
            cache_info = self.step_cache[cache_key]
            return await self._load_from_cache(cache_info["cache_path"])
        
        return None
    
    async def clear_step_cache(self, step_id: int, context: ProcessContext):
        """清理步骤缓存"""
        cache_key = self._generate_cache_key(step_id, context)
        
        if cache_key in self.step_cache:
            cache_info = self.step_cache[cache_key]
            os.remove(cache_info["cache_path"])
            del self.step_cache[cache_key]
    
    def get_cache_status(self) -> Dict[str, Any]:
        """获取缓存状态"""
        total_size = sum(info["size"] for info in self.step_cache.values())
        return {
            "total_steps": len(self.step_cache),
            "total_size": total_size,
            "cache_dir": self.cache_dir,
            "steps": list(self.step_cache.values())
        }
```

### 4.3 中断处理模块
```python
# interrupt_handler.py
class InterruptHandler:
    def __init__(self):
        self.interrupt_signals = {}
    
    async def handle_interrupt(self, step_id: int, interrupt_type: str, save_progress: bool = True):
        """处理中断信号"""
        if interrupt_type == "pause":
            await self._handle_pause(step_id)
        elif interrupt_type == "stop":
            await self._handle_stop(step_id, save_progress)
        elif interrupt_type == "skip":
            await self._handle_skip(step_id)
    
    async def _handle_pause(self, step_id: int):
        """处理暂停"""
        # 通知步骤暂停
        await self._notify_step_pause(step_id)
        
        # 保存当前状态
        await self._save_step_state(step_id, "paused")
    
    async def _handle_stop(self, step_id: int, save_progress: bool):
        """处理停止"""
        if save_progress:
            # 保存进度
            await self._save_step_progress(step_id)
        
        # 通知步骤停止
        await self._notify_step_stop(step_id)
        
        # 更新状态
        await self._save_step_state(step_id, "stopped")
    
    async def _handle_skip(self, step_id: int):
        """处理跳过"""
        # 通知步骤跳过
        await self._notify_step_skip(step_id)
        
        # 更新状态
        await self._save_step_state(step_id, "skipped")
    
    async def resume_from_interrupt(self, step_id: int) -> bool:
        """从中断恢复"""
        current_state = await self._get_step_state(step_id)
        
        if current_state in ["paused", "stopped"]:
            await self._notify_step_resume(step_id)
            await self._save_step_state(step_id, "running")
            return True
        
        return False
```

### 4.4 视频处理模块
```python
# video_service.py
class MediaService:
    def __init__(self):
        self.ffmpeg = FFmpeg()
        self.storage = FileStorage()
        self.cache_manager = CacheManager()
    
    async def process_media(self, file_path: str) -> MediaInfo:
        """处理媒体文件"""
        # 1. 识别文件类型（视频/音频）
        # 2. 验证文件格式
        # 3. 提取元数据
        # 4. 生成缩略图（仅视频）
        # 5. 转换格式（如果需要）
        # 6. 保存到存储
        pass
    
    async def extract_audio(self, video_path: str) -> str:
        """提取音频（仅视频文件）"""
        # 使用FFmpeg提取音频
        pass
    
    async def process_audio(self, audio_path: str) -> AudioInfo:
        """处理音频文件"""
        # 1. 验证音频格式
        # 2. 提取音频元数据
        # 3. 格式转换（如果需要）
        # 4. 质量检测
        pass
    
    async def generate_thumbnails(self, video_path: str) -> List[str]:
        """生成缩略图（仅视频文件）"""
        pass
```

### 4.2 语音识别模块
```python
# speech_recognition_service.py
class SpeechRecognitionService:
    def __init__(self):
        self.models = {
            'sense_voice': SenseVoiceModel(),  # 本地模型
            'baidu': BaiduSpeechService()     # 云端API
        }
    
    async def transcribe(self, audio_path: str, model: str = 'sense_voice') -> SRTResult:
        """语音识别转字幕"""
        # 1. 选择模型
        # 2. 预处理音频
        # 3. 执行识别
        # 4. 生成SRT格式
        # 5. 保存结果
        pass
    
    async def detect_language(self, audio_path: str) -> str:
        """检测语言"""
        pass
```

### 4.3 翻译模块
```python
# translation_service.py
class TranslationService:
    def __init__(self):
        self.models = {
            'deepseek': DeepSeekModel(),
            'glm': GLMModel()
        }
        self.cache_manager = TranslationCacheManager()
        self.srt_processor = SRTProcessor()
    
    async def translate_srt(self, srt_path: str, target_lang: str = 'zh') -> str:
        """翻译SRT文件 - 本地预处理+线上翻译方案"""
        # 1. 解析SRT文件
        srt_data = await self.srt_processor.parse_srt(srt_path)
        
        # 2. 文本预处理
        processed_text = await self.srt_processor.preprocess_text(srt_data)
        
        # 3. 检查翻译缓存
        cached_result = await self.cache_manager.get_cached_translation(
            processed_text, target_lang
        )
        if cached_result:
            return cached_result
        
        # 4. 批量翻译处理
        translated_chunks = await self._batch_translate(
            processed_text, target_lang
        )
        
        # 5. 重新组装SRT格式
        result_srt = await self.srt_processor.assemble_srt(
            srt_data, translated_chunks
        )
        
        # 6. 保存翻译缓存
        await self.cache_manager.save_translation(
            processed_text, translated_chunks, target_lang
        )
        
        return result_srt
    
    async def _batch_translate(self, text_chunks: List[str], target_lang: str) -> List[str]:
        """批量翻译文本块"""
        # 1. 智能分段（考虑上下文连贯性）
        chunks = self._smart_chunking(text_chunks)
        
        # 2. 并发翻译控制
        tasks = []
        for chunk in chunks:
            task = self._translate_chunk(chunk, target_lang)
            tasks.append(task)
        
        # 3. 执行翻译（控制并发数）
        results = await self._concurrent_translate(tasks)
        
        return results
    
    async def _translate_chunk(self, chunk: str, target_lang: str) -> str:
        """翻译单个文本块"""
        # 1. 选择最优模型
        model = self._select_optimal_model(chunk, target_lang)
        
        # 2. 执行翻译
        result = await model.translate(chunk, target_lang)
        
        # 3. 后处理优化
        return self._post_process_translation(result)
    
    def resume_translation(self, srt_path: str, checkpoint_path: str) -> str:
        """断点续传翻译"""
        # 从检查点恢复翻译进度
        pass
```

### 4.4 SRT预处理模块
```python
# srt_processor.py
class SRTProcessor:
    def __init__(self):
        self.max_chunk_size = 2000  # 单次翻译最大字符数
        self.context_window = 3     # 上下文窗口大小
    
    async def parse_srt(self, srt_path: str) -> List[SRTEntry]:
        """解析SRT文件"""
        entries = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析SRT格式
        blocks = content.split('\n\n')
        for block in blocks:
            if block.strip():
                entry = self._parse_srt_block(block)
                entries.append(entry)
        
        return entries
    
    async def preprocess_text(self, srt_data: List[SRTEntry]) -> List[TextChunk]:
        """文本预处理"""
        # 1. 提取纯文本
        texts = [entry.text for entry in srt_data]
        
        # 2. 去重处理
        unique_texts = self._remove_duplicates(texts)
        
        # 3. 智能分段
        chunks = self._smart_chunking(unique_texts)
        
        # 4. 添加上下文信息
        enriched_chunks = self._add_context(chunks, srt_data)
        
        return enriched_chunks
    
    def _smart_chunking(self, texts: List[str]) -> List[TextChunk]:
        """智能分段"""
        chunks = []
        current_chunk = ""
        
        for text in texts:
            # 考虑句子完整性
            if len(current_chunk + text) <= self.max_chunk_size:
                current_chunk += text + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = text + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def assemble_srt(self, original_data: List[SRTEntry], 
                          translated_chunks: List[str]) -> str:
        """重新组装SRT格式"""
        # 将翻译结果映射回原始SRT结构
        result = []
        
        for i, entry in enumerate(original_data):
            translated_text = self._map_translation(entry.text, translated_chunks)
            srt_block = self._format_srt_entry(
                entry.index, entry.start_time, entry.end_time, translated_text
            )
            result.append(srt_block)
        
        return '\n\n'.join(result)
```

### 4.5 翻译缓存管理模块
```python
# translation_cache_manager.py
class TranslationCacheManager:
    def __init__(self):
        self.cache_db = TranslationCacheDB()
        self.hash_generator = TextHashGenerator()
    
    async def get_cached_translation(self, text_hash: str, target_lang: str) -> Optional[str]:
        """获取缓存的翻译结果"""
        cache_key = f"{text_hash}_{target_lang}"
        return await self.cache_db.get_cache(cache_key)
    
    async def save_translation(self, original_hash: str, translated_text: str, 
                            target_lang: str, metadata: Dict = None):
        """保存翻译缓存"""
        cache_key = f"{original_hash}_{target_lang}"
        cache_data = {
            'original_hash': original_hash,
            'translated_text': translated_text,
            'target_lang': target_lang,
            'created_at': datetime.now(),
            'metadata': metadata or {}
        }
        await self.cache_db.save_cache(cache_key, cache_data)
    
    async def create_checkpoint(self, srt_path: str, progress: Dict):
        """创建翻译检查点"""
        checkpoint_data = {
            'srt_path': srt_path,
            'progress': progress,
            'timestamp': datetime.now(),
            'translated_chunks': progress.get('translated_chunks', []),
            'current_position': progress.get('current_position', 0)
        }
        await self.cache_db.save_checkpoint(srt_path, checkpoint_data)
    
    async def load_checkpoint(self, srt_path: str) -> Optional[Dict]:
        """加载翻译检查点"""
        return await self.cache_db.get_checkpoint(srt_path)
    
    def generate_text_hash(self, text: str) -> str:
        """生成文本哈希值"""
        return self.hash_generator.generate_hash(text)
```

### 4.4 角色识别模块
```python
# character_service.py
class CharacterService:
    def __init__(self):
        self.voice_analyzer = VoiceAnalyzer()
        self.gender_detector = GenderDetector()
        self.clustering = VoiceClustering()
    
    async def identify_characters(self, audio_path: str, srt_path: str) -> List[Character]:
        """识别角色"""
        # 1. 音频分段
        # 2. 特征提取
        # 3. 聚类分析
        # 4. 性别识别
        # 5. 角色分类
        pass
    
    async def extract_voice_features(self, audio_segment: str) -> VoiceFeatures:
        """提取音色特征"""
        pass
```

### 4.6 翻译缓存数据库设计
```sql
-- 翻译缓存表
CREATE TABLE translation_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text_hash VARCHAR(64) NOT NULL,
    original_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_lang VARCHAR(10) NOT NULL,
    target_lang VARCHAR(10) NOT NULL,
    model_used VARCHAR(50),
    quality_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    UNIQUE(text_hash, source_lang, target_lang)
);

-- 翻译检查点表
CREATE TABLE translation_checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    srt_path VARCHAR(500) NOT NULL,
    progress_data TEXT NOT NULL,  -- JSON格式
    current_position INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    translated_chunks TEXT,         -- JSON格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(srt_path)
);

-- 翻译任务表
CREATE TABLE translation_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(64) UNIQUE NOT NULL,
    srt_path VARCHAR(500) NOT NULL,
    source_lang VARCHAR(10) NOT NULL,
    target_lang VARCHAR(10) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 4.7 声音克隆模块
```python
# voice_cloning_service.py
class VoiceCloningService:
    def __init__(self):
        self.models = {
            'xtts': XTTSModel(),
            'vits': VITSModel()
        }
        self.trainer = ModelTrainer()
    
    async def clone_voice(self, character_id: str, audio_samples: List[str]) -> str:
        """克隆声音"""
        # 1. 数据预处理
        # 2. 模型训练
        # 3. 质量评估
        # 4. 保存模型
        pass
    
    async def synthesize(self, text: str, character_id: str) -> str:
        """语音合成"""
        # 1. 加载模型
        # 2. 文本预处理
        # 3. 语音合成
        # 4. 后处理
        pass
```

## 5. 数据库设计

### 5.1 核心表结构 (SQLite)
```sql
-- 媒体文件表
CREATE TABLE media_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    original_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(20) NOT NULL, -- 'video' or 'audio'
    duration INTEGER, -- 秒
    resolution VARCHAR(50), -- 视频分辨率
    sample_rate INTEGER, -- 音频采样率
    channels INTEGER, -- 音频声道数
    file_size INTEGER,
    format VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 音频轨道表（仅视频文件使用）
CREATE TABLE audio_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media_files(id),
    file_path VARCHAR(500) NOT NULL,
    duration INTEGER,
    sample_rate INTEGER,
    channels INTEGER,
    format VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 字幕表
CREATE TABLE subtitles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media_files(id),
    language VARCHAR(10) NOT NULL,
    content TEXT NOT NULL, -- SRT格式
    source_type VARCHAR(20), -- 'original' or 'translated'
    model_used VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色表
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    media_id INTEGER REFERENCES media_files(id),
    name VARCHAR(100),
    gender VARCHAR(10),
    character_type VARCHAR(20),
    total_duration INTEGER, -- 秒
    appearance_count INTEGER DEFAULT 0,
    voice_features TEXT, -- JSON格式存储音色特征
    model_path VARCHAR(500), -- 声音克隆模型路径
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色对话表
CREATE TABLE character_dialogues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER REFERENCES characters(id),
    subtitle_id INTEGER REFERENCES subtitles(id),
    start_time REAL NOT NULL,
    end_time REAL NOT NULL,
    confidence REAL,
    audio_segment_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 任务队列表
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type VARCHAR(50) NOT NULL,
    media_id INTEGER REFERENCES media_files(id),
    status VARCHAR(20) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 缓存表
CREATE TABLE cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT NOT NULL,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE system_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 索引设计
```sql
-- 性能优化索引
CREATE INDEX idx_media_files_status ON media_files(status);
CREATE INDEX idx_media_files_created_at ON media_files(created_at);
CREATE INDEX idx_media_files_type ON media_files(file_type);
CREATE INDEX idx_subtitles_media_language ON subtitles(media_id, language);
CREATE INDEX idx_characters_media ON characters(media_id);
CREATE INDEX idx_character_dialogues_character ON character_dialogues(character_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_media ON tasks(media_id);
CREATE INDEX idx_cache_key_expires ON cache(cache_key, expires_at);
```

## 6. API设计

### 6.1 RESTful API结构
```python
# 主要API端点
POST   /api/v1/media/upload               # 上传媒体文件
GET    /api/v1/media/{id}                 # 获取媒体文件信息
GET    /api/v1/media                      # 获取媒体文件列表
DELETE /api/v1/media/{id}                # 删除媒体文件

POST   /api/v1/media/{id}/process        # 开始处理
GET    /api/v1/media/{id}/status         # 获取处理状态
POST   /api/v1/media/{id}/pause          # 暂停处理
POST   /api/v1/media/{id}/resume         # 恢复处理
POST   /api/v1/media/{id}/cancel         # 取消处理

GET    /api/v1/media/{id}/audio          # 获取音频信息
GET    /api/v1/media/{id}/subtitles      # 获取字幕
POST   /api/v1/media/{id}/subtitles      # 上传字幕

GET    /api/v1/media/{id}/characters     # 获取角色列表
GET    /api/v1/characters/{id}            # 获取角色详情
POST   /api/v1/characters/{id}/clone      # 克隆声音
POST   /api/v1/characters/{id}/synthesize # 语音合成

GET    /api/v1/models/speech-recognition  # 获取语音识别模型
GET    /api/v1/models/translation        # 获取翻译模型
POST   /api/v1/models/test               # 测试模型连接

GET    /api/v1/settings                   # 获取设置
POST   /api/v1/settings                   # 更新设置
GET    /api/v1/system/status              # 获取系统状态
```

### 6.2 WebSocket事件
```python
# 实时通信事件
@websocket.on('connect')
async def handle_connect(websocket):
    """客户端连接"""
    pass

@websocket.on('video_progress')
async def handle_video_progress(websocket, data):
    """视频处理进度"""
    await websocket.send_json({
        'type': 'progress',
        'video_id': data['video_id'],
        'progress': data['progress'],
        'current_step': data['current_step']
    })

@websocket.on('character_update')
async def handle_character_update(websocket, data):
    """角色识别更新"""
    await websocket.send_json({
        'type': 'character_update',
        'video_id': data['video_id'],
        'characters': data['characters']
    })
```

## 7. 部署方案

### 7.1 桌面应用打包方案
```python
# build.py - 桌面应用打包脚本
import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_desktop_app():
    """构建桌面应用"""
    print("开始构建桌面应用...")
    
    # 1. 安装依赖
    print("安装Python依赖...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 2. 下载模型文件
    print("下载模型文件...")
    subprocess.run([sys.executable, "scripts/download_models.py"])
    
    # 3. 初始化数据库
    print("初始化数据库...")
    subprocess.run([sys.executable, "scripts/setup_db.py"])
    
    # 4. 使用PyInstaller打包
    print("打包应用...")
    cmd = [
        "pyinstaller",
        "--name=MovieTranslator",
        "--windowed",
        "--onefile",
        "--add-data=data;data",
        "--add-data=resources;resources",
        "--icon=resources/icons/app.ico",
        "--hidden-import=pydub",
        "--hidden-import=librosa",
        "--hidden-import=sense_voice",
        "app/main.py"
    ]
    subprocess.run(cmd)
    
    # 5. 创建安装程序
    print("创建安装程序...")
    create_installer()
    
    print("构建完成!")

def create_installer():
    """创建安装程序 (Inno Setup)"""
    # 生成Inno Setup脚本
    iss_content = """
[Setup]
AppName=Movie Translator
AppVersion=1.0
DefaultDirName={pf}\\Movie Translator
DefaultGroupName=Movie Translator
OutputDir=dist
OutputBaseFilename=MovieTranslator-Setup

[Files]
Source: "dist\\MovieTranslator.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "data\\*"; DestDir: "{app}\\data"; Flags: ignoreversion recursesubdirs
Source: "resources\\*"; DestDir: "{app}\\resources"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\\Movie Translator"; Filename: "{app}\\MovieTranslator.exe"
Name: "{commondesktop}\\Movie Translator"; Filename: "{app}\\MovieTranslator.exe"

[Run]
Filename: "{app}\\MovieTranslator.exe"; Description: "{cm:LaunchProgram,Movie Translator}"; Flags: nowait postinstall skipifsilent
"""
    
    with open("build/setup.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)
    
    # 编译安装程序
    subprocess.run(["iscc", "build/setup.iss"])

if __name__ == "__main__":
    build_desktop_app()
```

### 7.2 应用启动脚本
```python
# run.py - 应用启动脚本
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

def start_backend_server():
    """启动后端服务"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # 启动FastAPI服务器
    cmd = [sys.executable, "main.py", "--host", "127.0.0.1", "--port", "8000"]
    subprocess.run(cmd)

def start_desktop_app():
    """启动桌面应用"""
    app_dir = Path(__file__).parent / "app"
    os.chdir(app_dir)
    
    # 启动桌面应用
    cmd = [sys.executable, "main.py"]
    subprocess.run(cmd)

def main():
    """主函数"""
    print("启动电影翻译系统...")
    
    # 启动后端服务（在单独线程中）
    backend_thread = threading.Thread(target=start_backend_server)
    backend_thread.daemon = True
    backend_thread.start()
    
    # 等待后端服务启动
    time.sleep(3)
    
    # 启动桌面应用
    start_desktop_app()

if __name__ == "__main__":
    main()
```

### 7.3 系统要求检查脚本
```python
# scripts/check_system.py
import platform
import psutil
import GPUtil
import sys

def check_system_requirements():
    """检查系统要求"""
    print("检查系统要求...")
    
    # 操作系统
    print(f"操作系统: {platform.system()} {platform.release()}")
    
    # CPU
    cpu_count = psutil.cpu_count()
    print(f"CPU核心数: {cpu_count}")
    if cpu_count < 4:
        print("警告: CPU核心数建议4核以上")
    
    # 内存
    memory = psutil.virtual_memory()
    print(f"内存: {memory.total // (1024**3)}GB")
    if memory.total < 8 * 1024**3:
        print("警告: 内存建议8GB以上")
    
    # GPU
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            print(f"GPU: {gpu.name} ({gpu.memoryTotal}MB)")
        else:
            print("警告: 未检测到GPU，将使用CPU处理（速度较慢）")
    except:
        print("警告: 无法检测GPU信息")
    
    # 磁盘空间
    disk = psutil.disk_usage('/')
    free_space_gb = disk.free // (1024**3)
    print(f"可用磁盘空间: {free_space_gb}GB")
    if free_space_gb < 20:
        print("警告: 可用磁盘空间建议20GB以上")
    
    print("系统要求检查完成!")

if __name__ == "__main__":
    check_system_requirements()
```

## 8. 性能优化策略

### 8.1 数据库优化
- **索引优化**：为常用查询创建合适的索引
- **查询优化**：使用EXPLAIN分析查询性能
- **连接池**：使用数据库连接池减少连接开销
- **读写分离**：主从复制，读写分离
- **分库分表**：大数据量时的水平分片

### 8.2 缓存策略
- **多级缓存**：Redis + 本地缓存
- **缓存预热**：启动时加载热点数据
- **缓存更新**：采用合适的缓存更新策略
- **缓存淘汰**：LRU算法，设置合理的过期时间

### 8.3 异步处理
- **消息队列**：使用Celery处理耗时任务
- **异步IO**：使用async/await提高性能
- **批处理**：批量处理减少IO开销
- **流式处理**：大文件流式处理
- **串行处理**：一次只处理一个文件，确保系统稳定性

### 8.4 SenseVoice本地部署优化
- **GPU加速**：充分利用5090显卡的24GB显存
- **模型优化**：使用TensorRT加速推理，FP16精度
- **批处理**：支持多音频片段并行处理
- **显存管理**：模型预加载，避免重复加载开销
- **缓存机制**：相似音频复用识别结果

### 8.5 资源优化
- **内存管理**：及时释放不再使用的资源
- **GPU优化**：合理使用GPU加速
- **文件清理**：定期清理临时文件
- **监控告警**：实时监控系统资源使用情况

### 8.6 百度语音API集成优化
- **智能切换**：本地处理失败时自动切换百度API
- **限流控制**：合理控制API调用频率，避免超额
- **成本监控**：实时统计API调用成本
- **容错机制**：网络异常时的重试和降级策略
- **质量评估**：对比本地和云端识别质量，动态选择

### 8.7 翻译性能优化策略
- **智能分段**：基于语义完整性进行文本分段，保持上下文连贯性
- **并发控制**：合理控制并发翻译请求数，避免API限流
- **缓存命中**：哈希比对快速识别重复内容，减少重复翻译
- **断点续传**：定期保存翻译进度，支持大文件中断恢复
- **增量翻译**：仅翻译新增或修改的内容，提高效率
- **批处理优化**：将小文本块合并处理，减少API调用次数
- **内存管理**：流式处理大文件，避免内存溢出

## 9. 安全考虑

### 9.1 数据安全
- **输入验证**：严格验证用户输入
- **SQL注入**：使用参数化查询
- **文件上传**：限制文件类型和大小
- **数据加密**：敏感数据加密存储

### 9.2 访问控制
- **身份认证**：JWT令牌认证
- **权限控制**：基于角色的访问控制
- **API限流**：防止API滥用
- **CORS配置**：合理的跨域策略

### 9.3 系统安全
- **容器安全**：最小权限原则
- **网络安全**：防火墙配置
- **日志审计**：完整的操作日志
- **漏洞扫描**：定期安全扫描

## 10. 监控和运维

### 10.1 监控指标
- **系统指标**：CPU、内存、磁盘、网络
- **应用指标**：API响应时间、错误率、处理队列长度
- **业务指标**：处理任务数、成功率、平均处理时间
- **自定义指标**：模型准确率、资源使用率

### 10.2 日志管理
- **结构化日志**：JSON格式的结构化日志
- **日志级别**：DEBUG、INFO、WARNING、ERROR
- **日志聚合**：集中化日志收集和分析
- **日志轮转**：定期归档和清理

### 10.3 告警机制
- **阈值告警**：基于指标阈值的告警
- **异常检测**：基于机器学习的异常检测
- **告警通知**：邮件、短信、企业微信等多渠道通知
- **故障自愈**：自动化的故障恢复机制