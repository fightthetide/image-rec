import pytest
from unittest.mock import patch, Mock, MagicMock
from PIL import Image
import cv2

from my_classifier.models import YOLOv5Classifier  # Adjust import based on your package structure

# Fixture for the classifier with mocked torch.hub.load
@pytest.fixture
def classifier():
    with patch('torch.hub.load') as mock_torch_hub:
        mock_model = MagicMock()
        mock_torch_hub.return_value = mock_model
        classifier = YOLOv5Classifier(model_path="mock/path/to/model.pt")
        yield classifier, mock_torch_hub, mock_model

def test_init(classifier):
    """Test that the classifier initializes with the correct model path."""
    classifier_instance, mock_torch_hub, mock_model = classifier
    mock_torch_hub.assert_called_once_with('ultralytics/yolov5', 'custom', path="mock/path/to/model.pt")
    assert classifier_instance.model == mock_model

def test_predict(classifier):
    """Test the predict method with a mock image."""
    classifier_instance, _, mock_model = classifier
    mock_image = Mock()
    mock_results = Mock()
    mock_model.return_value = mock_results

    results = classifier_instance.predict(mock_image)

    mock_model.assert_called_once_with(mock_image)
    assert results == mock_results

@pytest.mark.parametrize("image_path", ["mock/image.jpg", "test/path/image.png"])
@patch('PIL.Image.open')
def test_process_image(mock_image_open, classifier, image_path):
    """Test processing an image file with different paths."""
    classifier_instance, _, mock_model = classifier
    mock_image = Mock(spec=Image.Image)
    mock_image_open.return_value.__enter__.return_value = mock_image
    mock_results = Mock()
    mock_model.return_value = mock_results

    results = classifier_instance.process_image(image_path)

    mock_image_open.assert_called_once_with(image_path)
    mock_model.assert_called_once_with(mock_image)
    assert results == mock_results

@patch('cv2.VideoCapture')
def test_process_video(mock_video_capture, classifier):
    """Test processing a video file."""
    classifier_instance, _, mock_model = classifier
    mock_cap = MagicMock()
    mock_video_capture.return_value = mock_cap
    
    # Simulate video frames
    mock_cap.isOpened.side_effect = [True, True, False]  # Two frames, then end
    mock_cap.read.side_effect = [
        (True, Mock()),  # First frame
        (True, Mock()),  # Second frame
        (False, None)    # End of video
    ]
    mock_results = Mock()
    mock_model.return_value = mock_results

    classifier_instance.process_video("mock/video.mp4")

    mock_video_capture.assert_called_once_with("mock/video.mp4")
    assert mock_cap.read.call_count == 3  # Called until False
    assert mock_model.call_count == 2     # Two frames processed
    mock_cap.release.assert_called_once()
