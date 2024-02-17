# Redis在windows上使用

### 下载及安装：
- [下载连接](https://github.com/microsoftarchive/redis/releases)

```dotnetcli
1、安装可参考：https://www.cnblogs.com/zhoading/p/17727259.html/

2、双击redis-server.exe 启动服务端，或 cd 到安装文件夹启动，如：
E:\1_software\redis_win10\Redis-x64-3.0.504>redis-server.exe，redis.windows.conf配置文件，包括端口等

redis默认端口6379，默认密码foobared
3、打开另一个cmd窗口，客户端调用：redis-cli.exe -h 127.0.0.1 -p 6379

测试命令：
    ping
    显示版本信息：info

```

### 安装redis的python 模块
```
pip install redis -i https://mirrors.aliyun.com/pypi/simple/

import redis

<!-- r=redis.Redis(host='127.0.0.1',port=6379,db=0,password='foobared') -->
r=redis.Redis()
print(r.keys("*"))
```


### python redis使用

```dotnetcli
使用前需要启动服务端，
cd E:\1_software\redis_win10\Redis-x64-3.0.504
E:\1_software\redis_win10\Redis-x64-3.0.504

```
 [参考]
 - https://blog.csdn.net/lyshark_lyshark/article/details/125846831
 - https://blog.csdn.net/qq_38628046/article/details/128123641

```dotnetcli

#######################
import redis

# 连接到本地Redis服务器，默认端口为6379
r = redis.Redis(host='localhost', port=6379, db=0)

# 设置键值对
r.set('hello', 'world')

# 获取键对应的值
value = r.get('hello')
# 输出 b'world'
print(value)

r.set("hello", 'world2')
# 输出 b'world'，没有覆盖
print("value2: ", value)
# 批量设置键值对
r.mset({'foo': '1', 'bar': '2'})

# 批量获取键对应的值
values = r.mget(['foo', 'bar'])
# 输出 [b'1', b'2']
print(values)

#######################
# 也可以使用StrictRedis对象连接redis服务器，StrictRedis类基于Redis类实现。

r = redis.StrictRedis(host='localhost', port=6379, db=0)
# 设置键值对
r.set('hello', 'world')

# 获取键对应的值
value = r.get('hello')
print(value)  # 输出 b'world'


#######################

r = redis.StrictRedis(host='localhost', port=6379, db=0)
# 设置哈希表键值对
r.hset('user1', 'name', 'Alice')
r.hset('user1', 'age', 20)
r.hset('user1', 'gender', 'female')
# 获取整个哈希表
hash_table = r.hgetall('user1')
print(hash_table) # 输出 {b'name': b'Alice', b'age': b'20', b'gender': b'female'}

```
测试
```dotnetcli
#!/usr/bin/env python


import redis

# 也可以使用StrictRedis对象连接redis服务器，StrictRedis类基于Redis类实现。

r = redis.StrictRedis(host='localhost', port=6379, db=0)

## 清空当前数据库中的数据
r.flushdb() # 或 r.flushall()

# 设置哈希表键值对
r.hset('user1', 'name', 'Alice')
r.hset('user1', 'age', 20)
r.hset('user1', 'gender', 'female')
# 获取整个哈希表
hash_table = r.hgetall('user1')
print(hash_table) # 输出 {b'name': b'Alice', b'age': b'20', b'gender': b'female'}

##  String类型
#   增加数据：set key value（如果key存在，则修改为新的value）
print(r.set('str_type', 'str_value'))  # 打印True
# 追加数据：append key value
print(r.append('str_type', 'vvv'))  # 打印13，字符长度
# 查看数据：get
print(r.get('str_type'))

## List类型
#   在插入数据时，如果该键并不存在，Redis将为该键创建一个
#   在末尾添加数据（列表右边）
r.rpush('list_type', '2', 'xy', 'li_val_end')
#   在头部添加数据（列表左边）
r.lpush('list_type', '1', 'xy', 'li_val_start')
#   查看数据
#   数据为：['li_val_start', 'xy', '1', '2', 'xy', 'li_val_end']
#   下标范围：lrange key start stop
print(r.lrange('list_type', 0, 10))
#   指定下标：lindex key index
print(r.lindex('list_type', -1)) # b'li_val_end'

#   删除数据
#   从末尾删除（列表右边）：rpop key
print(r.rpop('list_type'))  # 打印删除的值: b'li_val_end'
#   从头部删除（列表左边）：lpop key
#   指定值删除：lrem key count(可以存在多个重复的值，指定value删除的次数) value
print(r.lrem('list_type', 2, 'xy'))  # 打印成功删除的个数: 2

## Hash类型
#   hash类型的值是一个键值对集合，如：h_test : { field1:value1, field2:value2,...}
#   添加数据：hset key field value
print(r.hset('hash_type', 'filed', 'value'))  # 打印成功添加数据的条数: 1
#   查看域值：hget key field
print(r.hget('hash_type', 'filed')) # b'value'
#   查看所有的field：hkeys key
print(r.hkeys('hash_type')) # [b'filed']
#   查看所有的value：hvals key
print(r.hvals('hash_type')) # [b'value']
#   查看所有的键值对：hgetall key
print(r.hgetall('hash_type')) # {b'filed': b'value'}

print("#" * 10)
## Set类型
#   Set类型为无序的字符集合，元素具有唯一性， 不重复(自动去重)
#   添加数据：sadd key member1 [member2 ...]
print(r.sadd('set_type', 'va', 'vb', 'vc', 'vd'))  # 打印成功添加数据的条数
#   查看数据：smembers key
print(r.smembers('set_type')) # {b'vd', b'vb', b'vc', b'va'}
#   随机删除：spop key
print(r.spop('set_type'))  # 打印删除的值
#   指定删除：srem key member1 [member2 ...]
print(r.srem('set_type', 'va', 'vb'))  # 打印成功删除的个数


## Zset类型
#   每一个成员都会有一个分数(score)与之关联
#   成员是唯一的，但是分数(score)却是可以重复的
#   比如把一个班级的学生分成几组

#   添加数据： zadd key score member [score2 member2 …]
#   打印成功添加数据的条数
# print(r.zadd('zset_type',
#                      1, 'val1', 1, 'val2', 1, 'val3',
#                      4, 'val4', 4, 'val5',
#                      8, 'val6'
#                      ))
# #   查看数据
# #   根据索引：zrange key start stop
# print(r.zrange('zset_type', 0, 3))
# #   根据score：zrangebyscore key min max
# #   查看 score 1 到 2 的值
# print(r.zrangebyscore('zset_type', 1, 2))

## 全局key操作

print(r.keys()) # [b'str_type', b'hash_type', b'list_type', b'user1', b'set_type']
#   查看key的类型：type key
print(r.type('set_type')) # b'set'
#   exists key 查看key是否存在
print(r.exists('abcd'))  # 不存在返回False
#   改名：rename key new_key
#   如果不存在则报错：no such key
# print(con_redis.rename('str_type', 'str_type_new'))
#   删除键值对：del key [key2 key3 ...]
print(r.delete('hash_type'))  # 打印成功删除的个数

#   设置过期时间：expire key seconds
print(r.expire('list_type', 60))  # 返回bool
#   persist key 删除过期时间
print(r.persist('list_type'))# 返回bool
#   ttl key 查看时间
#   -1：没设置过期时间      -2：不存在这个键
print(r.ttl('list_type'))
```