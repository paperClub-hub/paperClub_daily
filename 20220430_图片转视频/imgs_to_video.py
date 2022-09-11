##!/usr/bin/python
# -*- coding: utf-8 -*-

import cv2
import glob,os
import numpy as np
import imageio
import argparse

def pad(image, min_height, min_width):
    """ 边填充 """
    h,w,_ = image.shape
    """ 图片边填充 """
    if h < min_height:
        h_pad_top = int((min_height - h) / 2.0)
        h_pad_bottom = min_height - h - h_pad_top
    else:
        h_pad_top = 0
        h_pad_bottom = 0
    if w < min_width:
        w_pad_left = int((min_width - w) / 2.0)
        w_pad_right = min_width - w - w_pad_left
    else:
        w_pad_left = 0
        w_pad_right = 0

    return cv2.copyMakeBorder(image, h_pad_top,
                              h_pad_bottom,
                              w_pad_left, w_pad_right,
                              cv2.BORDER_CONSTANT,
                              value=(255, 255, 255))


def video_save(cap, save_path, is_show=False):
    """ 视频保存 """
    fps = 10.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') ### 保存格式
    out = cv2.VideoWriter(save_path, fourcc, fps, (width, height))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # frame = cv2.flip(frame,0)
            out.write(frame)

            if is_show:
                cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    # cap.release()
    out.release()


def imgs_to_video(imgs, save_path, is_show=False):
    """ 图片保存为视频 """
    fps = 33.0
    limit_h, limit_w = 480, 640
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') ### 保存格式
    out = cv2.VideoWriter(save_path, fourcc, fps, (limit_w, limit_h))

    for i, imgfile in enumerate(imgs):
        print(imgfile)
        img = cv2.imread(imgfile)
        h, w, _ = img.shape
        r = max(limit_h, limit_w) / max(h, w)
        W, H = int(r * w), int(r * h)
        frame = pad(cv2.resize(img, (W, H), cv2.INTER_AREA), limit_h, limit_w )
        # frame = cv2.resize(img, (W, H), cv2.INTER_AREA)

        cv2.putText(frame, f"papaerClub-{i+1}", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.rectangle(frame, (0, 0), (limit_w -2, limit_h - 2), (0, 110, 255), 2) ### 添加窗口线

        if is_show:
            cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        out.write(frame)

    out.release()


def ims_to_gif(imgs, save_path, duration=0.1):
    """ imgs 转gif """
    frames = []

    for image in imgs:
        gimg = imageio.imread(image)
        frames.append(gimg)

    imageio.mimsave(save_path, frames, 'GIF', duration=duration)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--img_dir", '-d', default='./wuxia')
    parser.add_argument("--type", '-t', choices=['gif', 'video'], default='video')
    parser.add_argument("--out", '-o', default='./')
    args = parser.parse_args()
    img_dir = args.img_dir
    out_dir = args.out
    out_type = args.type

    imgfiles = glob.glob( img_dir + "/*")

    if out_type == "video":
        save_path = os.path.join(out_dir, "imgs.mp4")
        imgs_to_video(imgfiles, save_path, True)
    elif out_type == "gif":
        save_path = os.path.join(out_dir, "imgs.gif")
        ims_to_gif(imgfiles, save_path, duration=1.0)


