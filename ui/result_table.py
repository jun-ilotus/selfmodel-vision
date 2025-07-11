import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class ResultTableWidget(QWidget):
    """结果表格组件"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("识别结果")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["图像", "预测结果", "置信度", "正确答案", "正确率", "状态"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def update_results(self, results):
        """更新结果表格"""
        self.table.setRowCount(len(results))
        
        for i, result in enumerate(results):
            # 图像名称
            image_name = os.path.basename(result['image_path'])
            self.table.setItem(i, 0, QTableWidgetItem(image_name))
            
            # 预测结果
            self.table.setItem(i, 1, QTableWidgetItem(str(result['prediction'])))
            
            # 置信度
            confidence = f"{result['confidence']:.4f}" if result['confidence'] > 0 else "N/A"
            self.table.setItem(i, 2, QTableWidgetItem(confidence))

            # 正确答案
            self.table.setItem(i, 3, QTableWidgetItem(str(result.get('answer', ''))))
            # 正确率
            acc = result.get('accuracy', None)
            acc_str = f"{acc:.1f}%" if acc is not None else ""
            self.table.setItem(i, 4, QTableWidgetItem(acc_str))
            
            # 状态
            status_item = QTableWidgetItem(result['status'])
            if result['status'] == '成功':
                status_item.setBackground(QColor(200, 255, 200))  # 浅绿色
            else:
                status_item.setBackground(QColor(255, 200, 200))  # 浅红色
            self.table.setItem(i, 5, status_item)
        
        self.table.resizeColumnsToContents() 