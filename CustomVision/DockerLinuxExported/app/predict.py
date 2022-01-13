import tensorflow as tf
import numpy as np
import PIL.Image
from datetime import datetime
from urllib.request import urlopen

MODEL_FILENAME = 'model.pb'
LABELS_FILENAME = 'labels.txt'

od_model = None
labels = None


class ObjectDetection:
    INPUT_TENSOR_NAME = 'image_tensor:0'
    OUTPUT_TENSOR_NAMES = ['detected_boxes:0', 'detected_scores:0', 'detected_classes:0']

    def __init__(self, model_filename):
        graph_def = tf.compat.v1.GraphDef()
        with open(model_filename, 'rb') as f:
            graph_def.ParseFromString(f.read())

        self.graph = tf.Graph()
        with self.graph.as_default():
            tf.import_graph_def(graph_def, name='')

        # Get input shape
        with tf.compat.v1.Session(graph=self.graph) as sess:
            self.input_shape = sess.graph.get_tensor_by_name(self.INPUT_TENSOR_NAME).shape.as_list()[1:3]

    def predict_image(self, image):
        image = image.convert('RGB') if image.mode != 'RGB' else image
        image = image.resize(self.input_shape)

        inputs = np.array(image, dtype=np.float32)[np.newaxis, :, :, :]
        with tf.compat.v1.Session(graph=self.graph) as sess:
            output_tensors = [sess.graph.get_tensor_by_name(n) for n in self.OUTPUT_TENSOR_NAMES]
            outputs = sess.run(output_tensors, {self.INPUT_TENSOR_NAME: inputs})
            return outputs


def initialize():
    global od_model
    od_model = ObjectDetection(MODEL_FILENAME)
    global labels
    with open(LABELS_FILENAME) as f:
        labels = [l.strip() for l in f.readlines()]


def predict_url(image_url):
    with urlopen(image_url) as binary:
        image = PIL.Image.open(binary)
        return predict_image(image)


def predict_image(image):
    predictions = od_model.predict_image(image)

    predictions = [{'probability': round(float(p[1]), 8),
                    'tagId': int(p[2]),
                    'tagName': labels[p[2]],
                    'boundingBox': {
                        'left': round(float(p[0][0]), 8),
                        'top': round(float(p[0][1]), 8),
                        'width': round(float(p[0][2] - p[0][0]), 8),
                        'height': round(float(p[0][3] - p[0][1]), 8)
                        }
                    } for p in zip(*predictions)]

    response = {'id': '', 'project': '', 'iteration': '', 'created': datetime.utcnow().isoformat(),
                'predictions': predictions}

    print("Resuls: " + str(response))
    return response
