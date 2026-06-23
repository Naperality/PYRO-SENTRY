import cv2
from ultralytics import YOLO
import cvzone
import serial
import time

# ==========================
# ARDUINO SERIAL CONNECTION
# ==========================

ARDUINO_PORT = "COM3"  # Change this
BAUD_RATE = 9600

arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE)
time.sleep(2)

# ==========================
# YOLO MODEL
# ==========================

model = YOLO("model/best.pt")

# ==========================
# CAMERA
# ==========================

cap = cv2.VideoCapture(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ==========================
# THRESHOLDS
# ==========================

MIN_CONFIDENCE = 0.50
FIRE_CONFIRM_CONFIDENCE = 0.80

SMOKE_CONFIDENCE = 0.75
IOU_THRESHOLD = 0.20

# Fire must be visible continuously
CONFIRMATION_TIME = 3  # seconds

fire_start_time = None
fire_confirmed = False

COLORS = {
    "fire": (0, 0, 255),
    "smoke": (128, 128, 128)
}

print("Starting PyroSentry...")
print("Press Q to quit")

while True:

    success, frame = cap.read()

    if not success:
        print("Failed to read camera.")
        break

    results = model(
        frame,
        conf=MIN_CONFIDENCE,
        iou=IOU_THRESHOLD,
        verbose=False
    )

    detection_status = "No Detection"

    fire_detected_this_frame = False

    if len(results) > 0:

        boxes = results[0].boxes

        for box in boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0])

            class_id = int(box.cls[0])

            class_name = model.names[class_id]

            if class_name.lower() == "smoke":
                if confidence < SMOKE_CONFIDENCE:
                    continue

            color = COLORS.get(
                class_name.lower(),
                (0, 255, 0)
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                2
            )

            label = f"{class_name.upper()} {confidence:.2f}"

            cvzone.putTextRect(
                frame,
                label,
                (x1, max(35, y1)),
                scale=1.2,
                thickness=2,
                colorR=color
            )

            if class_name.lower() == "fire":

                detection_status = "FIRE DETECTED"

                if confidence >= FIRE_CONFIRM_CONFIDENCE:
                    fire_detected_this_frame = True

            elif class_name.lower() == "smoke":
                detection_status = "SMOKE DETECTED"

    # ==========================
    # FIRE CONFIRMATION LOGIC
    # ==========================

    current_time = time.time()

    if fire_detected_this_frame:

        if fire_start_time is None:
            fire_start_time = current_time

        elapsed = current_time - fire_start_time

        if elapsed >= CONFIRMATION_TIME:

            if not fire_confirmed:

                print("CONFIRMED FIRE")

                arduino.write(b"FIRE\n")

                fire_confirmed = True

    else:

        fire_start_time = None

        if fire_confirmed:

            arduino.write(b"SAFE\n")

            print("SAFE")

            fire_confirmed = False

    # ==========================
    # DISPLAY STATUS
    # ==========================

    cv2.rectangle(
        frame,
        (0, 0),
        (frame.shape[1], 40),
        (0, 0, 0),
        -1
    )

    status_text = (
        "CONFIRMED FIRE"
        if fire_confirmed
        else detection_status
    )

    cv2.putText(
        frame,
        status_text,
        (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "PyroSentry Fire Detection",
        frame
    )

    key = cv2.waitKey(1)

    if key & 0xFF == ord("q"):
        break

# ==========================
# CLEANUP
# ==========================

arduino.write(b"SAFE\n")

cap.release()

cv2.destroyAllWindows()

arduino.close()