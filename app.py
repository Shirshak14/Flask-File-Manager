import os
from flask import Flask, request, render_template, redirect, url_for
import boto3
from dotenv import load_dotenv

# 1. This tells Python exactly where THIS script lives
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Force it to load the .env file from that specific folder
load_dotenv(os.path.join(basedir, '.env'))

template_dir = r'C:\Users\Admin\Desktop\cloud-file-upload-2\Cloud 2\templates'
app = Flask(__name__, template_folder=template_dir)

# 3. GET variables with a fallback (so it never returns 'None')
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "shirshak-file-upload-123")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

# Create the client using these variables
s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

@app.route('/')
def index():
    # ... (rest of your listing code)
    # List all objects in the bucket
    files = []
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                # Generate a temporary link for each file
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': obj['Key']},
                    ExpiresIn=3600
                )
                files.append({'name': obj['Key'], 'url': url})
    except Exception as e:
        print(f"Error listing files: {e}")

    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file and file.filename != '':
        s3.upload_fileobj(
            file, 
            BUCKET_NAME, 
            file.filename,
            ExtraArgs={'ContentType': file.content_type}
        )
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    try:
        s3.delete_object(Bucket=BUCKET_NAME, Key=filename)
        print(f"✅ Deleted {filename} from {BUCKET_NAME}")
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    print(f"Checking for templates in: {template_dir}")
    print(f"Does index.html exist there? {os.path.exists(os.path.join(template_dir, 'index.html'))}")
    app.run(debug=True)
    
    