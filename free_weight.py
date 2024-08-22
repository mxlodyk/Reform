from ultralytics import YOLO
import cv2
import contextlib
import os

# ====================
# Free Weight Detector
# ====================
class FreeWeight:

    # Initialise
    def __init__(self):
        self.model = YOLO('runs/detect/barbell_detector/weights/best.pt')

    # Train model
    def train_model(self):
        self.model.train(
            data='/Users/melodyflavel/Projects/Python/Reform/dataset/data.yaml',
            epochs=1,
            imgsz=640, 
            batch=16,
            name='barbell_detector',
        )
    
    # Detect barbell
    def detect_barbell(self, video_path):
        barbell_detected = False
        bar_path_straight = None
        # Store range of x coordinates of barbell
        barbell_x_coordinates = [float('inf'), float('-inf')]

        cap = cv2.VideoCapture(video_path)
        print("Detecting barbell presence...")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Object detection
            results = self.model(frame, verbose=False)
            annotated = results[0].plot()
            cv2.imshow("YOLO Feed", annotated)
            if cv2.waitKey(10) & 0xFF == ord("q"):
                break
            for result in results:
                for detection in result.boxes:
                    confidence = detection.conf.item()
                    # If detection confidence score is greater than 70%
                    if confidence > 0.7:
                    # If 'barbell' class is detected
                        if detection.cls == 0:
                            barbell_detected = True

                            # Get smallest and largest x coordinates of barbell
                            box = detection.xywh[0]
                            x_coordinate = (box[0].item())
                            if x_coordinate < barbell_x_coordinates[0]:
                                barbell_x_coordinates[0] = x_coordinate
                            if x_coordinate > barbell_x_coordinates[1]:
                                barbell_x_coordinates[1] = x_coordinate

                            bar_path_straight = self.analyse_bar_path(barbell_x_coordinates)
        cap.release()
        cv2.destroyAllWindows()

        return barbell_detected, bar_path_straight

    # Analyse bar path
    def analyse_bar_path(self, coordinates):
        if abs(coordinates[0] - coordinates[1]) > 50:
            return False
        return True

