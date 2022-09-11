import cv2
import os
import time
from pathlib import Path
import numpy as np
import pandas as pd

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from collections import defaultdict
from libKMCUDA import kmeans_cuda

CSV = None
CUR_PATH = Path(os.path.dirname(__file__))


def init_colors():
    """Reading csv file with pandas and giving names to each column"""
    print("loading COLOR data...")
    index = ["en_name", "l", "a", "b", "cn_serie", "cn_name"]
    return pd.read_csv(CUR_PATH/'colors.csv', names=index, header=None)


if CSV is None:
    CSV = init_colors()


def to_lab(rgb):
    """颜色转换"""
    color_rgb = sRGBColor(rgb[0], rgb[1], rgb[2])
    color_lab = convert_color(color_rgb, LabColor)
    lab = color_lab.lab_l, color_lab.lab_a, color_lab.lab_b
    # print(rgb, {"L": lab[0], "A": lab[1], "B": lab[2]})
    return lab


def color_dist_lab(lab1, lab2):
    """两个lab颜色的欧几里得距离"""
    """ returns the squared euklidian distance between two color vectors in lab space """
    return sum((a-b)**2 for a, b in zip(lab1, lab2))


def yield_dominate_colors(cv_mat, k=8):
    """获取图片主色"""
    # 转成像素图
    r, c = cv_mat.shape[:2]
    out_r = 80
    image = cv2.resize(cv_mat, (int(out_r*float(c)/r), out_r))
    pixels = image.reshape((-1, 3))

    # 聚类
    # start = time.time()
    # km = KMeans(n_clusters=k)
    # km.fit(pixels)

    # # 根据颜色和占比，计算主色
    # colors = np.asarray(km.cluster_centers_, dtype='uint8')
    # percentage = np.asarray(np.unique(km.labels_, return_counts=True)[1], dtype='float32')
    # percentage = percentage/pixels.shape[0]
    # dom = [[percentage[ix], colors[ix]] for ix in range(km.n_clusters)]
    # dominance = sorted(dom, key=lambda x: x[0], reverse=True)


    # 改用 kmcuda 提高性能
    pixels = np.asarray(pixels, dtype="float32")
    dominance, assignments = kmeans_cuda(pixels, 8, verbosity=0, seed=4)
    dominance = np.asarray(dominance, dtype="uint8")
    # print('聚类', time.time() - start)

    unique, counts = np.unique(assignments, return_counts=True)
    rate = list(map(lambda x: x/sum(counts), counts))

    dominance = sorted(list(zip(unique, rate, dominance.tolist())), key=lambda x: x[1], reverse=True)
    dominance = [c[1:] for c in dominance]

    # 计算主色相似的中文名称
    for rate, rgb in dominance:
        lab1 = to_lab(rgb)
        _, idx = min([(color_dist_lab(lab1, (CSV.loc[i, "l"], CSV.loc[i, "a"], CSV.loc[i, "b"])), i)
                      for i in range(len(CSV))])
        yield (rate, CSV.loc[idx, "cn_serie"], CSV.loc[idx, "cn_name"])


def predict_color(cv_mat, k=8, min_rate=0.2, with_score=False, debug=False):
    result = defaultdict(float)
    for rate, serie, name in yield_dominate_colors(cv_mat, 8):
        if debug:
            print(rate, serie, name)
        result[serie] += rate

    result = [(s, r) for s, r in result.items() if r >= min_rate]
    result = sorted(result, key=lambda x: x[1], reverse=True)[:k]
    result = result if with_score else " ".join([s[0] for s in result])
    return result


if __name__ == "__main__":
    filename = "./Color/fen.jpg"

    image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    import time

    start = time.time()
    result = predict_color(image, min_rate=0.15, debug=False)
    print(time.time() - start)
    print(result)
