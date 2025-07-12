import os
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QPushButton, QProgressBar, QSplitter, QMessageBox, QFileDialog, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from .image_display import ImageDisplayWidget
from .result_table import ResultTableWidget
from .model_processor import ModelProcessor
from utils.model_utils import find_config_file
from utils.answer_utils import AnswerMatcher


class AlgorithmRecognitionPlatform(QMainWindow):
    """算法识别平台主窗口"""
    def __init__(self):
        super().__init__()
        self.model_path = None
        self.image_paths = []
        self.config_path = None
        self.answer_matcher = AnswerMatcher()  # 加载标准答案
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("算法识别平台")
        self.setGeometry(100, 100, 1500, 800)
        self.setup_styles()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)  

        # 创建各个组件
        self.create_button_area(main_layout)
        self.create_progress_bar(main_layout)
        self.create_content_area(main_layout)

        # 状态栏
        self.statusBar().showMessage("就绪")
        self.avg_acc_label = QLabel("平均正确率：-")
        self.avg_acc_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.avg_acc_label.setStyleSheet("color: #1976d2; padding: 0 30px;")
        self.statusBar().addPermanentWidget(self.avg_acc_label)
        self.center()
        
    def setup_styles(self):
        """设置界面样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLabel {
                color: #333;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
    def create_button_area(self, main_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.upload_image_btn = QPushButton("上传图像")
        self.upload_image_btn.clicked.connect(self.upload_images)
        button_layout.addWidget(self.upload_image_btn)
        
        self.upload_model_btn = QPushButton("加载模型")
        self.upload_model_btn.clicked.connect(self.upload_model)
        button_layout.addWidget(self.upload_model_btn)
        
        self.process_btn = QPushButton("开始识别")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        button_layout.addWidget(self.process_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
    def create_progress_bar(self, main_layout):
        """创建进度条"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def create_content_area(self, main_layout):
        """创建主要内容区域"""
        content_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧图像显示区域
        self.image_display = ImageDisplayWidget()
        content_splitter.addWidget(self.image_display)
        
        # 右侧结果表格区域
        self.result_table = ResultTableWidget()
        content_splitter.addWidget(self.result_table)
        
        # 设置分割器比例
        content_splitter.setSizes([500, 1000])
        main_layout.addWidget(content_splitter)
        
    def upload_images(self):
        """上传图像"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("图像文件 (*.png *.jpg *.jpeg *.bmp *.tiff)")
        
        if file_dialog.exec_():
            new_image_paths = file_dialog.selectedFiles()
            if new_image_paths:
                self.image_display.add_image(new_image_paths)  # 追加到显示组件
                self.image_paths = self.image_display.get_image_paths()  # 从显示组件获取完整列表
                self.statusBar().showMessage(f"已上传 {len(new_image_paths)} 张图像，总计 {len(self.image_paths)} 张")
                self.update_process_button()
        
    def upload_model(self):
        """上传模型"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("ONNX模型文件 (*.onnx)")
        
        if file_dialog.exec_():
            self.model_path = file_dialog.selectedFiles()[0]
            self.statusBar().showMessage(f"已上传模型: {os.path.basename(self.model_path)}")
            
            # 尝试查找配置文件
            self.find_config_file()
            self.update_process_button()
            
    def find_config_file(self):
        """查找配置文件"""
        self.config_path = find_config_file(self.model_path)
        # if self.config_path:
        #     self.statusBar().showMessage(f"已找到配置文件: {os.path.basename(self.config_path)}")
            
    def update_process_button(self):
        """更新处理按钮状态"""
        # 同步图像路径
        self.image_paths = self.image_display.get_image_paths()
        self.process_btn.setEnabled(bool(self.model_path and self.image_paths))
        
    def start_processing(self):
        """开始处理"""
        if not self.model_path or not self.image_paths:
            QMessageBox.warning(self, "警告", "请先上传模型和图像")
            return
            
        # 禁用按钮
        self.upload_image_btn.setEnabled(False)
        self.upload_model_btn.setEnabled(False)
        self.process_btn.setEnabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建处理线程
        self.processor = ModelProcessor(self.model_path, self.image_paths, self.config_path)
        self.processor.progress_signal.connect(self.update_progress)
        self.processor.result_signal.connect(self.handle_results)
        self.processor.error_signal.connect(self.handle_error)
        self.processor.start()
        
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
        
    def handle_results(self, data):
        """处理结果"""

        # 增加标准答案和正确率
        for result in data['results']:
            filename = os.path.basename(result['image_path'])
            answer = self.answer_matcher.get_answer(filename)
            result['answer'] = answer if answer is not None else ''
            if answer is not None:
                result['accuracy'] = self.answer_matcher.calculate_accuracy(result['prediction'], answer)
            else:
                result['accuracy'] = None

        self.result_table.update_results(data['results'])

        # 计算平均正确率
        acc_list = [r['accuracy'] for r in data['results'] if r.get('accuracy') is not None]
        if acc_list:
            avg_acc = sum(acc_list) / len(acc_list)
            self.avg_acc_label.setText(f"平均正确率：{avg_acc:.2f}%")
        else:
            self.avg_acc_label.setText("平均正确率：-")

        # 计算统计信息
        successful = sum(1 for r in data['results'] if r['status'] == '成功')
        total = data['total']
        # 恢复按钮状态
        self.upload_image_btn.setEnabled(True)
        self.upload_model_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"处理完成: {successful}/{total} 成功")
        # 显示统计信息
        if successful > 0:
            avg_confidence = np.mean([r['confidence'] for r in data['results'] if r['status'] == '成功'])
            QMessageBox.information(self, "处理完成", 
                                  f"处理完成！\n"
                                  f"成功识别: {successful}/{total}")
        
    def handle_error(self, error_msg):
        """处理错误"""
        QMessageBox.critical(self, "错误", f"处理过程中发生错误:\n{error_msg}")
        
        # 恢复按钮状态
        self.upload_image_btn.setEnabled(True)
        self.upload_model_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self.statusBar().showMessage("处理失败") 

    def center(self):
        """窗口居中显示"""
        screen = self.screen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        ) 