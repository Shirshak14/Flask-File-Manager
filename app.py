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

@app.route('/')
def index():
    files = []
    try:
        # 1. Fetch from S3
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        
        # 2. Check if 'Contents' actually exists in the response
        if 'Contents' in response:
            for obj in response['Contents']:
                size_bytes = obj['Size']
                
                # Conversion logic
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024**2:
                    size_str = f"{round(size_bytes/1024, 1)} KB"
                else:
                    size_str = f"{round(size_bytes/(1024**2), 1)} MB"

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
        else:
            print("💡 Info: Bucket is currently empty.")

    except Exception as e:
        # This will print the EXACT AWS error in your terminal
        print(f"❌ AWS Error: {e}")

    # 3. Always return the template, even if files is empty
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        try:
            # Upload to S3
            s3.upload_fileobj(
                file,
                BUCKET_NAME,
                file.filename,
                ExtraArgs={"ContentType": file.content_type}
            )
            print(f"✅ Successfully uploaded {file.filename}")
        except Exception as e:
            print(f"❌ Upload Error: {e}")
            
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        print(f"🗑️ Deleted {filename} from S3")
    except Exception as e:
        print(f"❌ Delete Error: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)