# YOLO Object Detection API

A Dockerized REST API for real-time object detection using YOLOv8 and FastAPI.  
Built as part of the AIMonk Labs ML Internship training program.

---

## What This Does

Takes an image via HTTP POST request, runs YOLOv8 object detection on it, draws bounding boxes with labels and confidence scores using OpenCV, and returns the annotated image.

---

## Project Structure

```
detection_api/
├── Dockerfile            # Environment setup instructions for Docker
├── requirements.txt      # Python dependencies
├── app.py                # FastAPI application — the core detection API
└── client.py             # Python client to hit the API from any machine
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.9-slim | Base runtime |
| FastAPI + Uvicorn | Web framework and ASGI server |
| Ultralytics YOLOv8 | Object detection model (yolov8n) |
| OpenCV (headless) | Drawing bounding boxes on images |
| Docker | Containerization and deployment |

---

## Setup & Installation

### Prerequisites
- Docker installed and running
- Docker Hub account (for push/pull)

### 1. Clone / Create Project Folder

```bash
mkdir detection_api
cd detection_api
# Add Dockerfile, requirements.txt, app.py, client.py
```

### 2. `requirements.txt`

```
numpy
fastapi
uvicorn
opencv-python-headless
requests
ultralytics
python-multipart
```

> **Why `opencv-python-headless`?**  
> Docker has no display/GUI. The regular opencv package tries to load GUI libraries and crashes inside a container. The headless version skips all GUI dependencies — same functionality, no display needed.

### 3. Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **Why copy `requirements.txt` before source code?**  
> Docker builds in layers and caches each one. If you copy all code first, every small code change forces a full pip install again. Copying requirements separately means pip install is only re-run when dependencies actually change.

---

## Build & Run

### Build the Docker Image

```bash
docker build -t yolo-detection:1.0 .
```

### Run the Container with Volume Mount

```bash
# Linux / macOS
docker run -d \
  --name detection_container \
  -p 8000:8000 \
  -v $(pwd):/app \
  yolo-detection:1.0

# Windows PowerShell
docker run -d `
  --name detection_container `
  -p 8000:8000 `
  -v C:\Users\<your-username>\Downloads\detection_api:/app `
  yolo-detection:1.0
```

> **Why volume mount (`-v`)?**  
> Volume mounting links your local `detection_api/` folder directly to `/app` inside the container. Any changes you make to `app.py` outside are instantly reflected inside — no need to rebuild the image every time you edit code. Essential for development workflow.

### Verify it's running

```bash
docker logs detection_container
```

Expected output:
```
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## API Reference

### `POST /detect`

Accepts an image file, runs YOLO detection, returns the annotated image with bounding boxes.

**Request**
- Method: `POST`
- URL: `http://localhost:8000/detect`
- Body: `multipart/form-data` with field `file` containing the image

**Response**
- Content-Type: `image/jpeg`
- Body: Annotated image with bounding boxes and labels

---

## Usage

### Option 1 — curl (terminal)

```bash
curl -X POST "http://localhost:8000/detect" \
  -F "file=@test.jpg" \
  --output result.jpg
```

Replace `test.jpg` with your image filename. Output saved as `result.jpg`.

**Windows PowerShell:**
```powershell
curl -X POST "http://localhost:8000/detect" -F "file=@test.jpg" --output result.jpg
```

### Option 2 — Python Client (`client.py`)

```python
import requests

def detect_objects(image_path, server_url, output_path):
    url = f"{server_url}/detect"
    
    with open(image_path, "rb") as f:
        files = {"file": (image_path, f, "image/jpeg")}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        with open(output_path, "wb") as out:
            out.write(response.content)
        print(f"Saved to {output_path}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    detect_objects(
        image_path="test.jpg",
        server_url="http://localhost:8000",
        output_path="result.jpg"
    )
```

Run it:
```bash
python client.py
```

> To hit the API from a **different server**, change `server_url` to the remote machine's IP:
> ```python
> server_url="http://<server-ip>:8000"
> ```

---

## Docker Hub

The image is publicly available on Docker Hub.

**Image:** `anshul397/yolo-detection:1.0`

### Pull and run from anywhere

```bash
docker pull anshul397/yolo-detection:1.0
docker run -d -p 8000:8000 anshul397/yolo-detection:1.0
```

### Push (for reference)

```bash
docker login
docker tag yolo-detection:1.0 anshul397/yolo-detection:1.0
docker push anshul397/yolo-detection:1.0
```


---

## YOLO Model Details

- Model: `yolov8n` (nano — smallest and fastest variant)
- Trained on: COCO dataset — detects 80 common object classes
- Classes include: person, car, truck, bus, dog, cat, laptop, phone, bottle, chair, and 70 more
- Model file downloads automatically on first container run (~6MB)

---


This project was built as part of the structured training period covering:
- Linux shell scripting (MIT Missing Semester)
- Docker fundamentals and containerization
- Computer vision with YOLOv8
- REST API development with FastAPI
- AWS fundamentals (EC2, AMI, GPU instances)

**GitHub:** [github.com/Anshul3977](https://github.com/anshul-art)  
**Docker Hub:** [hub.docker.com/r/anshul397/yolo-detection](https://hub.docker.com/r/anshul397/yolo-detection)

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|---|---|---|
| `opencv` crash in Docker | GUI libraries missing | Use `opencv-python-headless` |
| `python-multipart` error | FastAPI file upload dependency | Add to `requirements.txt` |
| `$(pwd)` not working | Windows PowerShell doesn't support it | Use full path: `C:\Users\...\detection_api` |
| Container not running | Code error in `app.py` | Run `docker logs detection_container` |
| Port already in use | Another process on 8000 | Change `-p 9000:8000` and hit port 9000 |
