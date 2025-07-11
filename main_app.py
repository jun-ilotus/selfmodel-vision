#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算法识别平台主程序
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import AlgorithmRecognitionPlatform


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("算法识别平台")
    app.setApplicationVersion("1.0")
    
    # 创建主窗口
    window = AlgorithmRecognitionPlatform()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 