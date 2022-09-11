
#### lession3: 从零学AI之图像算法3：使用 opencv 进行图片颜色转换


RGB色彩就是常说的三原色，R代表Red（红色），G代表Green（绿色），B代表Blue（蓝色）。
自然界中肉眼所能看到的任何色彩都可以由这三种色彩混合叠加而成，因此也称为加色模式。

在计算机当中，颜色处理在计算机图形学中，一个RGB颜色模型的真彩图形，也是由红、绿、蓝
三个色彩信息通道合成的， 每个通道用了8位色彩深度，共计24位，也就是 2<sup>24</sup> = 16777216
种颜色，它可以达到人眼分辨的极限，包含了所有彩色。 

OpenCV中有数百种关于在不同色彩空间之间转换的方法,常用的色彩空间：灰度、BGR以及
HSV (Hue, Saturation, Value)等转换。

## 不同颜色转换：
>- 灰度色彩空间是通过去除彩色信息来将其转换成灰阶，灰度色彩空间对中间处理特别有效，
   比如人脸检测。
>- BGR，即蓝一绿一红色彩空间，每一个像素点都由一个三元数组来表示，分别代表蓝、绿、
   红三种颜色。 网页开发者可能熟悉另一个与之相似的颜色空间：RGB，它们只是在颜色
   的顺序上不同。
>- HSV, H(Hue）是色调，S(Saturation）是饱和度，V(Value）表示黑暗的程度
   （或光谱另一端的明亮程度）。


上次介绍了通过opencv进行颜色转换，主要用到了cv2.cvtColor 和 cv2.inRange和个方法。我们先来回过一下最基本的使用方法：

cv2.cvtColor 和 cv2.inRange：
flags = [x for x in dir(cv2) if x.startswith("COLOR_") ]
print(len(flags), flags)
函数cv2.cvtColor(input_image ，flag)，flag是转换类型，也就是颜色转换的方法，我们发现有204种已经集成好的方法; input_image 是数组图片，即 cv2.imread结果。具体使用：

例如：

BGR和灰度图的转换使用 cv2.COLOR_BGR2GRAY
BGR和HSV的转换使用 cv2.COLOR_BGR2HSV

### 代码示例：
src = cv2.imread('src/imgs/xx.jpg')
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) ## bgr -> gray
gray2 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) ## gray -> bgr
hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV) ## bgr -> hsv
luv = cv2.cvtColor(src, cv2.COLOR_BGR2LUV) ## bgr -> luv
result = np.vstack((
            np.hstack((src, gray2)),
            np.hstack((hsv, luv)),
        ))

cv2.namedWindow("result", 0)
cv2.imshow('result', result)
cv2.waitKey(0)
颜色转换的结果：

从零学AI之图像算法3：使用 opencv 进行图片颜色转换2


函数：cv2.inRange(hsv, low, high)， 函数很简单，参数有三个，hsv指的是原图，low指的是把图像中低于这个low的值变为0，high指的是把图像中高于这个high的值变为0。cv2.inRange()在这里主要是用来根据设定阈值范围生成掩模，根据掩模再与原图像进行按位与运算。为了查找方便，附上各个颜色与其对应的HSV值：

从零学AI之图像算法3：使用 opencv 进行图片颜色转换2

src = cv2.imread('src/imgs/3.jpg')
hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV) ## bgr -> hsv
red_lower = np.array([0, 43, 46])
red_upper = np.array([10, 255, 255])

mask_red = cv2.inRange(hsv, red_lower, red_upper) ### 获得红色的掩膜图
red = cv2.bitwise_and(src, src, mask=mask_red) ### 图像逻辑计算

result = np.hstack((src, red))
cv2.namedWindow("red", 0)
cv2.imshow('red', result)
cv2.waitKey(0)
从零学AI之图像算法3：使用 opencv 进行图片颜色转换2
可以看到，我们顺利提取到了红色。再来挑战一下色卡：

原始色卡图像：

从零学AI之图像算法3：使用 opencv 进行图片颜色转换2
色卡图像红色提取结果：

从零学AI之图像算法3：使用 opencv 进行图片颜色转换2
可以看到不是很好，原因在于给定的 颜色范围设置过于机械和呆板，我们希望灵活一些，根据我的需要自己觉得，这样的话最好使用调色板来尝试。



2.“调色板”应用



##### 示例代码：
def color_bar():
    def callback(x):
        pass
    
    # 创建一副黑色图像
    img = np.zeros((300,512,3),np.uint8)
    cv2.namedWindow('image')

    switch = 'ON\nOFF'
    cv2.createTrackbar(switch, 'image', 0, 1, callback)

    cv2.createTrackbar('R','image', 0, 255, callback)
    cv2.createTrackbar('G','image', 0, 255, callback)
    cv2.createTrackbar('B','image', 0, 255, callback)

    while True:
        cv2.imshow('image',img)
        k = cv2.waitKey(1)&0xFF
        if k == 27:
            break

        r = cv2.getTrackbarPos('R','image')
        g = cv2.getTrackbarPos('G','image')
        b = cv2.getTrackbarPos('B','image')
        s = cv2.getTrackbarPos(switch,'image')

        if s == 0:
            img[:] = 0
            img[:] = [125, 0, 125]
        else:
            img[:] = [b, g, r]
        img[:] = [b, g, r]

    cv2.destroyAllWindows()

    



&nbsp;

 ***
 ***
 > 1. 感谢各位小伙伴对 [<font color=#FF6600> **paperClub** </font>](http://www.infersite.com/) 的关注， 您的点赞、鼓励和留言，都是我深夜坚持的一份动力，无论褒贬，都是我们行进途中最好回馈，也都会被认真对待。
 
 > 2. 我们将持续分享各类、好玩且有趣的算法应用及工程和项目，欢迎分享和转发。沟通、学习和交流，请与我联系，虽然平时忙，但留言必回，勿急，感谢理解！
 
 > 3. 分享内容包括开源项目和自研项目，如在引用或使用时，考虑不周、遗漏引用信息或涉及版权等，请您及时联系。如果您对某些内容感兴趣，我们可以一起讨论、交流和学习。

![avatar](./static/any1one_paperClub.png)
***