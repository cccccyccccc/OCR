from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for, jsonify
import os
import uuid
import shutil
from ocr_processor import process_file

# --- 配置 (无需改动) ---
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app = Flask(__name__)
# ... (其余配置与之前相同) ...
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.secret_key = 'a_very_secret_key'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_endpoint():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'success': False, 'message': '未选择任何文件'})
    
    file = request.files['file']
    original_filename = file.filename
    
    _, file_extension = os.path.splitext(original_filename)
    unique_filename = str(uuid.uuid4()) + file_extension
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(upload_path)
    
    output_dir_name = os.path.splitext(original_filename)[0]
    dedicated_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], output_dir_name)
    
    success = process_file(upload_path, dedicated_output_dir)
    
    if success:
        zip_filename_base = output_dir_name
        shutil.make_archive(
            base_name=os.path.join(app.config['OUTPUT_FOLDER'], zip_filename_base),
            format='zip',
            root_dir=app.config['OUTPUT_FOLDER'],
            base_dir=output_dir_name
        )
        zip_filename = f"{zip_filename_base}.zip"
        download_url = url_for('download_zip', zip_filename=zip_filename)
        
        # --- 【核心修改】 ---
        # 1. 找到生成的 .md 文件
        md_filename = f"{output_dir_name}.md"
        md_filepath = os.path.join(dedicated_output_dir, md_filename)
        
        markdown_content = ""
        try:
            # 2. 读取 .md 文件的内容
            with open(md_filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except Exception as e:
            print(f"Error reading markdown file: {e}")

        # 3. 将 .md 文件内容也加入到返回的JSON中
        return jsonify({
            'success': True, 
            'message': '文件解析成功！',
            'download_url': download_url,
            'zip_filename': zip_filename,
            'markdown_content': markdown_content # <--- 新增字段
        })
    else:
        return jsonify({'success': False, 'message': '文件解析失败，请检查后台日志。'})

@app.route('/download/<zip_filename>')
def download_zip(zip_filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
