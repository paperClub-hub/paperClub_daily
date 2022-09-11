import os,cv2
import numpy as np
import random,json
import glob
from tqdm import tqdm



def add_watermark2(point, water_mark, img_mat, alpha = 0.25):
	
	(X, Y) = point
	H, W = img_mat.shape[:2]
	logo_h, logo_w = water_mark.shape[:2]
	x1, x2 = X, X + logo_w
	y1, y2 = Y, Y + logo_h
	
	src, box = None, None
	
	if x2 < W and y2 < H:
		
		box = [x1,y1,logo_w,logo_h]
		image = np.dstack([img_mat, np.ones((H, W), dtype="uint8") * 255])  ### 4通道
		overlay = np.zeros((H, W, 4), dtype="uint8")  ### 4通道
		
		overlay[y1: y2, x1: x2] = water_mark
		
		src = image.copy()
		cv2.addWeighted(overlay, alpha, src, 0.8, 0.8, src)
		
		# cv2.imshow("logo_on", src)
		# cv2.waitKey()
	
	return src,box


def remove_bg(waterFile, imgFile):
	water_mat = cv2.imread(waterFile)
	img_mat = cv2.imread(imgFile)
	H, W = img_mat.shape[:2]
	X, Y = (50, 50)
	
	gray = cv2.cvtColor(water_mat, cv2.COLOR_BGR2GRAY)
	
	# 像素翻转
	thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)[1]
	(h, w) = thresh.shape
	
	thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
	water_mark = np.dstack([thresh, np.ones((h, w), dtype="uint8") * 255])
	
	# print(water_mark.shape)
	
	image = np.dstack([img_mat, np.ones((H, W), dtype="uint8") * 255])  ### 4通道
	overlay = np.zeros((H, W, 4), dtype="uint8")  ### 4通道
	
	x1, x2 = X, X + w
	y1, y2 = Y, Y + h
	
	overlay[y1: y2, x1: x2] = water_mark
	
	alpha = 0.5
	src = image.copy()
	cv2.addWeighted(overlay, alpha, src, 0.8, 0.8, src)
	cv2.imshow("src", src)
	cv2.waitKey()
	
	return water_mark


def remove_bg_add_watermark(point, water_mark, img_mat, alpha = 0.25):
	(X, Y) = point
	H, W = img_mat.shape[:2]
	
	def remove_bg(water_mat):
		gray = cv2.cvtColor(water_mat, cv2.COLOR_BGR2GRAY)
		# 像素翻转
		thresh = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)[1]
		(h, w) = thresh.shape
		
		thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
		water_mark = np.dstack([thresh, np.ones((h, w), dtype="uint8") * 255])
		
		return water_mark
	
	
	logo_h, logo_w = water_mark.shape[:2]
	x1, x2 = X, X + logo_w
	y1, y2 = Y, Y + logo_h
	
	src, box = None, None
	water_mark_bg = remove_bg(water_mark)
	if x2 < W and y2 < H:
		box = [x1, y1, logo_w, logo_h]
		image = np.dstack([img_mat, np.ones((H, W), dtype="uint8") * 255])  ### 4通道
		overlay = np.zeros((H, W, 4), dtype="uint8")  ### 4通道
		
		overlay[y1: y2, x1: x2] = water_mark_bg
		
		src = image.copy()
		cv2.addWeighted(overlay, alpha, src, 0.8, 0.8, src)
	
	# cv2.imshow("logo_on", src)
	# cv2.waitKey()
	
	return src,box

def random_points(log_mark,image):
	num_point = 1
	h, w = image.shape[:2]
	log_h, hog_w = log_mark.shape[:2]
	
	points = [(x,y) for x in range(10, w, 20) for y in range(10, h, 20) if x + hog_w < w and y + log_h < h]
	points = random.sample(points, num_point)
	points = points[0]
	# print(points)
	
	return points

def cv_resize(log_mark, min_height, min_width):
	h, w, _ = log_mark.shape
	
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
	
	return cv2.copyMakeBorder(log_mark, h_pad_top, h_pad_bottom, w_pad_left, w_pad_right,
							  cv2.BORDER_CONSTANT,value=(255, 255, 255))


