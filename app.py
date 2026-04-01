import os
import boto3
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Get the absolute path of the folder containing app.py
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

# Load the file using the absolute path
load_dotenv(dotenv_path=env_path, override=True)

print(f"DEBUG: Checking path: {env_path}")
print(f"DEBUG: File exists at path: {os.path.exists(env_path)}")
print(f"DEBUG: Access Key exists: {bool(os.getenv('S3_ACCESS_KEY'))}")
app = Flask(__name__)

# 2. AWS Configuration
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
S3_REGION = os.getenv('S3_REGION')
BUCKET_NAME = os.getenv('BUCKET_NAME')

# 3. Initialize S3 Client
s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

# --- ROUTES ---

# 1. LANDING PAGE (The "Front Door")
@app.route('/')
def home():
    return render_template('home.html')

# 2. DASHBOARD (The "Work" Page)
@app.route('/dashboard')
def dashboard():
    files = []
    try:
        # Fetch list from S3
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        
        if 'Contents' in response:
            for obj in response['Contents']:
                # Dynamic Size Calculation
                size_bytes = obj['Size']
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024**2:
                    size_str = f"{round(size_bytes/1024, 1)} KB"
                else:
                    size_str = f"{round(size_bytes/(1024**2), 1)} MB"

                # Generate secure viewing link
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                
                files.append({
                    'name': obj['Key'],
                    'size': size_str,
                    'url': url
                })
        return render_template('dashboard.html', files=files)

    except Exception as e:
        print(f"❌ AWS Error: {e}")
        return render_template('dashboard.html', files=[])

# 3. UPLOAD LOGIC
@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('file') # Supports multi-upload
    
    if not files or files[0].filename == '':
        return redirect(url_for('dashboard'))

    for file in files:
        try:
            s3.upload_fileobj(
                file,
                BUCKET_NAME,
                file.filename,
                ExtraArgs={"ContentType": file.content_type}
            )
            print(f"✅ Uploaded {file.filename}")
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            
    return redirect(url_for('dashboard'))

# 4. DELETE LOGIC
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        print(f"🗑️ Deleted {filename}")
    except Exception as e:
        print(f"❌ Delete Error: {e}")
    
    return redirect(url_for('dashboard'))

# 5. RENAME LOGIC
@app.route('/rename', methods=['POST'])
def rename_file():
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name')
    
    if not old_name or not new_name:
        return redirect(url_for('dashboard'))

    # Maintain extension
    ext = os.path.splitext(old_name)[1]
    if not new_name.lower().endswith(ext.lower()):
        new_name += ext

    try:
        copy_source = {'Bucket': BUCKET_NAME, 'Key': old_name}
        s3.copy_object(Bucket=BUCKET_NAME, CopySource=copy_source, Key=new_name)
        s3.delete_object(Bucket=BUCKET_NAME, Key=old_name)
        print(f"✅ Renamed {old_name} to {new_name}")
    except Exception as e:
        print(f"❌ Rename Error: {e}")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)