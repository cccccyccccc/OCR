# AI 文档结构化解析工具

这是一个基于 PaddleOCR 和 Flask 构建的Web应用，允许用户上传图片或PDF文件，并将其结构化内容解析为Markdown格式。

## 功能特性

- 支持图片（JPG, PNG）和PDF文件格式。
- 提供美观的、带有毛玻璃效果的Web界面。
- 异步处理文件，提供流畅的单页应用体验。
- 支持结果预览和打包下载（包含Markdown文本及提取出的图片）。

## 技术栈

- **后端**: Python, Flask, PaddleOCR
- **前端**: HTML, CSS, JavaScript, Pico.css, marked.js

## 如何运行

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/flask_ocr_app.git
cd flask_ocr_app
```

### 2. 创建并激活Conda环境

建议使用 Conda 来管理环境。

```bash
# 创建一个新环境
conda create --name ocr_app python=3.10 -y

# 激活环境
conda activate ocr_app
```

### 3. 安装依赖

本项目的所有依赖都已在 `requirements.txt` 中列出。

```bash
pip install -r requirements.txt
```
**注意**: 请确保您的系统中已正确安装支持GPU的PaddlePaddle版本，并配置好相应的CUDA环境，以获得最佳性能。

### 4. 运行应用

```bash
python app.py
```

应用将在 `http://0.0.0.0:5000` 上启动。请在您的浏览器中通过 `http://<您的WSL的IP地址>:5000` 来访问。
