import torch

class YOLOv5Classifier:
  def __init__(self, model_path='path/to/your/yolov5_model.pt'):
    self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)

  def predict(self, image):
    results = self.model(image)
    return results

  def process_image(self, image_path):
    with Image.open(image_path) as img:
        return self.predict(img)

  def process_video(self, video_path):
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
      ret, frame = cap.read()
      if ret:
        result = self.predict(frame)
        # Process result here
      else:
        break
    cap.release()
