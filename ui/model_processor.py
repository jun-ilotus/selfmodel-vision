import os
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from utils.model_utils import ModelLoader, find_config_file


class ModelProcessor(QThread):
    """模型处理线程，避免界面卡顿"""
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, model_path, image_paths, config_path=None):
        super().__init__()
        self.model_path = model_path
        self.image_paths = image_paths
        self.config_path = config_path
        self.model_loader = None
        
    def run(self):
        try:
            # 查找配置文件
            if not self.config_path:
                self.config_path = find_config_file(self.model_path)
            
            # 创建模型加载器
            self.model_loader = ModelLoader(self.model_path, self.config_path)
            
            # 加载模型
            self.progress_signal.emit(20)
            self.model_loader.load_model()
            
            # 加载标签映射
            if self.config_path and os.path.exists(self.config_path):
                import json
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'label_map_file' in config:
                        self.model_loader.load_label_map(config['label_map_file'])
            
            results = []
            total_images = len(self.image_paths)
            
            for i, img_path in enumerate(self.image_paths):
                try:
                    # 进行预测
                    prediction, confidence = self.model_loader.predict(img_path)
                    
                    results.append({
                        'image_path': img_path,
                        'prediction': prediction,
                        'confidence': confidence,
                        'status': '成功'
                    })
                    
                except Exception as e:
                    results.append({
                        'image_path': img_path,
                        'prediction': '错误',
                        'confidence': 0.0,
                        'status': f'失败: {str(e)}'
                    })
                
                progress = 20 + int(70 * (i + 1) / total_images)
                self.progress_signal.emit(progress)
            
            self.progress_signal.emit(100)
            self.result_signal.emit({'results': results, 'total': total_images})
            
        except Exception as e:
            self.error_signal.emit(str(e)) 