from .models import YOLOv5Classifier
from .datalayer import DataLayer

class Classifier:
  def __init__(self):
    self.model = YOLOv5Classifier()
    self.data_layer = DataLayer()

  def classify_image(self, image_path):
    result = self.model.process_image(image_path)
    # Here you might want to save the result or do further processing
    self.data_layer.save_result(result, 'path/to/save/result.txt')
    return result

  def classify_video(self, video_path):
    self.model.process_video(video_path)
    # Similar to classify_image but for video processing
