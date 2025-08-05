#!/usr/bin/env python3
"""
Movie Translate 启动脚本
此脚本会自动启动 API 服务器和 GUI 应用程序
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
# Also add the parent directory for absolute imports
sys.path.insert(0, str(Path(__file__).parent))

def start_api_server():
    """启动 API 服务器"""
    print("启动 API 服务器...")
    
    # 启动 API 服务器
    server_process = subprocess.Popen([
        sys.executable, 
        str(src_path / "movie_translate" / "api" / "server.py")
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # 等待服务器启动
    time.sleep(3)
    
    # 检查服务器是否成功启动
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("API 服务器启动成功")
            return server_process
        else:
            print("API 服务器启动失败")
            return None
    except Exception as e:
        print(f"无法连接到 API 服务器: {e}")
        return None

def start_gui_application():
    """启动 GUI 应用程序"""
    print("启动 GUI 应用程序...")
    
    # 启动 GUI 应用程序
    gui_process = subprocess.Popen([
        sys.executable, 
        "main.py"
    ])
    
    return gui_process

def main():
    """主函数"""
    print("Movie Translate 启动中...")
    
    # 启动 API 服务器
    server_process = start_api_server()
    if server_process is None:
        print("无法启动 API 服务器，请检查依赖项和配置")
        return 1
    
    try:
        # 启动 GUI 应用程序
        gui_process = start_gui_application()
        
        print("应用程序启动成功！")
        print("提示：关闭此窗口将停止所有服务")
        
        # 等待 GUI 应用程序结束
        gui_process.wait()
        
    except KeyboardInterrupt:
        print("\n正在停止服务...")
    finally:
        # 停止 API 服务器
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("API 服务器已停止")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)