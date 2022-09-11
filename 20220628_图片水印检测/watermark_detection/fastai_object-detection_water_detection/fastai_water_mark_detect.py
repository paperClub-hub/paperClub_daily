
import cv2,PIL,torch,os,glob
from object_detection_fastai.helper.object_detection_helper import *

size = 256
MODEL = None
anchors = create_anchors(sizes=[(32,32),(16,16),(8,8),(4,4)],
                         ratios=[0.5, 1, 2], scales=[0.35, 0.5, 0.6, 1, 1.25, 1.6])

def PIL2Tensor(pil_img):
    a = np.asarray(pil_img)
    if a.ndim==2 :
        a = np.expand_dims(a,2)
    a = np.transpose(a, (1, 0, 2))
    a = np.transpose(a, (2, 1, 0))
    x = torch.from_numpy(a.astype(np.float32, copy=False))
    x.div_(255)
    return Image(x)

if MODEL is None:
    MODEL = load_learner('coco/models', 'logo_detect.pkl')


def image_pad(img, new_shape=(256, 256), color=(114, 114, 114)):
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):  #### 防止输入1个值
        new_shape = (new_shape, new_shape)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])# Scale ratio (new / old)
    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    dw /= 2  # divide padding into 2 sides
    dh /= 2
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    del r,ratio,new_unpad,dw,dh,top, bottom,left, right
    
    return img

def Bbox2XYXYs(bboxs_tot):
    bboxes = [ele for ele in bboxs_tot[0]] if bboxs_tot else bboxs_tot ####(y1,x1,box-h, box-w)
    bboxes = [[ele[1], ele[0], ele[1]+ele[3], ele[0]+ele[2]] for ele in bboxes]
    bboxes = [list(map(int,box))  for box in bboxes]
    return bboxes


def Scale2Coords(X):
    img1_shape, coords, img0_shape = X
    gain = max(img1_shape) / max(img0_shape)  # gain  = old / new
    pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain

    def clip_coords(boxes, img_shape):# 坐标映射
        boxes[:, 0].clamp_(0, img_shape[1])  # x1
        boxes[:, 1].clamp_(0, img_shape[0])  # y1
        boxes[:, 2].clamp_(0, img_shape[1])  # x2
        boxes[:, 3].clamp_(0, img_shape[0])  # y2

    clip_coords(coords, img0_shape)
    return coords

def do_inference(img, detect_thresh=0.4, nms_thresh=0.1):
    clas, bboxs, xtr = MODEL.pred_batch(batch=MODEL.data.one_item(img))  ###
    scores_tot,bboxs_tot,labels_tot = [],[],[]
    for clas_pred, bbox_pred in list(zip(clas, bboxs)):
        t_sz = torch.Tensor([size])[None].cpu()
        bbox_pred, scores, preds = process_output(clas_pred, bbox_pred, anchors, detect_thresh)
        if bbox_pred is not None:
            to_keep = nms(bbox_pred, scores, nms_thresh)
            bbox_pred, preds, scores = bbox_pred[to_keep].cpu(), preds[to_keep].cpu(), scores[to_keep].cpu()
            # print("bbox_pred:",bbox_pred) #中心点y,中心点x, box-h, box-w
            bbox_pred = to_np(rescale_boxes(bbox_pred, t_sz))
            bbox_pred[:, :2] = bbox_pred[:, :2] - bbox_pred[:, 2:] / 2  ###转化为： (y1,x1,box-h, box-w)
            bboxs_tot.append(bbox_pred)
            scores_tot.append(scores)
            labels_tot.append(preds)
    
    return bboxs_tot, scores_tot, labels_tot




def plot_bbox(img, scores_tot, bboxs_tot,labels_tot, is_xyxy=False):
    TEXT_COLOR = (0, 0, 255)
    if bboxs_tot:
        for i, bbox_pred in enumerate(bboxs_tot[0]):
            pre_score = scores_tot[0].numpy().tolist()[i]
            label_index = labels_tot[0].numpy().tolist()[i]
            pre_str = str("{}-{:.2f}".format(label_index, pre_score))
            if is_xyxy:
                x1, y1, x2, y2 = map(int, bbox_pred)
            else:
                bbox = bbox_pred
                y1, x1, h, w = map(int, bbox)
                y2, x2 = y1 + h, x1 + w
            ((text_width, text_height), _) = cv2.getTextSize(pre_str, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.putText(img, pre_str, (x1, int(y1 - 0.3 * text_height)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, TEXT_COLOR, lineType=cv2.LINE_AA)
            cv2.rectangle(img, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=2)
    # plt.imshow(img)
    # plt.show()
    return img


def predict_api(imgPath,save_dir='./test_output',is_show = False):
    src = cv2.imread(imgPath)
    img = image_pad(src)
    img_pad_pil = PIL.Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    img_pad_in = PIL2Tensor(img_pad_pil)
    bboxs_tot, scores_tot, labels_tot = do_inference(img_pad_in)
    xyxys = Bbox2XYXYs(bboxs_tot)
    scale_xys = list(map(Scale2Coords, [[img.shape[:2], torch.Tensor([x]), src.shape[:2]] for x in xyxys]))
    img_resized = plot_bbox(img, scores_tot, bboxs_tot,labels_tot, is_xyxy=False)
    img_src = plot_bbox(src, scores_tot, scale_xys,labels_tot, is_xyxy=True)
    savePath = os.path.join(save_dir, os.path.splitext(os.path.basename(imgPath))[0] + "_pred.png")
    
    if is_show:
        # plt.subplot(121)
        # plt.imshow(img_resized),plt.title('img_resized')
        # plt.subplot(122),plt.title('img_src')
        plt.imshow(img_src),plt.title('img_src')
        # plt.show()
        plt.savefig(savePath)
        plt.close()
    
    del src,img,img_pad_pil,img_pad_in,xyxys,img_resized,img_src
    return bboxs_tot,scale_xys, scores_tot, labels_tot
    

test_imgs = glob.glob("F:/NSFW/watermark_detection/new_data/images/*.jpg")

from tqdm import tqdm
for testPath in tqdm(test_imgs):
    print(testPath)
    predict_api(testPath,is_show=True)