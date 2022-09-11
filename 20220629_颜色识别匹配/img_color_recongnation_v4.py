#coding:utf-8
import os,glob,cv2,webcolors
from collections import Counter
from sklearn.cluster import KMeans
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial import KDTree


def closest_colour_v1(requested_rgb_colour):
	### rgb空间中的欧几里得距离进行匹配
	hexnames = webcolors.css3_hex_to_names
	names = []
	colors = []
	
	for hex, name in hexnames.items():
		names.append(name)
		colors.append(webcolors.hex_to_rgb(hex))
	spacedb = KDTree(colors)
	
	dist, index = spacedb.query(requested_rgb_colour)
	min_dist = dist
	closest_name = names[index]
	# print('The color %r is closest to %s.' % (querycolor, names[index]))
	
	return min_dist, closest_name


def get_color_name(requested_rgb_colour):
	try:
		closest_name = actual_name = webcolors.rgb_to_name(requested_rgb_colour)
		min_dist = None
	except ValueError:
		min_dist, closest_name = closest_colour_v1(requested_rgb_colour)  # closest_colour(requested_rgb_colour)
		actual_name = None
	
	return closest_name, actual_name, min_dist


def RGB2HEX(color):
	return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def get_colors(image, number_of_colors, show_chart=False):
	resize_rate = 0.1
	w, h, c = image.shape
	# reszie and reshape the image to be a list of pixels
	modified_image = cv2.resize(image, (int(resize_rate * h), int(resize_rate * w)), interpolation=cv2.INTER_AREA)
	
	modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3)
	
	clf = KMeans(n_clusters=number_of_colors)
	labels = clf.fit_predict(modified_image)
	
	counts = Counter(labels)
	counts = dict(sorted(counts.items()))  ### 排序
	
	center_colors = clf.cluster_centers_
	# We get ordered colors by iterating through the keys
	ordered_colors = [center_colors[i] for i in counts.keys()]
	hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
	rgb_colors = [ordered_colors[i] for i in counts.keys()]
	
	# print(hex_colors)
	# print(counts)
	
	color_names = [get_color_name(tuple([int(j) for j in i.tolist()]))[0] for i in rgb_colors] ### ['brown', 'whitesmoke', 'brown']?
	hex_rate = ["{}".format(counts.get(i) / sum(counts.values())) for i in counts.keys()]
	colors_rate_dict = dict([color, rate] for color, rate in zip(color_names, hex_rate))
	
	colors_rate = ['{}\n({:.3f})'.format(c,float(r)) for c,r in colors_rate_dict.items()] ###
	# colors_rate = ["{} ({})".format(RGB2HEX(ordered_colors[i]),hex_rate.get(i)) for i in counts.keys()]
	# colors_rate = ["{} ({})".format(RGB2HEX(ordered_colors[i]), hex_rate.get(i)) for i in counts.keys()]
	
	colors_rate_dict = dict([color,rate] for color,rate in zip(color_names,hex_rate))
	
	closest_index = np.argmax(hex_rate)
	closest_color_name = color_names[closest_index]
	closest_color_rgb = rgb_colors[closest_index]
	closest_color_rgb = tuple(map(int,closest_color_rgb)) # tuple([int(i) for i in closest_color_rgb])
	print(closest_color_rgb)
	
	if (show_chart):
		plt.figure(figsize=(8, 6))
		plt.subplot(121)
		# plt.imshow(image),plt.axis('off')
		plt.imshow(image), plt.title("predict: {}\n(rgb = {})".format(closest_color_name, closest_color_rgb)), plt.axis('off')
		plt.subplot(122)
		plt.pie(counts.values(), labels=hex_colors, colors=hex_colors)
		# plt.pie(counts.values(), labels=colors_rate, colors=hex_colors)
		plt.show()
	
	return rgb_colors



imgs = glob.glob("./testimgs/*jpg")

for imgfile in imgs:
	print(imgfile)
	image = cv2.imread(imgfile)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	get_colors(image, 3, show_chart=True)
	