import jieba
from os import path
from ordered_set import OrderedSet
from collections import OrderedDict
from typing import Tuple, List, Any, Union, Callable

STYLE_LABEL = """
现代	|现代风|现代风格|
美式	|美式风|美式风格|
轻奢	|轻奢风|轻奢风格|
新中式	|新中式风|新中式风格|中式|中式风格|中式风|现代中式|Chinoiserie|
极简	|极简风|极简主义|极简风格|
日式	|日式风|日式风格|
北欧	|北欧风格|北欧风|
古典
侘寂	|诧寂|侘寂风|诧寂风|
复古	|复古风|复古风格|
欧式	|法式|意式|英式|欧式风|欧式风格|法式风格|意式风格|
简欧	|欧式|简欧风|简欧风格|
工业	|工业风|工业风格|
乡村	|田园|乡村风|乡村风格|田园风|田园风格|
新古典	|古典|新古典风格|新古典风|
东南亚	|东南亚风格|东南亚风|
混搭	|折衷|折衷主义|折中|折中主义|混搭风|混搭风格|
地中海	|地中海风格|地中海风|
后现代	|后现代风格|后现代风|
孟菲斯	|孟菲斯风格|孟菲斯风|
中古	|中古风|中古风格|
Art Deco	|装饰主义|艺术装饰|
波西米亚	|boho风|波西米亚风格|
波普	|波普风|波普风格|pop风|
包豪斯	|包豪斯风格|包豪斯风|
Japandi	|japandi风格|Japandi风|
超现实	|超现实主义|超现实风格|
复古未来主义	|复古未来|
未来	|科技|科幻|未来风|科幻风|科技风|未来风格|科幻风格|
简约	|简约风|简约风格|
北非	|清真|伊斯兰|伊斯兰风格|穆斯林|穆斯林风格|
好莱坞	|好莱坞摄政风格|好莱坞摄政风|摄政风|
赤贫	|赤贫风格|
原木	|原木风|原木风格|
奢华	|奢华风|奢华风格|奢侈|
极繁	|极繁主义|极多|极多主义|
度假	|度假风|
法式
意式"""

SPACE_LABEL = """
卫生间	|厕所|洗手间|卫浴间|卫浴|
客厅	|起居室|
卧室	|主卧|客卧|卧房|
餐厅	|饭厅|
厨房	|西厨|
玄关	|入户|入口|门厅|
阳台
儿童房	|男孩房|女孩房|女儿房|儿童|
书房
庭院	|院子|花园|户外|
茶室	|休闲区|
衣帽间	|步入式|
露台	|天台|户外|
影音室	|影音|休闲区|
阁楼	|顶楼|
地下室	|地下|
浴室	|卫浴间|卫浴|
外立面	|户外|室外|建筑|建筑外观|外观|别墅外观|
健身房	|健身区|休闲区|
走廊	|过道|
酒窖	|酒库|
车库
阳光房	|玻璃房|
楼梯间
娱乐	|休闲区|娱乐区|"""


LOCALSPACE_LABEL = """
背景墙	|主题墙|墙面|墙|背景|
电视背景墙	|背景墙|电视主题墙|主题墙|墙面|墙|电视墙|电视背景|
楼梯	|楼梯间|楼梯扶手|
洗衣房	|洗衣机柜|洗衣区|
床头
泳池	|游泳池|
吊顶	|天花板|天花|
吧台
榻榻米	|和室|
飘窗	|窗户|窗子|窗|
西厨	|开放式厨房|
沙发背景
床头背景
踢脚线
休闲角	|休闲区|
淋浴房	|淋浴间|淋浴|
电视墙
沙发区
办公区	|书桌区|工作间|
盥洗台	|洗手台|洗漱台|洗漱区|
天花板"""

PRODUCT_LABEL = """
沙发
休闲椅	|扶手椅|
坐凳
坐墩	|墩|
吧凳	|吧椅|吧台椅|吧台凳|
凳 |凳子|
椅 |椅子|椅|
座椅
餐椅
单椅
床
儿童床
床尾凳
躺椅
桌
桌子
餐桌
玄关桌
边桌	|边几|
茶几	|咖啡桌|
书桌	|写字桌|写字台|
岛台	|中岛|
梳妆台	|梳妆区|
柜   |柜子|
电视柜	|电视机柜|
餐边柜
床头柜	|床头桌|
橱柜	|厨柜|
书柜	|书架|
玄关柜	|门厅柜|
鞋柜
衣柜
浴室柜	|台盆柜|面盆柜|
斗柜	|抽屉柜|
边柜
装饰柜
展示柜	|展示架|
酒柜
搁板	|隔板|
置物架	|搁架|隔架|
壁柜	|壁橱|
灯	|灯具|
吊灯	|顶灯|
落地灯
壁灯
台灯
户外灯
吸顶灯	|顶灯|
射灯
灯带 |灯槽|间接照明|
筒灯
花洒	|莲蓬头|喷头|
龙头	|水龙头|
台盆	|面盆|洗手盆|
浴室镜	|镜子|镜|镜柜|
马桶	|坐便器|
浴缸
水槽	|水盆|
床品
装饰画	|油画|画|插画|挂画|抽象画|艺术画|
装饰品	|雕塑|摆件|艺术品|
屏风
衣帽架	|衣架|
植物	|绿植|盆栽|
镜子	|镜|
餐具
窗帘
厨具
浴帘
卡座
榻	|卧榻|沙发榻|"""

