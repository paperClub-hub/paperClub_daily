from tortoise import Model
from tortoise.fields import IntField, CharField, DatetimeField, TextField


class FavItem(Model):
    """ 收藏项模型
    """

    class Meta:
        table = "fav_item"

    id = IntField(True)
    fav_id = IntField(default=0, description='')
    account_id = IntField(default=0, description='')
    table_id = CharField(104, default="", description='')
    create_time = DatetimeField(auto_now_add=True, description='创建时间')
    update_time = DatetimeField(auto_now_add=True, description='更新时间')
