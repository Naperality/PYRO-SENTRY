import cv2
from ultralytics import YOLO
import cvzone

# Load trained model
model = YOLO("model/best.pt")

# Open webcam
cap = cv2.VideoCapture(1) # this is the source (use 0 for webcam or 1 for other cams connected)

# Optional webcam settings
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Detection thresholds
MIN_CONFIDENCE = 0.50
SMOKE_CONFIDENCE = 0.75
IOU_THRESHOLD = 0.20

# Class colors
COLORS = {
    "fire": (0, 0, 255),       # Red
    "smoke": (128, 128, 128)   # Gray
}

print("Starting Fire/Smoke Detection...")
print("Press Q to quit")

while True:

    success, frame = cap.read()

    if not success:
        print("Failed to read webcam.")
        break

    # Run YOLO inference
    results = model(
        frame,
        conf=MIN_CONFIDENCE,
        iou=IOU_THRESHOLD,
        verbose=False
    )

    detection_status = "No Detection"

    # Process detections
    if len(results) > 0:

        boxes = results[0].boxes

        for box in boxes:

            # Coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # Confidence
            confidence = float(box.conf[0])

            # Class ID
            class_id = int(box.cls[0])

            # Class Name
            class_name = model.names[class_id]

            # Apply smoke threshold
            if class_name.lower() == "smoke":
                if confidence < SMOKE_CONFIDENCE:
                    continue

            color = COLORS.get(class_name.lower(), (0, 255, 0))

            # Draw box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            # Detection label
            label = f"{class_name.upper()} {confidence:.2f}"

            cvzone.putTextRect(
                frame,
                label,
                (x1, max(35, y1)),
                scale=1.2,
                thickness=2,
                colorR=color
            )

            # Update status
            if class_name.lower() == "fire":
                detection_status = "FIRE DETECTED"

            elif class_name.lower() == "smoke":
                detection_status = "SMOKE DETECTED"

            # Print to terminal
            print(
                f"{class_name.upper()} "
                f"Confidence: {confidence:.2f}"
            )

    # Status bar
    cv2.rectangle(
        frame,
        (0, 0),
        (frame.shape[1], 40),
        (0, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        detection_status,
        (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    # Show video
    cv2.imshow("PyroSentry Fire Detection Test", frame)

    # Quit with Q
    key = cv2.waitKey(1)

    if key & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()