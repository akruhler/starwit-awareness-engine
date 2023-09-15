import argparse
import threading
from typing import List

import cv2
import numpy as np
from visionapi.messages_pb2 import (Detection, DetectionOutput,
                                    TrackedDetection, TrackingOutput,
                                    VideoFrame)
from visionlib.pipeline.consumer import RedisConsumer

ANNOTATION_COLOR = (0, 0, 255)

def create_output_image(frame: VideoFrame):
    img_shape = frame.shape
    img_bytes = frame.frame_data
    img = np.frombuffer(img_bytes, dtype=np.uint8) \
        .reshape((img_shape.height, img_shape.width, img_shape.channels))
    return img

def annotate(image, detection: Detection, object_id: bytes = None):
    bbox_x1 = detection.bounding_box.min_x
    bbox_y1 = detection.bounding_box.min_y
    bbox_x2 = detection.bounding_box.max_x
    bbox_y2 = detection.bounding_box.max_y

    class_id = detection.class_id
    conf = detection.confidence

    label = f'{class_id} - {round(conf,2)}'

    if object_id is not None:
        object_id = object_id.hex()[:4]
        label = f'ID {object_id} - {class_id} - {round(conf,2)}'

    line_width = max(round(sum(image.shape) / 2 * 0.002), 2)

    cv2.rectangle(image, (bbox_x1, bbox_y1), (bbox_x2, bbox_y2), color=ANNOTATION_COLOR, thickness=line_width, lineType=cv2.LINE_AA)
    cv2.putText(image, label, (bbox_x1, bbox_y1 - 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, color=ANNOTATION_COLOR, thickness=round(line_width/3), fontScale=line_width/4, lineType=cv2.LINE_AA)

def showImage(window_name, image):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1920, 1080)
    cv2.imshow(window_name, image)
    if cv2.waitKey(1) == ord('q'):
        stop_event.set()
        cv2.destroyAllWindows()

def source_output_handler(frame_message, stream_id):
    frame_proto = VideoFrame()
    frame_proto.ParseFromString(frame_message)
    image = create_output_image(frame_proto)

    showImage(stream_id, image)

def detection_output_handler(detection_message, stream_id):
    detection_proto = DetectionOutput()
    detection_proto.ParseFromString(detection_message)
    print(f'Inference times - detection: {detection_proto.metrics.detection_inference_time_us} us')
    image = create_output_image(detection_proto.frame)

    for detection in detection_proto.detections:
        annotate(image, detection)

    showImage(stream_id, image)

def tracking_output_handler(tracking_message, stream_id):
    track_proto = TrackingOutput()
    track_proto.ParseFromString(tracking_message)
    print(f'Inference times - detection: {track_proto.metrics.detection_inference_time_us} us, tracking: {track_proto.metrics.tracking_inference_time_us} us')
    image = create_output_image(track_proto.frame)

    for tracked_det in track_proto.tracked_detections:
        annotate(image, tracked_det.detection, tracked_det.object_id)

    showImage(stream_id, image)

STREAM_TYPE_HANDLER = {
    'videosource': source_output_handler,
    'objectdetector': detection_output_handler,
    'objecttracker': tracking_output_handler,
}


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-s', '--stream', type=str, required=True)
    arg_parser.add_argument('--redis-host', type=str, default='localhost')
    arg_parser.add_argument('--redis-port', type=int, default=6379)
    args = arg_parser.parse_args()

    STREAM_ID = args.stream
    STREAM_TYPE = STREAM_ID.split(':')[0]
    REDIS_HOST = args.redis_host
    REDIS_PORT = args.redis_port

    stop_event = threading.Event()
    last_retrieved_id = None

    consume = RedisConsumer(REDIS_HOST, REDIS_PORT, [STREAM_ID])

    with consume:
        for stream_id, proto_data in consume():
            if stop_event.is_set():
                break

            if stream_id is None:
                continue

            STREAM_TYPE_HANDLER[STREAM_TYPE](proto_data, stream_id)

        

        
    
