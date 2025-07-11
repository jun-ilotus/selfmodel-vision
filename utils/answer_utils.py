 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
答案工具模块
"""

import os
import json


class AnswerMatcher:
    """答案匹配器"""
    
    def __init__(self, answer_file_path="utils/data.json"):
        self.answer_file_path = answer_file_path
        self.answers = {}
        self.load_answers()
    
    def load_answers(self):
        """加载标准答案"""
        try:
            if os.path.exists(self.answer_file_path):
                with open(self.answer_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 将答案数据转换为字典，以文件名为键
                    for item in data:
                        if 'name' in item and 'label' in item:
                            self.answers[item['name']] = item['label']
                # print(f"成功加载 {len(self.answers)} 条标准答案")
            else:
                print(f"答案文件不存在: {self.answer_file_path}")
        except Exception as e:
            print(f"加载答案文件失败: {str(e)}")
    
    def get_answer(self, filename):
        """获取指定文件名的标准答案"""
        return self.answers.get(filename, None)
    
    def calculate_accuracy(self, prediction, correct_answer):
        """计算正确率（编辑距离）"""
        if not correct_answer:
            return None
        
        # 编辑距离
        prediction = str(prediction).strip()
        correct_answer = str(correct_answer).strip()
        if not correct_answer:
            return None
        
        dist = self.levenshtein_distance(prediction, correct_answer)
        acc = 1.0 - dist / max(1, len(correct_answer))
        return max(0.0, acc * 100)
    
    def is_standard_dataset(self, filename):
        """判断是否为标准数据集中的文件"""
        return filename in self.answers
    
    @staticmethod
    def levenshtein_distance(s1, s2):
        """计算Levenshtein编辑距离（动态规划算法）"""
        if len(s1) < len(s2):
            return AnswerMatcher.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]