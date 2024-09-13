import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint, QRect
from PIL import Image
import os

# Custom imports
import global_vars
from gui.pyqt6_gui import Yolo8AnnotationTool

class TestYolo8AnnotationTool(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.tool = Yolo8AnnotationTool()

    def test_show_next_image(self):
        self.tool.image_list = ["image1.png", "image2.png"]
        self.tool.current_index = 0
        self.tool.show_next_image()
        self.assertEqual(self.tool.current_index, 1)

    def test_show_previous_image(self):
        self.tool.image_list = ["image1.png", "image2.png"]
        self.tool.current_index = 1
        self.tool.show_previous_image()
        self.assertEqual(self.tool.current_index, 0)

    def test_on_file_selected(self):
        self.tool.image_list = ["image1.png", "image2.png"]
        self.tool.file_list_widget.addItem("image1.png")
        self.tool.file_list_widget.addItem("image2.png")
        self.tool.file_list_widget.setCurrentRow(1)
        self.tool.on_file_selected(self.tool.file_list_widget.currentItem(), None)
        self.assertEqual(self.tool.current_index, 1)

    def test_add_folder(self):
        folder_path = os.path.dirname(__file__)
        self.tool.load_images_from_folder(folder_path)
        self.assertTrue(len(self.tool.image_list) > 0)

    def test_load_images_from_folder(self):
        folder_path = os.path.dirname(__file__)
        self.tool.load_images_from_folder(folder_path)
        self.assertTrue(len(self.tool.image_list) > 0)

    def test_save_image(self):
        self.tool.current_image = Image.new('RGB', (100, 100))
        self.tool.image_path = "test_image.png"
        self.tool.save_image()
        self.assertTrue(os.path.exists("test_image.png"))
        os.remove("test_image.png")

    def test_start_drawing(self):
        event = self._create_mouse_event(Qt.MouseButton.LeftButton, QPoint(50, 50))
        self.tool.start_drawing(event)
        self.assertTrue(self.tool.drawing)

    def test_update_drawing(self):
        self.tool.drawing = True
        event = self._create_mouse_event(Qt.MouseButton.LeftButton, QPoint(100, 100))
        self.tool.update_drawing(event)
        self.assertEqual(self.tool.current_rect.bottomRight(), QPoint(0, 0))

    def test_finish_drawing(self):
        self.tool.drawing = True
        event = self._create_mouse_event(Qt.MouseButton.LeftButton, QPoint(100, 100))
        self.tool.finish_drawing(event)
        self.assertFalse(self.tool.drawing)

    def test_undo_bounding_box(self):
        self.tool.bounding_boxes.append(QRect(0, 0, 10, 10))
        self.tool.undo_stack.append(('add', QRect(0, 0, 10, 10)))
        self.tool.undo_bounding_box()
        self.assertEqual(len(self.tool.bounding_boxes), 0)

    def test_redo_bounding_box(self):
        self.tool.redo_stack.append(('add', QRect(0, 0, 10, 10)))
        self.tool.redo_bounding_box()
        self.assertEqual(len(self.tool.bounding_boxes), 1)

    def test_save_annotations(self):
        self.tool.image_path = "test_image.png"
        self.tool.bounding_boxes.append(QRect(0, 0, 10, 10))
        self.tool.annotation_input.setText("1")
        self.tool.save_annotations()
        self.assertTrue(os.path.exists("test_image.txt"))
        os.remove("test_image.txt")

    def test_delete_annotations(self):
        self.tool.image_path = "test_image.png"
        with open("test_image.txt", "w") as f:
            f.write("1 0.1 0.1 0.1 0.1")
        self.tool.delete_annotations()
        self.assertFalse(os.path.exists("test_image.txt"))

    def test_load_annotations(self):
        self.tool.image_path = "test_image.png"
        with open("test_image.txt", "w") as f:
            f.write("1 0.1 0.1 0.1 0.1")
        self.tool.load_annotations()
        self.assertEqual(len(self.tool.bounding_boxes), 1)
        os.remove("test_image.txt")

    def test_validate_annotations(self):
        self.tool.image_path = "test_image.png"
        with open("test_image.txt", "w") as f:
            f.write("1 0.1 0.1 0.1 0.1")
        self.tool.validate_annotations()
        self.assertTrue(True)  # Just to ensure the method runs without error
        os.remove("test_image.txt")

    def _create_mouse_event(self, button, pos):
        event = type('QMouseEvent', (object,), {})()
        event.button = lambda: button
        event.position = lambda: pos
        return event


if __name__ == "__main__":
    unittest.main()