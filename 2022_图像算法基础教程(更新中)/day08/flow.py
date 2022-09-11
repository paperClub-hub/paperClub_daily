import numpy as np
import cv2

# params for ShiTomasi corner detection
feature_params = dict( maxCorners = 100,
                        qualityLevel = 0.3,
                        minDistance = 7,
                        blockSize = 7 )

lk_params = dict( winSize = (15,15), maxLevel = 2,
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Create some random colors
color = np.random.randint(0,255,(100,3))
cap = cv2.VideoCapture(r'./img/a.mp4')
while (cap.isOpened()):
    ret, old_frame = cap.read()
    if ret == True:
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
        mask = np.zeros_like(old_frame)
        while(1):
            ret, frame = cap.read()
            img = frame.copy()
            frame_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
            good_new = p1[st==1]
            good_old = p0[st==1]
            # draw the tracks
            for i,(new,old) in enumerate(zip(good_new,good_old)):
                a,b = new.ravel()
                c,d = old.ravel()
                a, b = int(a), int(b)
                c, d = int(c), int(d)
                mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
                img = cv2.circle(img,(a,b),5,color[i].tolist(),-1)
            flow_img = cv2.add(img, mask)
            mat = np.vstack((frame, flow_img))
            cv2.namedWindow('OpticalFlow', 0)
            cv2.imshow('OpticalFlow', mat)
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
            # Now update the previous frame and previous points
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1,1,2)
            
cap.release()

