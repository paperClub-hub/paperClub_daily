import time
from collections import defaultdict
import numpy as np
import torch
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn_extra.cluster import KMedoids



def Zgrad(Z):
    """ 分组 """
    def Zcluser(X, threshold = None):
        idxs, groups = [],[]
        array = np.array(X.copy())
        DATA=pd.Series(np.array(X))
        if threshold is None:
            threshold = np.std(array)

        while len(DATA):
            group_idx, group_dt = [], []
            if len(DATA) == 1:
                group_idx.extend(list(DATA.index))
                group_dt.extend(list(DATA))
                DATA=DATA.drop(DATA.index)
            else:
                idx = DATA.index[0]
                dt = DATA[idx]
                DATA = DATA.drop(idx)
                dist = abs(DATA - dt)

                if (dist <= threshold).any():
                    data = DATA[dist <= threshold]
                    DATA = DATA.drop(data.index)
                    group_idx.extend([idx] + list(data.index))
                    group_dt.extend([dt]+list(data))
                else:
                    group_idx.extend([idx])
                    group_dt.extend([dt])

            idxs.append(group_idx)
            groups.append(group_dt)

        return idxs, groups

    distance = 0.0
    _, groups = Zcluser(Z[:,2], threshold=None)
    if len(groups) > 1:
        distance = groups[0][-1] + 1e-12
    elif len(groups) == 1: # 2条行为
        thres = 0.5
        distance = groups[0][-1]
        distance = distance - 1e-12 if distance > thres else distance ### 组间聚类大于 thres 强制分组
    flattened_clusters = fcluster(Z, t=distance, criterion='distance')

    return flattened_clusters, groups


def exponential_decay(t, init=0.8, m=30, finish=0.2):
    alpha = np.log(init / finish) / m
    l = - np.log(init) / alpha
    decay = np.exp(-alpha * (t + l))
    return decay



def get_user_vecs(embs, action_times, n_clusters_keep=3):
    """ 对用户历史点击行为特征进行层次聚类:
    使用层次聚类对用户历史行为进行聚类分组：期望获取每类行为的代表（特征），用筛选出的代表来反映用户的兴趣偏好。
    """

    interests = []
    interests_idx = []
    clusters = defaultdict(list)
    clusters_score = defaultdict(float)
    embs_idxs_dict = defaultdict(list)

    ##### 1. 兴趣分类：层次聚类，根据将用户历史行为分成不同类别
    item_embs = embs.tolist()
    z = linkage(item_embs, method='ward')
    # #### 最大类
    # max_cluster = 9999
    # flattened_clusters = fcluster(z, t=max_cluster, criterion='maxclust')
    # ### 标准差
    flattened_clusters, groups = Zgrad(z)


    ##### 2. 时间衰减：按时间衰减，计算重要分，保留前 n_clusters_keep 个集群
    now = int(time.time())
    for i, c in enumerate(flattened_clusters):
        importance_score = exponential_decay(now - action_times[i])
        clusters_score[c] += importance_score
    keep_clusters = [v[0] for v in sorted(clusters_score.items(), key=lambda i: i[1], reverse=True)[:n_clusters_keep]]
    for i, c in enumerate(flattened_clusters):
        if c in keep_clusters:
            clusters[c].append(item_embs[i])
            embs_idxs_dict[c].append(i)

    ##### 3. 兴趣代表： 使用Medoids从每类历史行为中选出一个作为此类兴趣代表
    for cluster, embs in clusters.items():
        km = KMedoids(n_clusters=1, random_state=0).fit(embs)
        interest = km.cluster_centers_[0]
        interests.append(torch.tensor(interest, dtype=torch.float))
        interest_idx = embs_idxs_dict.get(cluster)[embs.index(interest.tolist())]
        interests_idx.append(interest_idx)

    ##### 4. 返回兴趣代表 和 代表在历史行为中的位置
    return torch.stack(interests, 0), np.array(interests_idx)


