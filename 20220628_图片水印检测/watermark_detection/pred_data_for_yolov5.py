import os,glob
import random
import shutil


def convert_box_to_train_set(point_txt, img_dir, lable_outdir, dataset_root):
	CLASSES = ['logo']
	
	if not os.path.exists(dataset_root): os.mkdir(dataset_root)
	def convert(size, box):
		dw = 1. / size[0]
		dh = 1. / size[1]
		x = (box[0] + box[1]) / 2.0
		y = (box[2] + box[3]) / 2.0
		w = box[1] - box[0]
		h = box[3] - box[2]
		x = x * dw
		w = w * dw
		y = y * dh
		h = h * dh
		return (x, y, w, h)
	
	def data_copy(sample_list,save_dir):
		for filePath in sample_list:
			savePath = os.path.join(save_dir, os.path.basename(filePath))
			shutil.copy(filePath,savePath)
			if not os.path.exists(savePath):
				print("{} --> {}".format(filePath, savePath))
		
	
	def split_data(labeltext_dir, image_dir, save_root):
		
		val_rate = 0.2
		labelFiles = glob.glob(labeltext_dir + "/*.txt")
		imageFiles = glob.glob(image_dir + "/*.jpg")
		sample_ids = [os.path.splitext(os.path.basename(filename))[0] for filename in labelFiles]
		val_num = int(len(sample_ids) * val_rate)
		val_samples = random.sample(sample_ids,val_num)
		val_labels = [file_path for file_path in labelFiles if os.path.splitext(os.path.basename(file_path))[0] in val_samples ]
		val_images = [file_path for file_path in imageFiles if os.path.splitext(os.path.basename(file_path))[0] in val_samples ]
		
		train_samples = [i for i in sample_ids if i not in val_samples]
		train_labels = [file_path for file_path in labelFiles if os.path.splitext(os.path.basename(file_path))[0] in train_samples]
		train_images = [file_path for file_path in imageFiles if os.path.splitext(os.path.basename(file_path))[0] in train_samples]
		
		
		label_train_dir = os.path.join(save_root,"labels/train")
		label_val_dir = os.path.join(save_root, "labels/val")
		image_train_dir = os.path.join(save_root, "images/train")
		image_val_dir = os.path.join(save_root, "images/val")
		
		if not os.path.exists(label_train_dir):os.makedirs(label_train_dir)
		if not os.path.exists(label_val_dir): os.makedirs(label_val_dir)
		if not os.path.exists(image_train_dir): os.makedirs(image_train_dir)
		if not os.path.exists(image_val_dir): os.makedirs(image_val_dir)
		
		data_copy(val_labels,label_val_dir)
		data_copy(train_labels, label_train_dir)
		data_copy(val_images, image_val_dir)
		data_copy(train_images, image_train_dir)
		
		
		
		
		
		
	
	def point_to_text(point_txt,out_dir):
		with open(point_txt,'r') as f:
			for line in f.readlines():
				line = line.strip()
				ele = line.split("\t")
				info = ele[1].split(',')
				
				imgName = ele[0]
				roi_box = [int(info[0]), int(info[2]), ### x1,x2
						   int(info[1]), int(info[3]) ### y1,y2
						   ]
				
				image_size = (int(info[-1]),int(info[-2]))
				bb = convert(image_size, roi_box)
				
				label_id = 0
				outline = str(label_id) + " " + " ".join([str(a) for a in bb])
				print(outline)
				
				saveFile = os.path.join(out_dir, os.path.basename(os.path.splitext(imgName)[0] + ".txt"))
				print(outline,file=open(saveFile,'a'))
	
	
	point_to_text(point_txt, lable_outdir)
	split_data(lable_outdir, img_dir, dataset_root)
	
			
label_outdir = 'labels/'
img_dir = 'images/'
dataset_root = r'watermark_data\voc\yolo'
convert_box_to_train_set('images/points.txt', img_dir, label_outdir, dataset_root)