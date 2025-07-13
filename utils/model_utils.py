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
from PIL import Image
import sys


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包环境，使用当前文件所在目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class ModelConfig:
    """模型配置类"""
    
    def __init__(self, config_path=None, character_dict_path='utils/ppocr_keys_v1.txt', use_space_char=True):
        self.config = self.load_config(config_path)
        self.character = []
        # with open(character_dict_path, 'r', encoding='utf-8') as f:
        # 使用资源路径获取字符字典文件
        char_dict_path = get_resource_path(character_dict_path)
        with open(char_dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip('\n').strip('\r\n')
                self.character.append(line)
        if use_space_char:
            self.character.append(' ')
        self.character = ['blank'] + self.character

        self.classDict = []
        # with open('utils/label2class.txt', 'r', encoding='utf-8') as f:
        label_path = get_resource_path('utils/label2class.txt')
        with open(label_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip('\n').strip('\r\n')
                self.classDict.append(line)

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
        img_array = None
        input_name = self.get_input_name()[0]

        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if input_name == 'TextRecognizerInput':
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # 转换为BGR

            h, w = img.shape[:2]
            ratio = w / float(h)

            target_height, target_width = 48, 320

            new_w = int(np.ceil(target_height * ratio))
            if new_w > target_width:
                resized_img = cv2.resize(img, (new_w, target_height))
                # 如果宽度超过320，拆分为多个片段
                img_arrays = []

                start_x = 0
                end_x = min(target_width, new_w)
                while start_x < end_x:
                    # 裁剪当前片段
                    segment = resized_img[:, start_x:end_x, :]
                    
                    # 如果片段宽度不足320，进行填充
                    if segment.shape[1] < target_width:
                        padded_segment = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                        padded_segment[:, :segment.shape[1], :] = segment
                        segment = padded_segment
                    
                    # 转换为CHW格式并归一化
                    segment_array = segment.transpose(2, 0, 1)  # HWC转换为CHW格式
                    segment_array = segment_array.astype(np.float32) / 255.0
                    segment_array = (segment_array - 0.5) / 0.5
                    
                    img_arrays.append(segment_array)

                    start_x = end_x
                    end_x = min(target_width + target_width, new_w)
                
                # 组成batch
                img_array = np.stack(img_arrays, axis=0)  # 添加batch维度
            else:
                # 正常处理
                resized_img = cv2.resize(img, (new_w, target_height))
                padded_img = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                padded_img[:, :new_w, :] = resized_img

                img_array = padded_img.transpose(2, 0, 1) # HWC转换为CHW格式

                # 归一化到[-1, 1]
                img_array = img_array.astype(np.float32) / 255.0
                img_array = (img_array - 0.5) / 0.5

                img_array = img_array[np.newaxis, ...] # 添加batch维度
        elif input_name == 'ImageClassificationInput':
            # 将输入图像的最小边（宽或高）缩放到256像素，同时保持原始宽高比
            def image_resize(image, min_len):
                image = Image.fromarray(image)
                ratio = float(min_len) / min(image.size[0], image.size[1])
                if image.size[0] > image.size[1]:
                    new_size = (int(round(ratio * image.size[0])), min_len)
                else:
                    new_size = (min_len, int(round(ratio * image.size[1])))
                image = image.resize(new_size, Image.BILINEAR)
                return np.array(image)

            image = image_resize(img, 256)

            # 从调整大小后的图像中心裁剪出224×224的区域
            def crop_center(image, crop_w, crop_h):
                h, w, c = image.shape
                start_x = w // 2 - crop_w // 2
                start_y = h // 2 - crop_h // 2
                return image[start_y:start_y + crop_h, start_x:start_x + crop_w, :]

            image = crop_center(image, 224, 224)

            # 将图像从HWC格式（高度、宽度、通道）转换为CHW格式（通道、高度、宽度）
            image = image.transpose(2, 0, 1)

            # 将像素值从uint8转换为float32类型
            img_data = image.astype('float32')

            # 先除以255将像素值缩放到[0,1]范围, 然后使用ImageNet数据集的均值和标准差进行标准化
            mean_vec = np.array([0.485, 0.456, 0.406])
            stddev_vec = np.array([0.229, 0.224, 0.225])
            norm_img_data = np.zeros(img_data.shape).astype('float32')
            for i in range(img_data.shape[0]):
                norm_img_data[i, :, :] = (img_data[i, :, :] / 255 - mean_vec[i]) / stddev_vec[i]

            # add batch channel
            norm_img_data = norm_img_data.reshape(1, 3, 224, 224).astype('float32')
            img_array = norm_img_data
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
        input_name = self.get_input_name()[0]
        text = ''
        conf = 0.0

        if input_name == 'TextRecognizerInput':
            preds_idx = output.argmax(axis=2) # 取每个时间步（seq_len）上概率最大的类别索引，得到每个字符的预测类别，shape为[batch, seq_len]
            preds_prob = output.max(axis=2) # 取每个时间步（seq_len）上概率最大的概率值，得到每个字符的置信度，shape为[batch, seq_len]

            # 处理batch中的多个片段
            all_texts = []
            all_confs = []

            for i in range(len(preds_prob)):
                char_list = []
                conf_list = []
                prev_idx = None
                for idx, prob in zip(preds_idx[i], preds_prob[i]):
                    if idx == 0:  # blank
                        prev_idx = None
                        continue
                    if idx == prev_idx:  # 去重
                        continue
                    char_list.append(self.config.character[idx])
                    conf_list.append(prob)
                    prev_idx = idx

                segment_text = ''.join(char_list)
                segment_conf = float(np.mean(conf_list)) if conf_list else 0.0

                all_texts.append(segment_text)
                all_confs.append(segment_conf)

            # 合并所有片段的结果
            text = ''.join(all_texts)
            conf = float(np.mean(all_confs)) if all_confs else 0.0
        elif input_name == 'ImageClassificationInput':
            idx = output.argmax()
            text = self.config.classDict[idx]

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