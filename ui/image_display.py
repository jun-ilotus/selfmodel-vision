import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout, QMessageBox, QDialog, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont


class ImagePreviewDialog(QDialog):
    """大图预览弹窗"""
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图像预览")
        self.setMinimumSize(400, 400)
        layout = QVBoxLayout(self)
        pixmap = QPixmap(image_path)
        label = QLabel()
        label.setPixmap(pixmap.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class ImageDisplayWidget(QWidget):
    """图像显示组件，支持多图像缩略图网格展示"""
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题和按钮区域
        title_layout = QHBoxLayout()
        title = QLabel("上传的图像")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title_layout.addWidget(title)
        
        # 清除按钮
        self.clear_btn = QPushButton("清除全部")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px 10px;
                font-size: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all_images)
        title_layout.addWidget(self.clear_btn)
        
        layout.addLayout(title_layout)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        
    def add_image(self, image_path_or_list):
        """添加图像到显示区域，支持单张或多张，追加模式"""
        # 支持单张或多张
        if isinstance(image_path_or_list, list):
            new_images = image_path_or_list
        else:
            new_images = [image_path_or_list]
        
        # 追加新图像到现有列表
        self.image_paths.extend(new_images)
        self.refresh_grid()
        
    def clear_all_images(self):
        """清除所有图像"""
        if self.image_paths:
            reply = QMessageBox.question(self, '确认清除', 
                                       f'确定要清除所有 {len(self.image_paths)} 张图像吗？',
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.image_paths.clear()
                self.refresh_grid()

    def refresh_grid(self):
        # 清除现有图像
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # 网格参数
        col_count = 3
        row = 0
        col = 0
        for idx, image_path in enumerate(self.image_paths):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                thumb = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label = ClickableLabel(image_path)
                label.setPixmap(thumb)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("border: 1px solid #ccc; padding: 3px;")
                label.clicked.connect(self.show_preview)
                # 文件名
                filename = os.path.basename(image_path)
                filename_label = QLabel(filename)
                filename_label.setAlignment(Qt.AlignCenter)
                filename_label.setWordWrap(True)
                # 容器
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(2,2,2,2)
                container_layout.addWidget(label)
                container_layout.addWidget(filename_label)
                self.scroll_layout.addWidget(container, row, col)
                col += 1
                if col >= col_count:
                    col = 0
                    row += 1

    def show_preview(self, image_path):
        dlg = ImagePreviewDialog(image_path, self)
        dlg.exec_()
        
    def get_image_paths(self):
        """获取所有图像路径"""
        return self.image_paths.copy()


class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path) 