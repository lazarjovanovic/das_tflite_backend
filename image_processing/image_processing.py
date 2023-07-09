import tensorflow as tf
from utils.read_config import get_image_processing_config
from utils.logger import logging


class ImageProcessing(object):
    def __init__(self):
        self.config = get_image_processing_config()
        # self.classes = ["bcc", "psoriasis"]
        self.classes = list(self.config["classes"].split(','))
        self.path_model = 'image_processing/model_classificator.tflite'

        self.interpreter = tf.lite.Interpreter(model_path=self.path_model)
        self.interpreter.allocate_tensors()

    def run_odt_and_draw_results(self, image_path):
        """Run object detection on the input image and draw the detection results"""
        output_class = ""
        output_probability = ""
        status_flag = False
        try:
            # Load the input shape required by the model
            _, input_height, input_width, _ = self.interpreter.get_input_details()[0]['shape']

            # Load the input image and preprocess it
            preprocessed_image, original_image = self.preprocess_image(
                "examination_images/" + image_path,
                (input_height, input_width)
            )

            # Run object detection on the input image
            output_class, output_probability = self.detect_objects(preprocessed_image)
            status_flag = True
        except Exception as e:
            logging.warning(f"Unable to perform image processing for image {image_path} due to error {e}")
        return status_flag, output_class, output_probability

    @staticmethod
    def preprocess_image(image_path, input_size):
        """Preprocess the input image to feed to the TFLite model"""
        img = tf.io.read_file(image_path)
        img = tf.io.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.uint8)
        original_image = img
        resized_img = tf.image.resize(img, input_size)
        resized_img = resized_img[tf.newaxis, :]
        resized_img = tf.cast(resized_img, dtype=tf.uint8)
        return resized_img, original_image

    def detect_objects(self, image):
        input_details = self.interpreter.get_input_details()[0]
        output_details = self.interpreter.get_output_details()[0]
        self.interpreter.set_tensor(input_details["index"], image)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(output_details["index"])[0]
        output_class_index = output.argmax()
        output_class = self.classes[output_class_index]
        output_probability = round(output[output_class_index] / 256, 5) * 100

        return output_class, output_probability
