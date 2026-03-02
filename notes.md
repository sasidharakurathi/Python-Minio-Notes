# MinIO Notes

## 1. Windows Setup (Docker)

### Setup Docker 
  1. Go to [Docker Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
  2. Download `Docker Desktop` and Install it
  3. Make sure that `Docker` is added to Window's `System Environment Variables Path`

### Setup MinIO
  1. Go to `C:\Docker` directory
  2. Create a directory named `MinIO`
  3. Inside `MinIO` directory create a file named `docker-compose.yml`
  4. Open file and add below YAML code <br><br>
      ``` yml
      version: '3.8'

      services:
      minio:
          image: minio/minio:latest
          container_name: minio-local
          ports:
          - "9000:9000"  # The API Port (Python uses this)
          - "9001:9001"  # The Web Console Port (You use this in your browser)
          environment:
          # These are your default login credentials
          MINIO_ROOT_USER: minioadmin
          MINIO_ROOT_PASSWORD: minioadmin
          # This command starts the server and routes the UI to port 9001
          command: server /data --console-address ":9001"
          volumes:
          - minio_data:/data

      volumes:
          minio_data:
      ```
  5. Save the file and Open `cmd` and cd to `C:\Docker\MinIO`
  6. Execute the following command: `docker-compose up -d` (It will download and start the MinIO server)

## 2. Python (FastAPI) and MinIO Integration
  1. Run `pip install minio` in cmd to install the MinIO Utility Package for Python
  2. Check `minio_test.py` for python and minio test integration.
  3. Check `main.py` for python fastapi and minio bucket/objects integrations.
  4. You can run `run.py` using python to start the FastAPI Server.

## 3. Note
  1. Based on this setup MinIO's API runs on Port: `9000`
  2. Based on this setup MinIO's Web Console runs on Port: `9001`
  3. You can setup the `username` and `password` of minio in the `docker-compose.yml` file
  4. By default `username` and `password` are set to `minioadmin`
