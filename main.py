import onnxruntime as ort
import numpy as np
from PIL import Image
import json

# 读取模型说明文件
with open('config.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

input_shape = meta['input']['shape']  # [1, 92, 92, 1]
input_name = meta['input']['name']
output_name = meta['output']['name']
resize_h, resize_w = meta['preprocess']['resize']
adjust_contrast = meta['preprocess']['adjust_contrast']

# 读取标签映射
with open(meta['label_map_file'], 'r', encoding='utf-8') as f:
    w2i = json.load(f)
i2w = {v: k for k, v in w2i.items()}


def preprocess_image(img_path):
    img = Image.open(img_path).convert('L')
    img = np.array(img)
    img = 255 - img  # 取反色
    img = Image.fromarray(img)
    img = img.resize((resize_w, resize_h))
    img = np.array(img).astype(np.float32) / 255.0
    # onnxruntime不支持tf.image.adjust_contrast，简单近似
    mean = img.mean()
    img = (img - mean) * adjust_contrast + mean
    img = np.clip(img, 0, 1)
    img = img[np.newaxis, ..., np.newaxis]  # [1, H, W, 1]
    return img


def predict(img_path):
    img = preprocess_image(img_path)
    sess = ort.InferenceSession('model.onnx')
    outputs = sess.run([output_name], {input_name: img})
    print(outputs)
    pred_id = int(np.argmax(outputs[0]))
    print(pred_id)
    pred_char = i2w[pred_id]
    print('网络预测:', pred_char)
    return pred_char


if __name__ == '__main__':
    img_path = "test.png"
    predict(img_path)
