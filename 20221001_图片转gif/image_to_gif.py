#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from glob import glob
import imageio

def compose_gif(images: list, save_gif:str, fps:int=1):
    
    gif_images = []
    for path in images:
        gif_images.append(imageio.imread(path))
    imageio.mimsave(save_gif,gif_images,fps=fps)


imgs = glob("L3/*.jpg")
save_gif = '1.gif'
compose_gif(imgs, save_gif, fps=2)