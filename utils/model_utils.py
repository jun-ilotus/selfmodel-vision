#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型工具模块
"""

import os
import json
import cv2
import numpy as np
import onnxruntime as ort


class ModelConfig:
    """模型配置类"""
    
    def __init__(self, config_path=None, character_dict_path='ppocr_keys_v1.txt', use_space_char=True):
        self.config = self.load_config(config_path)
        self.character = []
        with open(character_dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip('\n').strip('\r\n')
                self.character.append(line)
        if use_space_char:
            self.character.append(' ')
        self.character = ['blank'] + self.character

    def load_config(self, config_path):
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            return {
                "input": {"name": "input", "shape": [1, 224, 224, 3]},
                "output": {"name": "output"},
                "preprocess": {"resize": [224, 224], "normalize": True}
            }
    
    def get_input_shape(self):
        """获取输入形状"""
        return self.config['input']['shape']
    
    def get_preprocess_config(self):
        """获取预处理配置"""
        return self.config['preprocess']


class ModelLoader:
    """模型加载器"""
    
    def __init__(self, model_path, config_path=None):
        self.model_path = model_path
        self.session = None
        self.label_map = {}
        self.config = ModelConfig(config_path)

    def get_input_name(self):
        """获取输入节点名称"""
        input_name = []
        for node in self.session.get_inputs():
            input_name.append(node.name)
        return input_name
    
    def get_output_name(self):
        """获取输出节点名称"""
        output_name = []
        for node in self.session.get_outputs():
            output_name.append(node.name)
        return output_name
    
    def get_input_feed(self, input_name, image_numpy):
        """
        input_feed={self.input_name: image_numpy}
        :param input_name:
        :param image_numpy:
        :return:
        """
        input_feed = {}
        for name in input_name:
            input_feed[name] = image_numpy
        return input_feed
        
    def load_model(self):
        """加载模型"""
        try:
            self.session = ort.InferenceSession(self.model_path, None, providers=['CPUExecutionProvider'])
            return True
        except Exception as e:
            raise Exception(f"模型加载失败: {str(e)}")
    
    def load_label_map(self, label_map_path=None):
        """加载标签映射"""
        if label_map_path and os.path.exists(label_map_path):
            try:
                with open(label_map_path, 'r', encoding='utf-8') as f:
                    self.label_map = json.load(f)
            except Exception as e:
                print(f"标签映射加载失败: {str(e)}")
    
    def preprocess_image(self, img_path):
        """预处理图像"""

        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # 转换为BGR

        h, w = img.shape[:2]
        ratio = w / float(h)

        target_height, target_width = self.config.get_preprocess_config()['resize']

        new_w = min(int(np.ceil(target_height * ratio)), target_width)
        resized_img = cv2.resize(img, (new_w, target_height))
        padded_img = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        padded_img[:, :new_w, :] = resized_img

        img_array = padded_img.transpose(2, 0, 1) # HWC转换为CHW格式

        # 归一化到[-1, 1]
        img_array = img_array.astype(np.float32) / 255.0
        img_array = (img_array - 0.5) / 0.5

        img_array = img_array[np.newaxis, ...] # 添加batch维度
        
        return img_array
    
    def predict(self, img_path):
        """进行预测"""
        if self.session is None:
            raise Exception("模型未加载")
        
        # 预处理图像
        processed_img = self.preprocess_image(img_path)
        
        # 运行推理
        input_name = self.get_input_name()
        output_name = self.get_output_name()

        input_feed = self.get_input_feed(input_name, processed_img)

        outputs = self.session.run(output_name, input_feed=input_feed)
        
        # 处理结果
        prediction, confidence = self.process_output(outputs[0])
        
        return prediction, confidence
    
    def process_output(self, output, is_remove_duplicate=True):
        """处理模型输出
            :param output: 模型输出
            :param is_remove_duplicate: 是否去除重复
            :return: 预测结果
        """
        preds_idx = output.argmax(axis=2) # 取每个时间步（seq_len）上概率最大的类别索引，得到每个字符的预测类别，shape为[batch, seq_len]
        preds_prob = output.max(axis=2) # 取每个时间步（seq_len）上概率最大的概率值，得到每个字符的置信度，shape为[batch, seq_len]

        char_list = []
        conf_list = []
        prev_idx = None
        for idx, prob in zip(preds_idx[0], preds_prob[0]):
            if idx == 0:  # blank
                prev_idx = None
                continue
            if idx == prev_idx:  # 去重
                continue
            char_list.append(self.config.character[idx])
            conf_list.append(prob)
            prev_idx = idx
        text = ''.join(char_list)
        conf = float(np.mean(conf_list)) if conf_list else 0.0

        return text, conf


def find_config_file(model_path):
    """查找配置文件"""
    model_dir = os.path.dirname(model_path)
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    possible_configs = [
        os.path.join(model_dir, "config.json"),
        os.path.join(model_dir, f"{model_name}_config.json"),
        "config.json"  # 当前目录
    ]
    
    for config_path in possible_configs:
        if os.path.exists(config_path):
            return config_path
    return None 