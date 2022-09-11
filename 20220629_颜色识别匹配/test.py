#coding:utf-8

###### 图像颜色识别:


##### skl-kmeans
import os, codecs
import cv2,glob
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from sklearn import metrics
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
imgDir= "./testimgs/"
imgList = glob.glob(imgDir+"/*.jpg")


def cv_kmeans_show(imgfile):
    """
    显示颜色聚类结果,https://blog.csdn.net/FontThrone/article/details/72330737
    :param imgfile:
    :return:
    """
    
    img = cv2.imread(imgfile)
    w,h = img.shape[:2]
    print(img.shape)
    rate = 0.5
    img = cv2.resize(img,(int(h*rate),int(w*rate)))
    print(img.shape)
    Z = img.reshape((-1,3))
    # convert to np.float32
    Z = np.float32(Z)
    j =0
    # define criteria, number of clusters(K) and apply kmeans()
    ## 这是迭代终止准则:type(A = TERM_CRITERIA_EPS 按照精度终止,B = TERM_CRITERIA_MAX_ITER,按照迭代次数终止,A+B 满足任一条件时终止)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    Klist = [1,2,4,6,8,10]
    for i in Klist:
        ret,label,center=cv2.kmeans(Z,i,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
        j +=2
        # Now convert back into uint8, and make original image
        center = np.uint8(center)
        res = center[label.flatten()]
        res2 = res.reshape((img.shape))
        # result = np.hstack([img,res2])
        # # cv2.imshow(str(("spaceship K=",i)), res2)
        # cv2.namedWindow(str(("spaceship K=", i)), 0)
        # cv2.imshow(str(("spaceship K=", i)), result)
        # cv2.waitKey(0)
        
        print(center)
        
        # Now separate the data, Note the flatten()
        fig, ax = plt.subplots(2,2,figsize=(14, 7))
        
        A = Z[label.ravel() == 0]
        B = Z[label.ravel() == 1]
        
        # print(A)
        # print(A[:, 0])
        # Now plot 'A' in red, 'B' in blue, 'centers' in yellow
        ### 直方图
        ax[0,0].hist(A[:, 0], 256, [0, 256], color='r')
        ax[0,0].hist(B[:, 0], 256, [0, 256], color='b')
        ax[0,0].hist(center[:, 0], 32, [0, 256], color='y')
        
        
        
        # Plot the data
        ax[0,1].scatter(A[:, 0], A[:, 1])
        ax[0,1].scatter(B[:, 0], B[:, 1], c='r')
        ax[0,1].scatter(center[:, 0], center[:, 1], s=80, c='y', marker='s')
        # ax[0,1].set_ylabel("Height"),ax[1].set_xlabel("Weight")

        ax[1,0].imshow(img[:,:,::-1])
        ax[1,1].imshow(res2[:,:,::-1])
        
        plt.title('k = {}'.format(i))
        plt.show()
        
    
# cv_kmeans_show(imgList[1])




# ############## 
from skimage.exposure import rescale_intensity
from skimage.segmentation import slic
from skimage.util import img_as_float
from skimage import io
import numpy as np
import cv2,scipy
import scipy.cluster.hierarchy as sch
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans



def rgb_cluster(imgfile):
    
    # 读入图片
    oimage = cv2.imread(imgfile)

    # 将图片缩放至[150,200]，降低聚类的复杂度，提高运行速度
    img_szie = 100
    orig = cv2.resize(oimage,(img_szie,img_szie),interpolation=cv2.INTER_CUBIC)

    # 初始化显示模块
    vis = np.zeros(orig.shape[:2],dtype="float")
    # 定义图片剪切范围的起点
    x,y = 0,0
    # 剪切图片
    points = np.array(orig[x:,y:,:])
    points.shape=((orig.shape[0]-x)*(orig.shape[1]-y),3)
    # print (points.shape)


    # 级联聚类
    disMat = sch.distance.pdist(points,'euclidean')
    Z = sch.linkage(disMat,method='average')
    cluster = sch.fcluster(Z,t=1,criterion='inconsistent')
    
    # 输出每个元素的类别号
    print ("original cluster by hierarchy clustering:\n:",cluster)
    print (cluster.shape)

    # 找出含有元素数目最多的类别
    cluster_tmp=cluster
    print("max value: ",np.max(cluster))
    count = np.bincount(cluster)
    # print(count)
    
    #index = np.argmax(count)
    count[np.argmax(count)]=-1
    #count[np.argmax(count)]=-1 # 此每多运行n次，就是取含元素数目第n+1多的类别
    
    
    print("max count value: ",np.argmax(count))
    cluster_tmp.shape=([orig.shape[0]-x,orig.shape[1]-y])

    # 将相应类别的点映射到vis矩阵中
    vis[cluster_tmp == np.argmax(count)] = 1

    vis.shape=[orig.shape[0]-x,orig.shape[1]-y]
    # 为了方便opencv显示，我们需要将vis数值归一化到0-255的整形
    vis = rescale_intensity(vis, out_range=(0,255)).astype("uint8")
    vis = cv2.resize(vis,(oimage.shape[1],oimage.shape[0]))
    contours, hierarchy = cv2.findContours(vis,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)


    cv2.drawContours(oimage,contours, -1,(255,255,255),3)

    # 图片显示
    cv2.imshow("Input",oimage) # 显示原图
    orig_cut = points
    orig_cut.shape=(orig.shape[0]-x,orig.shape[1]-y,3)

    
    # 显示剪切图
    cv2.imshow("cut",cv2.resize(orig_cut,(oimage.shape[1],oimage.shape[0]),interpolation=cv2.INTER_CUBIC))
    cv2.imshow("vis",cv2.resize(vis,(oimage.shape[1],oimage.shape[0]),interpolation=cv2.INTER_CUBIC))
    cv2.waitKey(0)


# rgb_cluster(imgList[1])



def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()

    # return the histogram
    return hist


def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0
    
    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        print(percent, color)
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar

def show_color_fre(hist,cluster_centers_):
    """
    :param hist: 颜色直方图
    :param cluster_centers_: kmeans结果
    :return: 颜色示例图, 最大比例颜色值(b,g,r)和最大比例
    """
    zipped = zip(hist, cluster_centers_)
    zipped = sorted(zipped,reverse=True, key=lambda x: x[0])
    hist, cluster_centers_ = zip(*zipped)
    # print(hist)
    bar = np.zeros((20, 300, 3), dtype="uint8")
    startX = 0
    for (percent, color) in zip(hist, cluster_centers_):
        endX = startX + (percent * 300)
        print(color)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),color.astype("uint8").tolist(), -1)
        startX = endX
    
    # cv2.imshow("result",bar)
    # cv2.waitKey(0)
    return bar, cluster_centers_[0], hist[0] ## 直方图, 最大比例的颜色(b,g,r)和最大比例