MATERIAL_LABEL = """
木	|木材|木质|木头|
金属
玻璃
布	|布艺|布料|
亚克力	|塑料|
大理石
水磨石
黄铜 铜
金
银
铁 铁艺
陶土	|陶|赤陶|
皮革	|皮|皮草|
藤编	|藤草编织|藤草|
丝绒	|天鹅绒|
镜面
壁纸	|壁布|墙纸|墙布|
瓷砖
砖	|砖头|
自流平	|地坪|地平|
水泥	|微水泥|
石材	|石|
地板	|木地板|
涂料	|墙漆|漆|艺术漆|
板材	|胶合板|密度板|
地毯	|块毯|
护墙板	|墙板|墙面镶板|镶板|"""

COLOR_LABEL = """
白色	|白|
绿色	|绿|
粉色	|粉|
蓝色	|蓝|
红色	|红|
黄色	|黄|
灰色	|灰|
紫色	|紫|
橙色	|橙|
棕色	|棕|
彩色	|多彩|
黑色	|黑|
单色	|纯色|
撞色	|比对色|
糖果色	|彩虹|
大地色系	|大地色|
马卡龙色	|马卡龙|
莫兰迪色	|莫兰迪|
木色
裸色	|奶油色|米色|
荧光	|荧光色|
金色	|金|
银色	|银|"""

FEAT_LABEL = """
隔断
壁龛	|凹龛|
西厨
圆拱	|拱形|拱型|
枯山水
挑空
无主灯	|间接照明|
尖拱	|拱形|拱型|
壁画
花砖
墙面拼色	|涂刷|拼接|
梁柱	|横梁|立柱|
几何	|几何图案|几何图形|
流线	|曲线|有机|
纹理	|肌理|
尖顶	|斜顶|
模块化	|组合|
半户外
景观	|观景|
马赛克
夹层
天井	|采光井|
间接照明	|反射照明|
半开放	|敞开式|
有机
错层	|下沉|下沉式|
垭口	|门框|
石膏线
定制家具	|整屋定制|全屋定制|
开放式	|开放|
天窗	|窗户|窗子|窗|
棋盘格"""


def init_lbl_cls(label: str):
    """初始化 dhome 标签词对应的标签及分类相关基础变量"""
    label = label.replace('|', ' ').replace('\t', ' ').lower()
    labels = list(filter(bool, label.splitlines()))
    labels = [s.strip().split() for s in labels]

    lbl_cls_dict = OrderedDict({lbl[0]: cls for cls, lbl in enumerate(labels)})
    cls_lbl_dict = {cls: lbl for lbl, cls in lbl_cls_dict.items()}

    def cls2lbl(cls: Union[List[int], int]):
        if isinstance(cls, int):
            cls = [cls]
        return [cls_lbl_dict[i] if v else '' for i, v in enumerate(cls) if v and i < len(cls_lbl_dict)]

    def lbl2cls(lbl: str, with_matched=False) -> Union[List[int], Tuple[List[int], List[str]]]:
        result = set()
        vs = jieba.lcut(lbl)
        matched = OrderedSet()
        for v in vs:
            if not v:
                continue
            v = v.lower()
            for lbl in labels:
                if v in lbl:
                    result.add(lbl_cls_dict.get(lbl[0]))
                    matched.add(v)

        cls = [1 if i in result else 0 for i in range(len(lbl_cls_dict))]

        if with_matched:
            return cls, list(matched)

        return cls

    return labels, lbl_cls_dict, cls_lbl_dict, cls2lbl, lbl2cls


def save_label_dict(all_labels, path='./dict/label.dict'):
    label_set = set()
    for labels in all_labels:
        for label in labels:
            label_set.add(label)
    print('\n'.join(label_set), file=open(path, 'w', encoding='utf-8'))
    print('专用标签词典已写入：', path)


STYLES, STYLE_CLASS, CLASS_STYLE, class2style, style2class = init_lbl_cls(STYLE_LABEL)
SPACES, SPACE_CLASS, CLASS_SPACE, class2space, space2class = init_lbl_cls(SPACE_LABEL)
LOCALSPACES, LOCALSPACE_CLASS, CLASS_LOCALSPACE, class2localspace, localspace2class = init_lbl_cls(LOCALSPACE_LABEL)
PRODUCTS, PRODUCT_CLASS, CLASS_PRODUCT, class2product, product2class = init_lbl_cls(PRODUCT_LABEL)
MATERIALS, MATERIAL_CLASS, CLASS_MATERIAL, class2material, material2class = init_lbl_cls(MATERIAL_LABEL)
COLORS, COLOR_CLASS, CLASS_COLOR, class2color, color2class = init_lbl_cls(COLOR_LABEL)
FEATS, FEAT_CLASS, CLASS_FEAT, class2feat, feat2class = init_lbl_cls(FEAT_LABEL)

# 记录专用标签词典
data_dir = path.dirname(__file__)
dict_path = path.join(data_dir, './dict/label.dict')
all_labels = STYLES + SPACES + LOCALSPACES + PRODUCTS + MATERIALS + COLORS + FEATS
save_label_dict(all_labels, dict_path)
jieba.load_userdict(dict_path)

# query = '北欧风格好还是复古好'
# cls, matched = style2class(query, True)
# print('测试查询值', query)
# print('测试分类值', cls)
# print('测试风格值', class2style(cls))
# print('测试匹配值', matched)
# print('=' * 20)
