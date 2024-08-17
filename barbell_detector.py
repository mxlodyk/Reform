from ultralytics import YOLO
import cv2

class BarbellDetector:

    def __init__(self):
        self.model = YOLO('/Users/melodyflavel/Projects/Python/Reform/runs/detect/barbell_detector6/weights/best.pt')

    def train_model(self):
        self.model.train(
            data='/Users/melodyflavel/Projects/Python/Reform/dataset/data.yaml',  # Path to your dataset configuration
            epochs=1,  # Number of epochs, adjust as needed
            imgsz=640,  # Image size
            batch=16,  # Batch size, adjust according to your GPU memory
            name='barbell_detector',  # Name of your training run
        )
    
    # Process video
    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Object detection
            object_detection_results = self.model(frame)
            annotated_object_detection = object_detection_results[0].plot()
            cv2.imshow("YOLO Feed", annotated_object_detection)
            if cv2.waitKey(10) & 0xFF == ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()