def rgb_mean_std(mat):
    
    ### 均值
    mean_b = np.mean(mat[:, :, 0])
    mean_g = np.mean(mat[:, :, 1])
    mean_r = np.mean(mat[:, :,2])
    
    ### 中位数
    
    median_b = np.median(mat[:, :, 0])
    median_g = np.median(mat[:, :, 1])
    median_r = np.median(mat[:, :, 2])
    
    ### 方差
    std_b = np.std(mat[:, :, 0])
    std_g = np.std(mat[:, :, 1])
    std_r = np.std(mat[:, :, 2])
    
    pixel_mean  = [mean_b, mean_g, mean_r]
    pixel_median = [median_b, median_g, median_r]
    pixel_std = [std_b, std_g, std_r]

    mean_bar = np.zeros((20, 300, 3), dtype="uint8")
    median_bar = np.zeros((20, 300, 3), dtype='uint8')
    
    
    cv2.rectangle(mean_bar, (0, 0), (300, 50), np.array(pixel_mean).astype("uint8").tolist(), -1)
    cv2.rectangle(median_bar, (0, 0), (300, 50), np.array(pixel_median).astype("uint8").tolist(), -1)
    
    return pixel_mean,pixel_median,pixel_std,mean_bar,median_bar


def rgb_mean_std_v1(mat):
    ### 均值
    b,g,r = cv2.split(mat)
    
    b = [i for row in b.tolist() for i in row if (i<250 and i!=0)]
    g = [i for row in g.tolist() for i in row if (i<250 and i != 0)]
    r = [i for row in r.tolist() for i in row if (i<250 and i != 0)]
    
    mean_b = np.mean(b)
    mean_g = np.mean(g)
    mean_r = np.mean(r)

    median_b = np.median(b)
    median_g = np.median(g)
    median_r = np.median(r)

    std_b = np.std(b)
    std_g = np.std(g)
    std_r = np.std(r)

    pixel_mean = [mean_b, mean_g, mean_r]
    pixel_median = [median_b, median_g, median_r]
    pixel_std = [std_b, std_g, std_r]
    
    mean_bar = np.zeros((20, 300, 3), dtype="uint8")
    median_bar = np.zeros((20, 300, 3), dtype='uint8')

    cv2.rectangle(mean_bar,  (0, 0),  (300, 50),  np.array(pixel_mean).astype("uint8").tolist(), -1)
    cv2.rectangle(median_bar, (0, 0), (300, 50), np.array(pixel_median).astype("uint8").tolist(), -1)
    
    return pixel_mean, pixel_median, pixel_std, mean_bar, median_bar
    
    
    

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))


