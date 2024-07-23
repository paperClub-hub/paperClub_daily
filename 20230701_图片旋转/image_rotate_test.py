import os, cv2
import matplotlib.pyplot as plt
import numpy as np


def rotate_bound(image, angle):
	(h, w) = image.shape[:2]
	(cX, cY) = (w // 2, h // 2)
	
	M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
	cos = np.abs(M[0, 0])
	sin = np.abs(M[0, 1])
	
	# compute the new bounding dimensions of the image
	nW = int((h * sin) + (w * cos))
	nH = int((h * cos) + (w * sin))
	
	M[0, 2] += (nW / 2) - cX
	M[1, 2] += (nH / 2) - cY
	
	# cv2.imshow('image', image)
	# cv2.waitKey(0)
	return cv2.warpAffine(image, M, (nW, nH))


def crop_rotated_img(rotated_img, W, H):
	gray = cv2.cvtColor(rotated_img, cv2.COLOR_BGR2GRAY)
	gray_blurred = cv2.blur(gray, (3, 3))
	w, h = gray.shape
	
	### 关键步骤： max_r 理论可以设为0，但不能大于 max（w,h)
	max_r = int(0.5 * max(W, H))
	detected_circles = cv2.HoughCircles(gray_blurred, cv2.HOUGH_GRADIENT, 1, 20,
										param1=50, param2=30, minRadius=int(0.5 * max_r), maxRadius=max_r)
	
	try:  ### 判断寻找圆结果
		detected_circles = np.uint16(np.around(detected_circles))
		
		circles_sorted = sorted(detected_circles[0], key=lambda x: x[2], reverse=True)
		
		x, y, r = circles_sorted[0]
		
		mask = np.zeros((w, h), dtype=np.uint8)
		result = mask.copy()
		result = ~result
		result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
		binary = mask
		cv2.circle(mask, (x, y), r, (255, 255, 255), -1, 8, 0)
		
		for i in range(w):
			for j in range(h):
				if binary[i, j] == 255:  # roi区域
					result[i, j] = rotated_img[i, j]  ## 抠图，为了安全没有使用轮廓检测。
		
		# 保持形状一致
		x1 = int(0.5 * w - 0.5 * W)
		y1 = int(0.5 * h - 0.5 * H)
		y2 = y1 + W
		x2 = x1 + H
		
		finial = result[y1:y2, x1:x2]
		
		return finial
	
	except:
		print('请检查找圆参数 ！')
		return rotated_img


def image_process(test_in, angle):
	filename = os.path.splitext(os.path.basename(test_in))[0]
	save_file = filename + "_rotated-{}.png".format(angle)
	img = cv2.imread(test_in)
	w, h, _ = img.shape
	
	rotated_img = rotate_bound(img, angle)
	result = crop_rotated_img(rotated_img, w, h)
	
	cv2.imwrite(save_file, result)
	cv2.imshow('input', img)
	cv2.imshow('rotated:{}'.format(angle), rotated_img)
	cv2.imshow('result', result)
	
	cv2.waitKey(0)


if __name__ == '__main__':
	test_in = "./test.jpg"
	angle = 77
	image_process(test_in, angle)
	
	cv2.destroyAllWindows()