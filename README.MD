# 🚀 AWS S3 Cloud File Manager
A Flask-based web application that allows users to upload files directly to an Amazon S3 bucket and view a list of stored files using secure Presigned URLs.

🛠️ Performance Features : 
Recursive Multi-Upload: Handles bulk file transfers by asynchronously streaming data to S3.

Smart Type-Sensing: Automatically detects file extensions (.pdf, .jpg, .mp4) and assigns high-quality FontAwesome icons.

Ephemeral Security: Generates Presigned URLs for file viewing, ensuring your S3 bucket remains private while still allowing user access.

Instant Search: A zero-lag filter built in vanilla JavaScript to handle large file lists locally.

## 📦 Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your AWS credentials.
4. Run the app: `python app.py`
