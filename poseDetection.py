import cv2
import time
import json
import paho.mqtt.client as mqtt
from ultralytics import YOLO

# ==========================
# CONFIGURAZIONE MQTT
# ==========================
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC = "/pose/json"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connesso al broker MQTT con successo.")
    else:
        print(f"Connessione al broker MQTT fallita. Codice: {rc}")

def on_disconnect(client, userdata, rc):
    print("Disconnesso dal broker MQTT.")

def publish_keypoints_json(client, keypoints_list):
    data = {"keypoints": []}
    for label, (x, y) in keypoints_list:
        data["keypoints"].append({
            "label": label,
            "x": float(x),
            "y": float(y),
            "z": 0.0
        })

    payload = json.dumps(data)
    result = client.publish(MQTT_TOPIC, payload)
    if result[0] == 0:
        print(f"[MQTT] Pubblicato JSON su {MQTT_TOPIC}")
    else:
        print(f"[MQTT] ERRORE pubblicando su {MQTT_TOPIC}")

# ==========================
# SCRIPT PRINCIPALE
# ==========================
def main():
    # 1) Carica il modello YOLOv8 Pose
    model = YOLO("yolov8n-pose.pt")  # Modello leggero
    model.to("cpu")  # Usa GPU se disponibile

    # 2) Inizializza il client MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    client.loop_start()

    # 3) Apri la webcam con risoluzione ridotta
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        print("Errore: impossibile aprire la webcam.")
        return

    keypoint_names = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Errore nel leggere il frame.")
                break

            # 4) Predizione pose
            results = model.track(frame, conf=0.5, persist=True)  # Usa il tracciamento
            if results and results[0].keypoints is not None:
                kpts_persona = results[0].keypoints.xy[0]  # shape: (17, 2)

                # Costruisci la lista (label, (x, y))
                keypoints_list = [
                    (keypoint_names[i], (px, py))
                    for i, (px, py) in enumerate(kpts_persona)
                    if i < len(keypoint_names)
                ]

                # 5) Pubblica in formato JSON
                if keypoints_list:
                    publish_keypoints_json(client, keypoints_list)

                # 6) Disegna i keypoint sul frame (opzionale)
                for (lbl, (xx, yy)) in keypoints_list:
                    cv2.circle(frame, (int(xx), int(yy)), 4, (0, 255, 0), -1)

            # 7) Mostra il frame (opzionale)
            cv2.imshow("YOLOv8 Pose", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interruzione da tastiera.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

