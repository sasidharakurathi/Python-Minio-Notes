from minio import Minio
import io

# 1. Connect to the MinIO Docker Container
client = Minio(
    "localhost:9000",         # Note: We use 9000 (API), not 9001 (UI)
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False              # Set to False because we aren't using HTTPS locally
)

BUCKET_NAME = "my-images"

def setup_minio():
    print("🚀 Connecting to MinIO...")
    
    # 2. Pre-flight check: Create the bucket if it doesn't exist
    if not client.bucket_exists(BUCKET_NAME):
        client.make_bucket(BUCKET_NAME)
        print(f"✅ Created new bucket: '{BUCKET_NAME}'")
    else:
        print(f"✅ Bucket '{BUCKET_NAME}' already exists.")

def upload_test_file():
    # 3. Create some dummy data (simulating an image or file)
    file_name = "hello-world.txt"
    raw_data = b"Hello from Python! This is a test file stored in MinIO."
    
    # Convert raw bytes into a file-like object so MinIO can read it
    data_stream = io.BytesIO(raw_data)
    data_length = len(raw_data)

    print(f"-> Uploading '{file_name}' to MinIO...")
    
    # 4. Upload the file
    client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=file_name,
        data=data_stream,
        length=data_length,
        content_type="text/plain" # Change to "image/png" for images
    )
    
    print(f"🎉 Success! '{file_name}' has been safely stored.")

if __name__ == "__main__":
    try:
        setup_minio()
        upload_test_file()
    except Exception as e:
        print(f"❌ Error: {e}")