if __name__ == '__main__':
    pass

    user_seq_embs = np.asarray([[0.0664, -0.0692, 0.0749, 0.0635, 0.0505, 0.1591, 0.1755, -0.0269,
                                 0.3300, 0.1547, -0.1071, 0.0468, 0.0637, -0.1306, 0.1132, 0.0806,
                                 -0.1991, 0.3163, 0.0341, 0.2663, -0.1393, -0.1295, 0.1421, -0.0719,
                                 -0.0284, 0.0231, -0.0711, -0.0952, -0.1042, -0.1454, 0.1571, -0.1172,
                                 0.1187, 0.0121, -0.0702, 0.3384, 0.3205, 0.0256, -0.2075, 0.1906,
                                 -0.1563, 0.1984, 0.1980, -0.0757, 0.0704, 0.0112, 0.0902, 0.1038,
                                 -0.0664, -0.1104, 0.1270, -0.0523, 0.0535, -0.0032, 0.1112, 0.0569,
                                 0.0326, 0.3931, -0.1434, -0.0111, -0.0538, -0.0940, 0.0617, -0.0044,
                                 0.0999, 0.0597, 0.0111, 0.2409, -0.0047, 0.2618, 0.2423, -0.1548,
                                 -0.0686, -0.0880, -0.0969, 0.0854, -0.0710, 0.1003, -0.0813, -0.0331,
                                 -0.0386, 0.2180, 0.1521, 0.0334, -0.1663, 0.0272, 0.2370, 0.1274,
                                 0.2698, -0.1032, 0.3687, -0.1572, -0.0424, 0.2060, 0.0942, -0.0279,
                                 0.3128, -0.0763, 0.1170, -0.0066, -0.0937, 0.1633, -0.0887, -0.1871,
                                 0.0121, 0.0723, -0.0011, -0.0820, 0.1423, 0.2756, 0.0440, -0.0471,
                                 0.2924, 0.0304, -0.0121, -0.1167, 0.1034, 0.1985, 0.1667, 0.0248,
                                 -0.0339, 0.0857, 0.0615, -0.0483, 0.0348, 0.2667, -0.1197, 0.0179],
                                [0.0249, 0.0383, 0.1808, 0.0802, 0.0589, 0.2254, 0.1070, -0.1773,
                                 0.3322, 0.0614, -0.1335, 0.0810, -0.0720, -0.0893, 0.0052, -0.0149,
                                 -0.0960, 0.3365, 0.0103, 0.3382, -0.1470, -0.0952, 0.2146, -0.1298,
                                 0.0728, 0.0343, -0.0663, -0.0302, -0.1759, -0.0656, 0.0733, -0.0876,
                                 0.1336, 0.0018, -0.0014, 0.2569, 0.3200, 0.1026, -0.1483, 0.1556,
                                 0.0239, 0.2039, 0.1730, -0.0930, 0.0404, 0.0296, 0.1083, 0.1459,
                                 -0.1286, -0.0538, 0.0726, -0.1097, -0.0511, -0.0228, 0.1032, 0.0615,
                                 0.0915, 0.4583, -0.1166, -0.0846, -0.0431, -0.0407, 0.1886, -0.1332,
                                 0.0541, 0.0730, 0.0012, 0.3483, 0.0302, 0.2819, 0.2063, -0.1508,
                                 -0.1209, -0.0320, 0.0361, 0.0754, -0.0138, 0.1345, -0.0958, 0.0068,
                                 -0.0372, 0.1952, 0.2499, -0.0084, -0.2105, 0.0968, 0.2603, 0.0547,
                                 0.3967, -0.1071, 0.3022, -0.2265, -0.1374, 0.1524, 0.0587, 0.0141,
                                 0.3656, 0.0180, 0.0826, 0.0013, -0.0457, 0.1572, 0.0146, -0.2199,
                                 -0.0204, 0.0771, -0.0184, 0.0781, 0.2294, 0.2966, 0.0886, 0.0070,
                                 0.2882, 0.1704, -0.0817, 0.0531, 0.1226, 0.0517, 0.2764, -0.0543,
                                 -0.0224, 0.0922, 0.0518, -0.1207, -0.0205, 0.2848, -0.1083, 0.0399],
                                [-0.0055, -0.0481, 0.1241, 0.0618, 0.0548, 0.2311, 0.0952, -0.1240,
                                 0.3195, 0.0793, -0.1361, 0.0983, -0.1202, -0.0640, 0.0057, -0.0134,
                                 -0.1005, 0.2721, -0.0557, 0.2887, -0.0796, -0.0465, 0.1324, -0.0963,
                                 0.1217, 0.0096, -0.1137, -0.0231, -0.0859, -0.0988, 0.0451, -0.0846,
                                 0.0479, -0.0042, -0.0208, 0.2578, 0.3114, 0.1342, -0.0994, 0.1531,
                                 -0.0249, 0.1661, 0.1675, -0.0990, 0.0521, 0.0395, -0.0314, 0.1550,
                                 -0.1379, -0.1401, 0.1190, -0.0421, -0.0766, -0.0341, 0.1567, -0.0276,
                                 -0.0105, 0.5251, -0.0948, -0.1036, -0.0665, -0.0848, 0.2100, -0.1042,
                                 0.0994, 0.1070, 0.0203, 0.2562, 0.0409, 0.2415, 0.2790, -0.0293,
                                 -0.0992, -0.0221, 0.0404, 0.1322, 0.0163, 0.2003, -0.1259, -0.0229,
                                 -0.0854, 0.1362, 0.3510, 0.0515, -0.1988, 0.0821, 0.2610, 0.1250,
                                 0.3730, -0.1128, 0.2765, -0.2229, -0.0767, 0.1831, 0.0652, -0.0489,
                                 0.3599, -0.0648, 0.0291, 0.0039, -0.1143, 0.1386, -0.0811, -0.1784,
                                 -0.0007, 0.0908, 0.0332, -0.0472, 0.1824, 0.2983, 0.0637, 0.0109,
                                 0.1951, 0.0969, -0.1462, 0.0746, 0.1634, 0.0432, 0.3008, 0.0226,
                                 -0.0262, 0.0124, -0.0145, -0.1262, 0.0029, 0.3029, -0.0584, 0.0441]])


    user_interests, idxs = get_user_vecs(user_seq_embs, action_times=[int(time.time())] * len(user_seq_embs))
    # print(user_interests)
    print(len(user_interests))
    print(idxs)
