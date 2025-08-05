# Movie Translate 启动指南

## 🚀 快速启动

### 方法一：使用启动脚本（推荐）

```bash
python start_app.py
```

此脚本会自动启动 API 服务器和 GUI 应用程序。

### 方法二：手动启动

#### 1. 启动 API 服务器
```bash
python src/movie_translate/api/server.py
```

#### 2. 启动 GUI 应用程序（在新的终端窗口）
```bash
python main.py
```

## 🔧 配置要求

### 系统要求
- Python 3.10+
- Windows 10/11 或 Linux

### 依赖项
运行 `python main.py` 会自动检查依赖项。

### API 服务器配置
- 默认地址：`http://localhost:8000`
- 健康检查：`http://localhost:8000/health`

## 🛠️ 故障排除

### 问题：点击创建项目没有反应
**原因**：API 服务器未启动
**解决**：确保 API 服务器正在运行

### 问题：无法连接到 API 服务器
**原因**：
1. API 服务器未启动
2. 端口 8000 被占用
3. 防火墙阻止连接

**解决**：
1. 使用 `start_app.py` 启动
2. 检查端口占用：`netstat -ano | findstr :8000`
3. 检查防火墙设置

### 问题：依赖项缺失
**解决**：
```bash
uv sync  # 推荐方式
# 或
pip install -r requirements.txt
```

## 📋 功能验证

### 1. 检查 API 服务器状态
访问 `http://localhost:8000/health` 或运行：
```bash
curl http://localhost:8000/health
```

### 2. 检查 GUI 应用程序
- 窗口大小：1400x1200
- 支持音频文件：MP3, WAV, FLAC, AAC, OGG, M4A, WMA
- 支持视频文件：MP4, AVI, MKV, MOV, WMV, FLV, WebM

## 🎯 使用步骤

1. **启动应用程序**
   ```bash
   python start_app.py
   ```

2. **创建新项目**
   - 点击"新建项目"
   - 填写项目名称
   - 选择媒体文件（视频或音频）
   - 选择目标语言
   - 点击"创建"

3. **项目处理**
   - 按照步骤导航处理项目
   - 可以随时保存和恢复项目

## 🔍 日志和调试

### 日志位置
- 应用程序日志：控制台输出
- 数据库：`movie_translate.db`

### 调试模式
启动 API 服务器时使用调试模式：
```bash
python src/movie_translate/api/server.py --debug
```

## 📞 支持

如果遇到问题，请检查：
1. API 服务器是否正在运行
2. 网络连接是否正常
3. 依赖项是否完整安装
4. 防火墙设置是否阻止连接