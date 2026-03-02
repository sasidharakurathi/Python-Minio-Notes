from fastapi import FastAPI, HTTPException, UploadFile, File
from minio import Minio
from minio.error import S3Error
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="MinIO Bucket Manager",
    description="A FastAPI wrapper for MinIO bucket operations",
    version="1.0.0"
)

# Initialize the MinIO Client
# Update the endpoint, access_key, and secret_key to match your environment.
minio_client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False # Set to True if using HTTPS
)

@app.get("/api/buckets", tags=["Buckets"])
def list_buckets():
    try:
        buckets = minio_client.list_buckets()
        return {"buckets": [{"name": bucket.name, "creation_date": bucket.creation_date} for bucket in buckets]}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")

@app.get("/api/buckets/{bucket_name}", tags=["Buckets"])
def check_bucket_exists(bucket_name: str):
    try:
        exists = minio_client.bucket_exists(bucket_name)
        if not exists:
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
        return {"message": f"Bucket '{bucket_name}' exists."}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")

@app.post("/api/buckets/{bucket_name}", tags=["Buckets"])
def create_bucket(bucket_name: str):
    try:
        if minio_client.bucket_exists(bucket_name):
            raise HTTPException(status_code=400, detail=f"Bucket '{bucket_name}' already exists.")
        
        minio_client.make_bucket(bucket_name)
        return {"message": f"Bucket '{bucket_name}' created successfully."}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")

@app.delete("/api/buckets/{bucket_name}", tags=["Buckets"])
def delete_bucket(bucket_name: str):
    try:
        if not minio_client.bucket_exists(bucket_name):
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
        
        minio_client.remove_bucket(bucket_name)
        return {"message": f"Bucket '{bucket_name}' deleted successfully."}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")
    
    
@app.post("/api/buckets/{bucket_name}/objects", tags=["Objects"])
def upload_object(bucket_name: str, file: UploadFile = File(...)):
    try:
        if not minio_client.bucket_exists(bucket_name):
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
        
        # Calculate file size (MinIO requires this for put_object)
        file.file.seek(0, 2) # Go to the end of the file
        file_size = file.file.tell() # Get the current position (size)
        file.file.seek(0) # Reset to the beginning of the file
        
        # Upload the file
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=file.filename,
            data=file.file,
            length=file_size,
            content_type=file.content_type
        )
        return {"message": f"File '{file.filename}' uploaded successfully."}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")


@app.get("/api/buckets/{bucket_name}/objects", tags=["Objects"])
def list_objects(bucket_name: str):
    try:
        if not minio_client.bucket_exists(bucket_name):
            raise HTTPException(status_code=404, detail=f"Bucket '{bucket_name}' not found.")
            
        objects = minio_client.list_objects(bucket_name)
        return {
            "objects": [
                {"name": obj.object_name, "size": obj.size, "last_modified": obj.last_modified} 
                for obj in objects
            ]
        }
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")


@app.get("/api/buckets/{bucket_name}/objects/{object_name}", tags=["Objects"])
def download_object(bucket_name: str, object_name: str):
    try:
        # Get the object from MinIO
        response = minio_client.get_object(bucket_name, object_name)
        
        # Create a generator to stream the file in chunks 
        # This prevents massive files from crashing your server's RAM
        def file_iterator():
            try:
                for chunk in response.stream(32 * 1024):
                    yield chunk
            finally:
                response.close()
                response.release_conn()

        return StreamingResponse(
            file_iterator(), 
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={object_name}"}
        )
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail=f"Object '{object_name}' not found.")
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")


@app.delete("/api/buckets/{bucket_name}/objects/{object_name}", tags=["Objects"])
def delete_object(bucket_name: str, object_name: str):
    try:
        minio_client.remove_object(bucket_name, object_name)
        return {"message": f"Object '{object_name}' deleted successfully."}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO Error: {str(e)}")