def get_watermaskImg(logoFile,srcFile,saveDir):
	# logFile = os.path.join(saveDir, "points.json")
	random_number = random.randint(2, 12)
	log_mark = cv2.imread(logoFile, cv2.IMREAD_UNCHANGED)
	image = cv2.imread(srcFile)
	log_h,hog_w = log_mark.shape[:2]
	
	if random_number %2 ==0:
		print("OOOO")
		resize_factor = random_number / 10  #### 产生随机缩放系数，进行图像大小调整
		targe_size = int(min(log_h, hog_w) * resize_factor)
		log_mark = cv_resize(log_mark, targe_size, targe_size)
		# cv2.imshow("log_mark", log_mark)
		# cv2.waitKey()
	
	point = random_points(log_mark, image)
	alpha = random_number/12.0
	
	# waterMark,Box = add_watermark2(point, log_mark, image, alpha)
	waterMark, Box = remove_bg_add_watermark(point, log_mark, image, alpha)
	
	
	h, w = waterMark.shape[:2]
	
	
	if waterMark is not None:
		# cv2.imshow("waterMark",waterMark)
		# cv2.waitKey()
		
		saveFile = os.path.join(saveDir, os.path.splitext(os.path.basename(srcFile))[0]
								+ "_{}_{}_{}".format(random_number,point[0],point[0]) + ".jpg")
		
		cv2.imwrite(saveFile, waterMark)
		
		filename = os.path.basename(saveFile)
		
	else:
		filename, Box = None, None
		
	return filename,Box, h,w
	





# logoFile = "watermark_logo/lianjia.png"
# srcFile = "sourc_imgs/00000096.jpg"
# saveDir = "images/"
# # get_watermaskImg(logoFile,srcFile,saveDir)
#
# water_mark = cv2.imread(logoFile,cv2.IMREAD_UNCHANGED)
# img_mat = cv2.imread(srcFile)
#
# remove_bg_add_watermark((50,50), water_mark, img_mat)

# a = remove_bg(logoFile,srcFile)
# cv2.imshow("a",a)
# cv2.waitKey()

logoFiles = glob.glob('watermark_logo/*')
srcFiles = glob.glob("sourc_imgs/*")
saveDir = "images/"






for srcFile in tqdm(srcFiles):
	logFile = os.path.join(saveDir, "points.txt")
	result = {}
	for logoFile in logoFiles:
		print("{} --> {}".format(srcFile,logoFile))
		filename,box,h,w = get_watermaskImg(logoFile, srcFile, saveDir)
		
		if filename:
			result[filename] = box + [h,w]

		filename2,box2,h2,w2 = get_watermaskImg(logoFile, srcFile, saveDir)
		if filename2:
			result[filename2] = box2 + [h2,w2]

		filename3, box3, h3, w3 = get_watermaskImg(logoFile, srcFile, saveDir)
		if filename3:
			result[filename3] = box3 + [h3, w3]

	for ele in result:
		line = ele + "\t" + ",".join([str(i) for i in  result.get(ele)])
		print(line,file=open(logFile,"a"))


# with open("images/points.txt",'r',encoding='utf-8') as f:
# 	for line in f.readlines():
# 		print(line.strip())




def text_to_json():

	import json
	with open(r"F:\NSFW\watermark_detection\images\points.txt",'r') as f:

		result = []
		for line in f.readlines():
			line = line.strip()
			ele = line.split('\t')
			# print(line)
			filename = ele[0]
			info = ele[1].split(',')

			x = float(info[0])
			y = float(info[1])
			width = float(info[2])
			height = float(info[3])
			labelname = 'logo'
			labeltype = 'rect'


			roi_annotation = {
				"class": labelname,
				"height": height,
				"type": labeltype,
				"width": width,
				"x": x,
				"y": y
			}

			annotations = {
				"annotations": [roi_annotation],
				"class": "image",
				"filename": filename
			}


			result.append(annotations)

		print(result)
		with open("points.json",'a') as f:
			json.dump(result,f)


# text_to_json()