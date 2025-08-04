# Movie Translate 快速开始指南

## 🚀 5分钟快速上手

### 第一步：环境准备

1. **确保Python环境**
   ```bash
   python --version  # 确保Python 3.8+
   ```

2. **安装uv并运行安装脚本**
   ```bash
   # 安装 uv
   pip install uv
   
   # 运行安装脚本
   python setup.py
   ```

### 第二步：配置API密钥

编辑 `config.json` 文件，添加您的API密钥：

```json
{
  "api_keys": {
    "deepseek_api_key": "sk-your-deepseek-key",
    "minimax_api_key": "your-minimax-key",
    "minimax_group_id": "your-group-id"
  }
}
```

### 第三步：启动应用

```bash
uv run python src/movie_translate/ui/main_app.py
```

### 第四步：使用应用

1. **导入视频** - 拖拽或选择视频文件
2. **设置语言** - 选择源语言和目标语言
3. **开始处理** - 点击"开始翻译"按钮
4. **等待完成** - 查看进度，完成后导出视频

## 📋 支持的语言

### 源语言
- 🇨🇳 中文 (zh)
- 🇺🇸 英语 (en)
- 🇯🇵 日语 (ja)
- 🇰🇷 韩语 (ko)
- 🇫🇷 法语 (fr)
- 🇩🇪 德语 (de)
- 🇪🇸 西班牙语 (es)
- 🇷🇺 俄语 (ru)

### 目标语言
支持所有源语言作为目标语言

## 🔑 API密钥获取

### DeepSeek API
1. 访问 https://platform.deepseek.com/
2. 注册账户
3. 创建API密钥
4. 复制密钥到config.json

### MiniMax API
1. 访问 https://api.minimax.chat/
2. 注册账户
3. 创建应用获取API密钥和Group ID
4. 复制到config.json

### 百度语音API
1. 访问 https://cloud.baidu.com/product/speech
2. 创建语音技术应用
3. 获取API Key和Secret Key
4. 复制到config.json

## 🎯 常用操作

### 批量处理
1. 选择多个视频文件
2. 统一设置处理参数
3. 批量开始处理

### 断点续传
- 处理中断后重新启动应用
- 系统会自动恢复处理进度
- 避免重复处理

### 质量调整
- **高质量** - 效果最好，处理较慢
- **标准质量** - 平衡效果和速度
- **快速模式** - 处理快速，质量稍低

## 💡 使用技巧

### 提高处理速度
1. 使用SSD存储
2. 增加并行处理数量
3. 选择合适的处理质量

### 节省API费用
1. 启用缓存功能
2. 使用本地处理模式
3. 设置月度预算限制

### 优化翻译质量
1. 选择合适的翻译模型
2. 确保音频质量清晰
3. 正确识别角色声音

## 🆘 遇到问题？

### 常见错误
- **API密钥错误** - 检查密钥是否正确
- **网络连接问题** - 检查网络连接
- **内存不足** - 关闭其他程序，增加虚拟内存
- **音频格式不支持** - 转换为MP4格式

### 获取帮助
1. 查看 `README.md` 详细文档
2. 检查 `logs/` 目录下的日志文件
3. 访问项目主页提交问题

---

**开始您的视频翻译之旅！** 🎬✨