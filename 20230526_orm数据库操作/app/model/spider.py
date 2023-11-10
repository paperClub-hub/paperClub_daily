from tortoise.models import Model
from tortoise.fields import IntField, CharField, SmallIntField, DatetimeField, JSONField, FloatField, TextField



class zhimo_project_detail(Model):
    """ zhimo_project_detail
    """

    class Meta:
        table = "zhimo_project_detail"
    
    id = IntField(True)
    info = JSONField(default="{}", description="")
    update_time = DatetimeField()
    
    
class zhimo_project(Model):
    """ zhimo_project： 所有字段必须和数据库对应一致
    """
    class Meta:
        table = "zhimo_project"
        
    id = IntField(True)
    title = CharField(255, default="", description="")
    desc = CharField(255, default="", description="")
    view_num = IntField(default=0)
    fav_num = IntField(default=0)
    cover = CharField(255, default="", description="")
    filter_items = CharField(5048, default="", description="")
    has_detail = IntField(default=0)
    valid = IntField(default=0)
    publish_time = DatetimeField(default=None, description='更新时间')
    create_time = DatetimeField(auto_now_add=True, description='更新时间')
    update_time = DatetimeField(auto_now_add=True, description='更新时间')
    dhomev2_projectid = IntField(default=0)

class top_ids(Model):
    """ top_ids """
    class Meta:
        table = "top_ids"

    id = IntField(True)

