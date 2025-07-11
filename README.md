# 算法识别平台

一个基于PyQt5的桌面端算法识别平台，支持用户加载自己的ONNX格式模型进行图像识别和物体检测。

## 功能特点

- 🖼️ **多图像上传**: 支持同时上传多张图像进行批量识别
- 🤖 **模型加载**: 支持加载用户本地的ONNX格式模型
- 📊 **结果展示**: 清晰的结果表格显示，包含预测结果、置信度和处理状态
- ⚡ **异步处理**: 使用多线程处理，避免界面卡顿
- 📈 **统计信息**: 自动计算识别成功率和平均置信度
- 🎨 **美观界面**: 现代化的用户界面设计
- 🏗️ **模块化架构**: 清晰的代码结构，易于维护和扩展

## 项目结构

```
SelfModelVision/
├── main_app.py              # 主程序入口
├── algorithm_recognition_platform.py  # 旧版本（已重构）
├── ui/                      # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py       # 主窗口
│   ├── image_display.py     # 图像显示组件
│   ├── result_table.py      # 结果表格组件
│   └── model_processor.py   # 模型处理线程
├── utils/                   # 工具模块
│   ├── __init__.py
│   └── model_utils.py       # 模型工具类
├── requirements.txt         # 依赖包列表
├── README.md               # 项目说明
├── run.bat                 # Windows启动脚本
├── config.json             # 模型配置文件示例
├── model.onnx              # 示例模型文件
└── test.png                # 测试图像
```

## 系统要求

- Python 3.7+
- Windows 10/11 (推荐)
- 支持ONNX格式的深度学习模型

## 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd SelfModelVision
   ```

2. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行程序**
   ```bash
   # 方法1: 直接运行
   python main_app.py
   
   # 方法2: Windows用户双击运行
   run.bat
   ```

## 使用方法

### 1. 启动程序
运行 `python main_app.py` 启动算法识别平台。

### 2. 上传模型
- 点击"上传模型"按钮
- 选择您的ONNX格式模型文件
- 系统会自动查找同目录下的配置文件（config.json）

### 3. 上传图像
- 点击"上传图像"按钮
- 选择一张或多张图像文件
- 支持的格式：PNG, JPG, JPEG, BMP, TIFF

### 4. 开始识别
- 确保已上传模型和图像后，"开始识别"按钮会变为可用状态
- 点击"开始识别"开始处理
- 处理过程中会显示进度条

### 5. 查看结果
- 右侧表格会显示每张图像的识别结果
- 包含图像名称、预测结果、置信度和处理状态
- 处理完成后会显示统计信息

## 模型配置

系统支持通过config.json文件配置模型参数：

```json
{
  "model_type": "classification",
  "input": {
    "name": "input",
    "shape": [1, 224, 224, 3],
    "dtype": "float32"
  },
  "output": {
    "name": "output",
    "shape": [1, 1000],
    "dtype": "float32"
  },
  "preprocess": {
    "resize": [224, 224],
    "normalize": true,
    "convert_to_grayscale": false,
    "invert_color": false
  },
  "label_map_file": "labels.json"
}
```

### 配置参数说明

- **input**: 模型输入配置
  - `name`: 输入节点名称
  - `shape`: 输入张量形状
  - `dtype`: 数据类型

- **output**: 模型输出配置
  - `name`: 输出节点名称
  - `shape`: 输出张量形状

- **preprocess**: 图像预处理配置
  - `resize`: 调整图像大小 [高度, 宽度]
  - `normalize`: 是否归一化到[0,1]
  - `convert_to_grayscale`: 是否转换为灰度图
  - `invert_color`: 是否反转颜色

- **label_map_file**: 标签映射文件路径（可选）

## 标签映射文件

如果您的模型是分类模型，可以创建标签映射文件：

```json
{
  "cat": 0,
  "dog": 1,
  "bird": 2
}
```

## 支持的模型类型

- **图像分类**: 输出类别概率分布
- **目标检测**: 输出检测框和类别
- **语义分割**: 输出像素级分类结果
- **其他ONNX模型**: 系统会尝试自动处理

## 代码架构

### 模块说明

- **main_app.py**: 程序入口，创建QApplication和主窗口
- **ui/main_window.py**: 主窗口类，管理整体界面布局和事件处理
- **ui/image_display.py**: 图像显示组件，负责显示上传的图像
- **ui/result_table.py**: 结果表格组件，显示识别结果
- **ui/model_processor.py**: 模型处理线程，在后台进行模型推理
- **utils/model_utils.py**: 模型工具类，提供模型加载、配置管理等功能

### 设计模式

- **MVC模式**: 界面(View)、业务逻辑(Controller)、数据处理(Model)分离
- **单例模式**: 主窗口使用单例模式
- **观察者模式**: 使用信号槽机制进行组件间通信
- **工厂模式**: 模型加载器使用工厂模式创建不同类型的模型

## 故障排除

### 常见问题

1. **模型加载失败**
   - 确保模型文件是有效的ONNX格式
   - 检查模型文件路径是否正确

2. **图像处理错误**
   - 确保图像文件格式受支持
   - 检查图像文件是否损坏

3. **内存不足**
   - 减少同时处理的图像数量
   - 关闭其他占用内存的程序

4. **依赖包安装失败**
   - 使用管理员权限运行pip
   - 尝试使用conda安装

5. **模块导入错误**
   - 确保在项目根目录运行程序
   - 检查Python路径设置

### 错误日志

程序会在状态栏显示错误信息，如果遇到问题，请查看状态栏的提示信息。

## 技术架构

- **前端界面**: PyQt5
- **模型推理**: ONNX Runtime
- **图像处理**: Pillow + NumPy
- **多线程处理**: QThread
- **代码架构**: 模块化设计，MVC模式

## 开发计划

- [ ] 支持更多模型格式（TensorFlow, PyTorch）
- [ ] 添加结果导出功能
- [ ] 支持视频文件处理
- [ ] 添加模型性能分析
- [ ] 支持GPU加速推理
- [ ] 添加插件系统
- [ ] 支持批量配置管理

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License 