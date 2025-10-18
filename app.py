from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for, jsonify
import os
import uuid
import shutil
import re
from ocr_processor import process_file


UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.secret_key = 'a_very_secret_key'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/outputs/<path:filepath>')
def serve_output_file(filepath):
    """
    这个新的路由使得 'outputs' 文件夹下的所有文件都可以通过 URL 被访问。
    例如: /outputs/原始文件名/img/figure-1.png
    """
    return send_from_directory(app.config['OUTPUT_FOLDER'], filepath)

@app.route('/process', methods=['POST'])
def process_endpoint():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify({'success': False, 'message': '未选择任何文件'})
    file = request.files['file']
    original_filename = file.filename
    session_id = str(uuid.uuid4())
    _, file_extension = os.path.splitext(original_filename)
    unique_filename = session_id + file_extension
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(upload_path)
    
    # output_dir_name = os.path.splitext(original_filename)[0]
    dedicated_output_dir = os.path.join(app.config['OUTPUT_FOLDER'], session_id)
    
    success = process_file(upload_path, dedicated_output_dir)
    
    if success:
        shutil.make_archive(
            base_name=os.path.join(app.config['OUTPUT_FOLDER'], session_id),
            format='zip',
            root_dir=app.config['OUTPUT_FOLDER'],
            base_dir=session_id
        )
        zip_filename = f"{session_id}.zip"
        download_url = url_for('download_zip', zip_filename=zip_filename)
        md_filename = f"{session_id}.md"
        md_filepath = os.path.join(dedicated_output_dir, md_filename)
        
        markdown_content = ""
        try:
            with open(md_filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            def replace_html_image_src(match):
                image_path = match.group(1)
                new_url = url_for('serve_output_file', filepath=f"{session_id}/{image_path}")
                return match.group(0).replace(image_path, new_url)

            markdown_content = re.sub(r'<img src="(.*?)"', replace_html_image_src, markdown_content)
        except Exception as e:
            print(f"Error reading markdown file: {e}")
        return jsonify({
            'success': True, 
            'message': '文件解析成功！',
            'download_url': download_url,
            'zip_filename': zip_filename,
            'markdown_content': markdown_content 
        })
    else:
        return jsonify({'success': False, 'message': '文件解析失败，请检查后台日志。'})

@app.route('/download/<zip_filename>')
def download_zip(zip_filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], zip_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
