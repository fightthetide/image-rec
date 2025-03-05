from unittest.mock import patch, Mock, MagicMock
from ..classifier import YOLOv5Classifier

class TestYOLOv5Classifier:
    def setup_method(self):
        """Runs before each test method to set up common state."""
        with patch('torch.hub.load') as self.mock_torch_hub_load:
            self.classifier = YOLOv5Classifier(model_path="test/path/model.pt")
            self.mock_model = self.mock_torch_hub_load.return_value

    @patch('torch.hub.load')
    def test_init(self, mock_torch_hub_load):
        """Test that __init__ loads the model with the correct path."""
        model_path = "test/path/model.pt"
        classifier = YOLOv5Classifier(model_path=model_path)
        
        mock_torch_hub_load.assert_called_once_with('ultralytics/yolov5', 'custom', path=model_path)
        assert classifier.model == mock_torch_hub_load.return_value

    def test_predict(self):
        """Test that predict calls the model with the image and returns results."""
        fake_image = "fake_image_data"
        mock_results = Mock()
        self.mock_model.return_value = mock_results
        
        result = self.classifier.predict(fake_image)
        
        self.mock_model.assert_called_once_with(fake_image)
        assert result == mock_results

    @patch('PIL.Image.open')  # Adjust based on your import
    def test_process_image(self, mock_image_open):
        """Test that process_image opens an image and calls predict."""
        image_path = "test/image.jpg"
        mock_image = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_image
        mock_results = Mock()
        self.mock_model.return_value = mock_results
        
        result = self.classifier.process_image(image_path)
        
        mock_image_open.assert_called_once_with(image_path)
        self.mock_model.assert_called_once_with(mock_image)
        assert result == mock_results

    @patch('cv2.VideoCapture')  # Adjust based on your import
    def test_process_video(self, mock_video_capture):
        """Test that process_video processes frames and releases the capture."""
        video_path = "test/video.mp4"
        mock_cap = mock_video_capture.return_value
        mock_cap.isOpened.side_effect = [True, True, False]  # Two frames, then end
        mock_cap.read.side_effect = [
            (True, "frame1"),
            (True, "frame2"),
            (False, None),
        ]
        mock_results = Mock()
        self.mock_model.side_effect = [mock_results, mock_results]
        
        self.classifier.process_video(video_path)
        
        mock_video_capture.assert_called_once_with(video_path)
        assert mock_cap.read.call_count == 2
        assert self.mock_model.call_count == 2
        mock_cap.release.assert_called_once()

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])