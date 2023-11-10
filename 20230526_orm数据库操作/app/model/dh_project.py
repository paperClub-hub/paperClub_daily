from tortoise import Model
from tortoise.fields import IntField, CharField, DatetimeField, TextField


class Project(Model):
    """ 案例模型
    """

    class Meta:
        table = "project"

    id = IntField(True)
    country = CharField(20, description='国家')
    city = CharField(64, description='城市')
    title = CharField(255, description='标题')
    cover_id = IntField(default=0, description='封面编号media.id')
    cover_ids = CharField(255, description='预览封面 []media.id，如 |1|2|')
    user_id = IntField(default=0, description='发布者编号')
    cate_ids = CharField(10, description='分类编号集合;eg:|1|2|3|')
    cate_id = IntField(default=0, description='最下级分类编号,category.id')
    tags = CharField(255, description='标签组;eg:|xxxx|xxxx|')
    ext = CharField(612, description='扩展信息')
    enabled = IntField(default=1, description='启用禁用：1=启用;0禁用;-1待审核')
    create_time = DatetimeField(auto_now_add=True, description='创建时间')
    update_time = DatetimeField(auto_now_add=True, description='更新时间')
    publish_time = DatetimeField(default=None, description='原案例发布时间')
    view_num = IntField(default=0, description='浏览数')
    fav_num = IntField(default=0, description='收藏数')
    pic_num = IntField(default=0, description='图片数')
    source = CharField(20, description='来源')
    source_id = CharField(255, description='来源编号')
    lng = CharField(20, description='经度')
    lat = CharField(20, description='维度')


class Media(Model):
    class Meta:
        table = 'media'

    id = IntField(True)
    table_id = CharField(11, description='所属表:编号，如 project:123')
    kind = CharField(64, description='')
    file = TextField(description='')
    text = TextField(description='')
    create_time = DatetimeField(description='创建时间')


class ProjectMedias(Model):
    class Meta:
        table = 'project_medias'

    id = IntField(True)
    media_ids = TextField(description='')


class Pin(Model):
    class Meta:
        table = 'pin'

    id = IntField(True)
    info = TextField(description='')
    file = TextField(default=None, description='')
