# -*- coding: utf-8 -*-

# Max-Planck-Gesellschaft zur Förderung der Wissenschaften e.V. (MPG) is
# holder of all proprietary rights on this computer program.
# You can only use this computer program if you have closed
# a license agreement with MPG or you get the right to use the computer
# program from someone who is authorized to grant you that right.
# Any use of the computer program without a valid license is prohibited and
# liable to prosecution.
#
# Copyright©2023 Max-Planck-Gesellschaft zur Förderung
# der Wissenschaften e.V. (MPG). acting on behalf of its Max Planck Institute
# for Intelligent Systems. All rights reserved.
#
# Contact: mica@tue.mpg.de

import argparse
from pathlib import Path

from yacs.config import CfgNode as CN
import os

cfg = CN()

cfg.flame_geom_path = 'data/FLAME2020/generic_model.pkl'
cfg.flame_template_path = 'data/uv_template.obj'
cfg.flame_lmk_path = 'data/landmark_embedding.npy'
cfg.tex_space_path = 'data/FLAME2020/FLAME_texture.npz'

cfg.num_shape_params = 300
cfg.num_exp_params = 100
cfg.tex_params = 140
cfg.actor = ''
cfg.config_name = ''
cfg.kernel_size = 7
cfg.sigma = 9.0
cfg.keyframes = [0]
cfg.bbox_scale = 2.5
cfg.fps = 25
cfg.begin_frames = 0
cfg.end_frames = 0
cfg.image_size = [512, 512]  # height, width
cfg.rotation_lr = 0.05
cfg.translation_lr = 0.003
cfg.raster_update = 16
cfg.pyr_levels = [[0.5, 90], [1.0, 80], [2.0, 70]]  # Gaussian pyramid levels (scaling, iters per level)
cfg.optimize_shape = False
cfg.optimize_jaw = False
cfg.crop_image = True
cfg.save_folder = './output/'

# Weights
cfg.w_pho = 350
cfg.w_lmks = 65
cfg.w_lmks_lid = 20
cfg.w_lmks_mouth = 80
cfg.w_lmks_iris = 4
cfg.w_lmks_oval = 3

cfg.w_exp = 0.02
cfg.w_shape = 0.5
cfg.w_tex = 0.04


def get_cfg_defaults():
    return cfg.clone()


def update_cfg(cfg, cfg_file):
    cfg.merge_from_file(cfg_file)
    return cfg.clone()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', type=str, help='Configuration file', default = './configs/actors/basic.yml', required=False)
    parser.add_argument('--input_video', type=str, help='The path to original video', required=True)
    parser.add_argument('--output_dir', type=str, help='The path to the directory where the output will be saved', required=True)

    args = parser.parse_args()
    print(args, end='\n\n')

    cfg = get_cfg_defaults()
    if args.cfg is not None:
        cfg_file = args.cfg
        cfg = update_cfg(cfg, args.cfg)
        cfg.cfg_file = cfg_file

    # cfg.config_name = Path(args.cfg).stem

    # Update cfg with args
    cfg.save_folder = args.output_dir
    cfg.actor = args.input_video

    # the name of the config file is the name of the video
    for root, dirs, files in os.walk(args.input_video):
        for file in files:
            if file.endswith(".mp4"):
                cfg.config_name = file.split('.')[0]
                break

    return cfg


def parse_cfg(cfg_file):
    cfg = get_cfg_defaults()
    cfg = update_cfg(cfg, cfg_file)
    cfg.cfg_file = cfg_file

    cfg.config_name = Path(cfg_file).stem

    return cfg
