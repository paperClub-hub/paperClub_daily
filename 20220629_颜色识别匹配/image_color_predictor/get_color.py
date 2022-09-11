from sklearn.cluster import KMeans
import cv2
import json
import numpy as np


def get_dominance_colors():
    image = cv2.imread("./Color/fen2.jpg")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    r, c = image.shape[:2]
    out_r = 120
    image = cv2.resize(image, (int(out_r*float(c)/r), out_r))
    pixels = image.reshape((-1, 3))

    km = KMeans(n_clusters=8)
    km.fit(pixels)

    colors = np.asarray(km.cluster_centers_, dtype='uint8')

    percentage = np.asarray(np.unique(km.labels_, return_counts=True)[1], dtype="float32")
    percentage = percentage/pixels.shape[0]
    percentage

    dom = [[float(percentage[ix]), colors[ix].tolist()] for ix in range(km.n_clusters)]
    dominance = sorted(dom, key=lambda x: x[0], reverse=True)

    # print(dominance)
    print(json.dumps(dominance, indent=2))
    return dominance


if __name__ == "__main__":
    get_dominance_colors()
