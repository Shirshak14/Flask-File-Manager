# 🚀 AWS S3 Cloud File Manager
A Flask-based web application that allows users to upload files directly to an Amazon S3 bucket and view a list of stored files using secure Presigned URLs.

## 🛠️ Features
- **Secure Uploads:** Uses `boto3` to stream files to S3.
- **Private Access:** Generates temporary 1-hour links for viewing files.
- **Environment Safety:** Uses `.env` files to protect AWS credentials.

## 📦 Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your AWS credentials.
4. Run the app: `python app.py`
