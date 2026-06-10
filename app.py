from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
import cv2
import numpy as np
import io

app = FastAPI()

# Load model ONCE at startup — why? Loading model is heavy (seconds).
# If you load inside the endpoint it reloads on every request = very slow
model = YOLO("yolov8n.pt")  # downloads ~6MB model automatically on first run

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    
    # Read raw bytes from HTTP request
    contents = await file.read()
    
    # Convert bytes → numpy array → opencv image
    # Why? YOLO and opencv work on numpy arrays, not raw bytes
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Run YOLO detection
    results = model(image)

    # Draw boxes on image
    for result in results:
        for box in result.boxes:
            # Get box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])   # confidence score
            cls = int(box.cls[0])       # class index
            label = f"{model.names[cls]} {conf:.2f}"

            # Draw rectangle — why opencv? It directly manipulates image pixels
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label above box
            cv2.putText(image, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Convert image back to bytes to send in HTTP response
    _, buffer = cv2.imencode(".jpg", image)
    
    # StreamingResponse — why? Sends raw image bytes directly
    # media_type tells browser/client it's a jpeg image
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")