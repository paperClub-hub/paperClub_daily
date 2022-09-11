#coding:utf-8
import os,glob,cv2,webcolors,math
from collections import Counter
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import KDTree
from skimage.color import rgb2lab, deltaE_cie76
from scipy.stats.stats import  pearsonr
from scipy.spatial.distance import cosine

def RGB2HEX(color):
	return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def kmean_rgb_feat(image, number_of_colors):
	resize_rate = 0.1
	w, h, c = image.shape
	modified_image = cv2.resize(image, (int(resize_rate * h), int(resize_rate * w)), interpolation=cv2.INTER_AREA)
	modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3)
	
	clf = KMeans(n_clusters=number_of_colors)
	labels = clf.fit_predict(modified_image)
	counts = Counter(labels)
	# sort to ensure correct color percentage
	counts = dict(sorted(counts.items()))  ### 排序
	
	center_colors = clf.cluster_centers_
	# We get ordered colors by iterating through the keys
	ordered_colors = [center_colors[i] for i in counts.keys()]
	rgb_colors = [ordered_colors[i] for i in counts.keys()]
	main_rgb_colors = rgb_colors[np.argmax(list(counts.values()))].tolist()
	main_rgb_colors = tuple(map(int,main_rgb_colors))

	return main_rgb_colors


def mean_rgb_feat(image):
	resize_rate = 0.1
	w, h, c = image.shape
	image = cv2.resize(image, (int(resize_rate * h), int(resize_rate * w)), interpolation=cv2.INTER_AREA)
	mean_b = np.mean(image[:, :, 2])
	mean_g = np.mean(image[:, :, 1])
	mean_r = np.mean(image[:, :, 0])
	main_rgb_colors = tuple([int(mean_r), int(mean_g), int(mean_b)])

	return main_rgb_colors




def get_test_colors_feats(imglist,k):
	color_feats = []
	for filename in imglist:
		image = cv2.imread(filename)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		# rgb_feat = kmean_rgb_feat(image, k) ## KDtree聚类
		rgb_feat = mean_rgb_feat(image)#### rgb平均值
		color_feats.append(rgb_feat)
		
	return color_feats


def colour_kdtree_mapping(template_rgb_colour,test_rgb_colours):
	dists = []
	### KDTree
	spacedb = KDTree([template_rgb_colour])
	
	for test_rgb_colour in test_rgb_colours:
		dist, index = spacedb.query(test_rgb_colour)
		dists.append(dist)
	return dists


def colour_O_dist_mapping(template_rgb_colour, test_rgb_colours):
	dists = []
	### rgb空间中的欧几里得距离进行匹配
	r_c, g_c, b_c = template_rgb_colour

	for test_rgb_colour in test_rgb_colours:
		rd = (r_c - test_rgb_colour[0]) ** 2
		gd = (g_c - test_rgb_colour[1]) ** 2
		bd = (b_c - test_rgb_colour[2]) ** 2
		dist = np.sqrt(rd + gd + bd)
		dists.append(dist)

	return dists

def colour_M_dist_mapping(template_rgb_colour, test_rgb_colours):
	dists = []
	### rgb马氏距离, 该方法不适用

	sum_template = sum(template_rgb_colour)

	for test_rgb_colour in test_rgb_colours:
		sum_test = sum(test_rgb_colour)
		d = 0

		for index in range(0, len(template_rgb_colour)):
			d += np.sqrt((template_rgb_colour[index] / sum_template) * (test_rgb_colour[index] / sum_test))


		dist = np.sqrt(rd + gd + bd)
		dists.append(dist)

	return dists

def colour_lab_mapping(template_rgb_colour, test_rgb_colours):
	dists = [] ###
	template_rgb_colour = rgb2lab(np.uint8(np.asarray([[template_rgb_colour]])))
	for test_rgb_colour in test_rgb_colours:
		test_rgb_colour = rgb2lab(np.uint8(np.asarray([[test_rgb_colour]])))
		diff = deltaE_cie76(template_rgb_colour, test_rgb_colour)
		dists.append(diff)
		# print(diff)

	return dists


