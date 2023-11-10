from tortoise import Model
from tortoise.fields import *

class ItemInteract(Model):
    """ 图片交互数据
    """

    class Meta:
        table = "item_interact"

    id = IntField(True)
    num_impressions = IntField(default=0, description='')
    num_clicks = IntField(default=0, description='')
    num_likes = IntField(default=0, description='')
    num_collects = IntField(default=0, description='')
    num_shares = IntField(default=0, description='')
    num_downloads = IntField(default=0, description='')
    update_time = DatetimeField(description='')
   


class ItemProfile(Model):
    """ 图片信息
    """
    
    class Meta:
        table = "item_profile"

    id = IntField(pk=True)
    region = IntField(description='曝光数')
    cate1 = CharField(12, description='')
    cate2 = CharField(12, description='')
    cate3 = CharField(12, description='')
    keywords = CharField(255, description='')
    text = CharField(1024, description='')
    num_words = IntField(description='')
    info_score = IntField(description='')
    aes_score = IntField(description='')
    publish_time = DatetimeField(description='')