def get_colors(image, number_of_colors, show_chart=False):
    modified_image = cv2.resize(image, (600, 400), interpolation=cv2.INTER_AREA)
    modified_image = modified_image.reshape(modified_image.shape[0] * modified_image.shape[1], 3)
    
    clf = KMeans(n_clusters=number_of_colors)
    labels = clf.fit_predict(modified_image)
    
    counts = Counter(labels)### 转化为dict, Counter({1: 170282, 0: 54192, 2: 15526})
    # print(counts)
    # sort to ensure correct color percentage
    counts = dict(sorted(counts.items())) ### 排序
    
    
    center_colors = clf.cluster_centers_
    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]) for i in counts.keys()]
    # print(hex_colors)
    
    
    rgb_colors = [ordered_colors[i] for i in counts.keys()]
    
    if (show_chart):
        plt.figure(figsize=(8, 6))
        plt.pie(counts.values(), labels=hex_colors, colors=hex_colors)
        plt.show()
    
    return rgb_colors

def cal_color_diff(color1,color2):
    R1, G1, B1 = color1
    R2, G2, B2 = color2
    
    difference = np.sqrt(np.square(R1 - R2) + np.square(G1 - G2) + np.square(B1 - B2))
    
    return difference


def skl_kmeans(imgfile,k):
    # COLORS = {
    #     'GREEN':  [0,  128,  0],
    #     'BLUE':   [0,  0,  128],
    #     'YELLOW': [255, 255, 0],
    #     'BLACK': [0, 0, 0],
    #     'RED': [255, 0, 0],
    #     'WHITE':  [255, 255, 255]
    # }
    #

    COLORS = {
        'GREEN': [0, 255, 0],
        'BLUE': [0, 0, 255],
        'YELLOW': [255, 255, 0],
        'RED': [255, 0, 0],
        'WHITE': [255, 255, 255]
    }

    # load the image and show it
    image_base = cv2.imread(imgfile)
    print(image_base.shape)
    # reshape the image to be a list of pixels
    image = image_base.reshape((image_base.shape[0] * image_base.shape[1], 3))
    
    # k = 3 #聚类的类别个数
    iterations = 4 #并发数4
    iteration = 200 #聚类最大循环次数
    clt = KMeans(n_clusters = k, n_jobs = iterations, max_iter = iteration)
    clt.fit(image)
    
    hist = centroid_histogram(clt)#### 分布直方图频率，即每种的比例，颜色为clt.cluster_centers_
    # bar = plot_colors(hist, clt.cluster_centers_) ### 每种颜色的直方图
    # # show our color bart
    # fig = plt.figure()
    # ax = fig.add_subplot(211)
    # ax.imshow(image_base[:,:,::-1])##ax.imshow(image_base)
    # ax = fig.add_subplot(212)
    # ax.imshow(bar[:,:,::-1])
    # plt.show()

    # mean_color,median_color, std_color, mean_bar,median_bar = rgb_mean_std(image_base)
    mean_color, median_color, std_color, mean_bar, median_bar = rgb_mean_std_v1(image_base)
    
    
    
    pre_labels = np.unique(clt.labels_)
    # pre_labels_count = np.bincount(clt.labels_)
    pre_labels_count2 = [clt.labels_.tolist().count(i) for i in pre_labels]
    pre_labels_count2 = [i / sum(pre_labels_count2) for i in pre_labels_count2]  ### 等同hist

    kmeans_bar, most_color,rate = show_color_fre(hist, clt.cluster_centers_)
    most_color = most_color.tolist()
    b,g,r = most_color
    b, g, r = int(b),int(g),int(r)
    
    #### 计算颜色相似度
    top_num_color = k
    image_rgb = cv2.cvtColor(image_base, cv2.COLOR_BGR2RGB)
    image_colors = get_colors(image_rgb, k)### 聚类获取颜色的 rgb颜色
    
    #target_colors_dict = dict([color_name, rgb2lab(np.uint8(np.asarray([[color]])))] for color_name in COLORS.keys())## rgb2lab(np.uint8(np.asarray([['GREEN']]))) 将颜色转化为数组

    target_color_dict = {}
    for i in range(top_num_color):
        curr_color = rgb2lab(np.uint8(np.asarray([[image_colors[i]]])))
        
        for color_name in COLORS.keys():
            temp_color = rgb2lab(np.uint8(np.asarray([[COLORS[color_name]]])))
            diff = deltaE_cie76(temp_color, curr_color)
            diff = diff[0].tolist()[0]
            # print(diff)
            
            
            if color_name not in target_color_dict:
                target_color_dict[color_name] = diff
            else:
                color_diff = target_color_dict[color_name]
                if diff < color_diff:
                    target_color_dict[color_name] = diff
    
    target_color_dict = dict(sorted(target_color_dict.items(),key=lambda x:x[1],reverse=False))
    print(target_color_dict)
    
    pred_img_color = sorted(target_color_dict.items(),key=lambda x:x[1], reverse=False)[0]
    print(pred_img_color)
    
    
    
    plt.figure()

    plt.subplot(121)
    plt.imshow(image_base[:, :, ::-1]), plt.title("input image"), plt.axis('off')

    plt.subplot(322)
    text = "k-means color legend [top 1 ({:.2f}): r={}, g={}, b={}]".format(rate, r,g,b)
    plt.imshow(kmeans_bar[:,:,::-1]),plt.title(text), plt.axis('off')

    plt.subplot(324)
    mean_text = "mean color legend [ r={}, g={}, b={}]".format(int(mean_color[-1]),int(mean_color[1]),int(mean_color[0]))
    plt.imshow(mean_bar[:, :, ::-1]), plt.title("mean color legend"), plt.title(mean_text),plt.axis('off')
    plt.subplot(326)
    median_text = "median color legend [ r={}, g={}, b={}]".format(int(median_color[-1]), int(median_color[1]),int(median_color[0]))
    plt.imshow(median_bar[:, :, ::-1]), plt.title("median color legend"), plt.title(median_text), plt.axis('off')

    plt.show()
    #


print(imgList)
# skl_kmeans(imgList[4], 5)

# get_colors(cv2.imread(imgList[9])[:,:,::-1],3,True)
for i in imgList:
    skl_kmeans(i, 3)