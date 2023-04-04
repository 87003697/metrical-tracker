import os
from abc import ABC
from glob import glob
from pathlib import Path

import cv2
import face_alignment
import numpy as np
import torch
from loguru import logger
from torch.utils.data import Dataset
from tqdm import tqdm

from face_detector import FaceDetector
from image import crop_image_bbox, squarefiy, get_bbox
from glob import glob

class GeneratorDataset(Dataset, ABC):
    def __init__(self, source, config):
        self.device = 'cuda:0'
        self.config = config
        self.source = Path(source)

        self.initialize()
        self.face_detector_mediapipe = FaceDetector('google')
        self.face_detector = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, device=self.device)

    def initialize(self):
        path = Path(self.source, 'source')
        if not path.exists() or len(os.listdir(str(path))) == 0:
            # video_file = self.source / 'video.mp4'
            # find video file under the source directory using glob
            video_file = glob(f'{self.source}/*.mp4')[0]

            if not os.path.exists(video_file):
                logger.error(f'[ImagesDataset] Neither images nor a video was provided! Execution has stopped! {self.source}')
                exit(1)
            path.mkdir(parents=True, exist_ok=True)
            os.system(f'ffmpeg -i {video_file} -vf fps={self.config.fps} -q:v 1 {self.source}/source/%05d.png')

        self.images = sorted(glob(f'{self.source}/source/*.jpg') + glob(f'{self.source}/source/*.png'))

    def process_face(self, image):
        # detect face and if CUDA OOM, try again
        while True:
            try:
                lmks, scores, detected_faces = self.face_detector.get_landmarks_from_image(image, return_landmark_score=True, return_bboxes=True)
                break
            except RuntimeError as e:
                if str(e).startswith('CUDA'):
                    print("Warning: out of memory, sleep for 30s")
                    import time; time.sleep(30)
                else:
                    print(e)
                    break        

        if detected_faces is None:
            lmks = None
        else:
            lmks = lmks[0]
            detected_faces = detected_faces[0][:-1]
        dense_lmks = self.face_detector_mediapipe.dense(image)
        return lmks, dense_lmks, detected_faces

    def run(self):
        logger.info('Generating dataset...')
        bbox = None
        bbox_path = self.config.actor + "/bbox.pt"

        if os.path.exists(bbox_path):
            bbox = torch.load(bbox_path)

        prev_bbox = None # in case the face is not detected in the current frame, use the bbox from the previous frame
        for imagepath in tqdm(self.images):
            lmk_path = imagepath.replace('source', 'kpt').replace('png', 'npy').replace('jpg', 'npy')
            lmk_path_dense = imagepath.replace('source', 'kpt_dense').replace('png', 'npy').replace('jpg', 'npy')

            if not os.path.exists(lmk_path) or not os.path.exists(lmk_path_dense):
                image = cv2.imread(imagepath)
                h, w, c = image.shape

                if bbox is None and self.config.crop_image:
                    lmk, _, bbox = self.process_face(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # estimate initial bbox
                    if bbox is None:
                        bbox = prev_bbox
                    else:
                        bbox = get_bbox(image, bbox, self.config.bbox_scale)
                        torch.save(bbox, bbox_path)

                if self.config.crop_image:
                    image = crop_image_bbox(image, bbox)
                    prev_bbox = bbox # the bbox is saved in case the face is not detected in the future frame
                    if self.config.image_size[0] == self.config.image_size[1]:
                        image = squarefiy(image, size=self.config.image_size[0])
                else:
                    image = cv2.resize(image, (self.config.image_size[1], self.config.image_size[0]), interpolation=cv2.INTER_CUBIC)

                lmk, dense_lmk, _ = self.process_face(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                if lmk is None:
                    logger.info(f'Empty face_alignment lmks for path: ' + imagepath)
                    lmk = np.zeros([68, 2])

                if dense_lmk is None:
                    logger.info(f'Empty mediapipe lmks for path: ' + imagepath)
                    dense_lmk = np.zeros([478, 2])

                Path(lmk_path).parent.mkdir(parents=True, exist_ok=True)
                Path(lmk_path_dense).parent.mkdir(parents=True, exist_ok=True)
                Path(imagepath.replace('source', 'images')).parent.mkdir(parents=True, exist_ok=True)

                cv2.imwrite(imagepath.replace('source', 'images'), image)
                np.save(lmk_path_dense, dense_lmk)
                np.save(lmk_path, lmk)
