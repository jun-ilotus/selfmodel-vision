#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt程序打包脚本
"""

import os
import subprocess
import sys


def build_exe():
    """打包程序为exe"""
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装完成")
    
    # 打包命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 不显示控制台窗口
        "--name=算法识别平台",           # 指定exe文件名
        "--icon=icon.ico",              # 图标文件（如果有的话）
        "--add-data=utils/data.json;utils",  # 添加数据文件
        "--hidden-import=PyQt5.sip",    # 确保PyQt5模块被包含
        "--hidden-import=onnxruntime",
        "--hidden-import=PIL",
        "--hidden-import=numpy",
        "main_app.py"                   # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    print("开始打包...")
    print("命令:", " ".join(cmd))
    
    try:
        subprocess.check_call(cmd)
        print("\n打包完成！")
        print("exe文件位置: dist/算法识别平台.exe")
        print("您可以将dist文件夹中的exe文件复制到其他电脑上运行")
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False
    
    return True


def build_with_spec():
    """使用spec文件打包（更灵活）"""
    
    # 创建spec文件
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_app.py'],
    pathex=[],
    binaries=[],
    datas=[('utils/data.json', 'utils')],
    hiddenimports=[
        'PyQt5.sip',
        'onnxruntime',
        'PIL',
        'numpy',
        'ui.main_window',
        'ui.image_display',
        'ui.result_table',
        'ui.model_processor',
        'utils.model_utils',
        'utils.answer_utils'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='算法识别平台',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # 写入spec文件
    with open('算法识别平台.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("使用spec文件打包...")
    try:
        subprocess.check_call(["pyinstaller", "算法识别平台.spec"])
        print("\n打包完成！")
        print("exe文件位置: dist/算法识别平台.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        return False


if __name__ == "__main__":
    print("=== PyQt程序打包工具 ===")
    print("1. 简单打包")
    print("2. 使用spec文件打包（推荐）")
    
    choice = input("请选择打包方式 (1/2): ").strip()
    
    if choice == "1":
        build_exe()
    elif choice == "2":
        build_with_spec()
    else:
        print("无效选择") 