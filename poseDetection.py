import cv2
import json
import paho.mqtt.client as mqtt
from ultralytics import YOLO

# ==========================
# CONFIGURAZIONE MQTT
# ==========================
MQTT_BROKER = "80.116.191.172"
MQTT_PORT = 1883
MQTT_KEEPALIVE = 60
MQTT_TOPIC = "pose/json"

# Per MQTTv5: on_connect(client, userdata, flags, reason_code, properties)
def on_connect(client, userdata, flags, reason_code, properties):
    # Stampa solo se la connessione ha un problema (commenta se vuoi nascondere tutto)
    if reason_code != 0:
        print(f"Connessione MQTT fallita. Codice: {reason_code}")

# Per MQTTv5: on_disconnect(client, userdata, reason_code, properties)
def on_disconnect(client, userdata, reason_code, properties):
    pass  # Nessun output

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
    client.publish(MQTT_TOPIC, payload)

def main():
    # Carica il modello YOLOv8 Pose
    model = YOLO("yolov8n-pose.pt")
    model.to("cpu")  # Usa GPU con "cuda" se disponibile

    # Inizializza il client MQTT (protocollo v5)
    client = mqtt.Client(protocol=mqtt.MQTTv5)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
    client.loop_start()

    # Apri la webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    if not cap.isOpened():
        print("Errore: impossibile aprire la webcam.")
        return

    # Nomi keypoint YOLOv8 Pose
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

            results = model(frame, conf=0.5)
            if len(results) > 0:
                result = results[0]
                if hasattr(result, 'keypoints') and result.keypoints is not None:
                    kpts_all = result.keypoints.xy
                    if len(kpts_all) > 0:
                        # Usa la prima persona rilevata
                        kpts_persona = kpts_all[0]
                        if kpts_persona is not None and len(kpts_persona) == 17:
                            keypoints_list = [
                                (keypoint_names[i], (px, py))
                                for i, (px, py) in enumerate(kpts_persona)
                            ]
                            publish_keypoints_json(client, keypoints_list)

    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
