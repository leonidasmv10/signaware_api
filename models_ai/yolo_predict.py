from ultralytics import YOLO
from PIL import Image
import io

model = YOLO("models_ai/models/best.pt") 

def predict_image(image_bytes):
    """
    Recibe una imagen en bytes (como capturada desde la cámara),
    la pasa por el modelo YOLOv8 y devuelve una lista de detecciones.
    """
    # Convertir bytes en imagen PIL
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Hacer predicción
    results = model(image)

    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])  # ID de clase
            label = model.names[cls_id]  # Nombre de la clase
            conf = float(box.conf[0])  # Confianza
            coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]

            detections.append(
                {
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": [round(c, 2) for c in coords],
                }
            )

    return detections