def Lab_colourDistance(rgb, test_rgb_colours):
	dists = []  ###
	R_1,G_1,B_1 = rgb
	print(test_rgb_colours)
	for test_rgb_colour in test_rgb_colours:
		print(test_rgb_colour)
		R_2,G_2,B_2 = test_rgb_colour
		rmean = (R_1 +R_2 ) / 2
		R = R_1 - R_2
		G = G_1 -G_2
		B = B_1 - B_2
		dist =  math.sqrt((2+rmean/256)*(R**2)+4*(G**2)+(2+(255-rmean)/256)*(B**2))
		dists.append(dist)

	return dists


def colour_pearson_mapping(template_rgb_colour, test_rgb_colours):
	dists = []

	for test_rgb_colour in test_rgb_colours:
		corr = pearsonr(template_rgb_colour, test_rgb_colour)
		dists.append(corr[0])
		print(corr)

	return dists

def colour_cosine_mapping(template_rgb_colour, test_rgb_colours):
	dists = []
	### 余弦相识度
	for test_rgb_colour in test_rgb_colours:
		corr = cosine(test_rgb_colour,template_rgb_colour)
		dists.append(corr)
		# print(corr)

	return dists


def color_name2rgb_value(requested_color_name):
	try:
		rgb = webcolors.name_to_rgb(requested_color_name)
		return rgb
	except ValueError:
		print("error webcolors.name_to_rgb({})".format(requested_color_name))
		return None


def img_color_check(imglist ,color_name):
	k = 5
	template_rgb = color_name2rgb_value(color_name)
	test_rgb_colours = get_test_colors_feats(imglist,k)
	# mapping_dist = colour_kdtree_mapping(template_rgb, test_rgb_colours)### 效果一般
	# mapping_dist = colour_O_dist_mapping(template_rgb,test_rgb_colours)### 效果一般+
	# mapping_dist = colour_lab_mapping(template_rgb, test_rgb_colours) ### 效果较好
	mapping_dist = colour_pearson_mapping(template_rgb, test_rgb_colours) ### 效果较好+， 识别白色和黑色时，计算公式返回nan
	# mapping_dist = Lab_colourDistance(template_rgb,test_rgb_colours)### 效果一般++
	# mapping_dist = colour_cosine_mapping(template_rgb, test_rgb_colours)#### 较差
	
	mapping_dist_index = dict([index,dist] for index,dist in enumerate(mapping_dist))
	# mapping_dist_index = dict(sorted(mapping_dist_index.items(), key = lambda x :x[1], reverse=False))
	mapping_dist_index = dict(sorted(mapping_dist_index.items(), key=lambda x: x[1], reverse=True))## for pearson
	print(mapping_dist_index)


	top3 = list(mapping_dist_index.keys())[:]

	for i in top3:
		img_file = imglist[i]
		print("query_color= {}(rgb={}), mapping_rgb= {}, dist/corr= {} ,file={}".format(
			color_name, template_rgb, test_rgb_colours[i], mapping_dist_index.get(i),img_file))
		img = cv2.imread(img_file)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		# plt.imshow(img),plt.title("query = {}(rgb={}), mapping :\n top {}(rgb = {}) , dict={}".format(
		# 	color_name,template_rgb, top3.index(i)+1, test_rgb_colours[i], int(mapping_dist_index.get(i))))
		plt.imshow(img), plt.title("query color = {}, mapping results :\n top {}(rgb = {}) , dist/corr={:.2f}".format(
			color_name, top3.index(i) + 1, test_rgb_colours[i], mapping_dist_index.get(i)))
		plt.axis('off')
		plt.show()
	
	


imgs = glob.glob("./testimgs2/*jpg")

query_name = 'red'
img_color_check(imgs,query_name)


