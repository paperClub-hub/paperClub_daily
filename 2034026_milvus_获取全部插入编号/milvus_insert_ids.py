

def get_insert_milvus_ids(MILVUS, collection_name):
    ##### 获取全部插入编号
    def _get_segmentIds(collection_name):
        "获取分区编号list"
        segment_ids = []
        _, segment_info = MILVUS.get_collection_stats(collection_name)
        if segment_info.get('partitions')[0].get('segments'):
            segment_ids = [x.get("name") for x in segment_info.get('partitions')[0].get('segments')]

        return segment_ids


    def _segment2insertId(segmet_id):
        "根据分区编号，获得id列表"

        _, insert_ids = MILVUS.list_id_in_segment(collection_name =collection_name, segment_name=segmet_id)
        return insert_ids

    ##### 文件分区编号列表
    milvus_insert_ids = []
    segment_ids = _get_segmentIds(collection_name)
    if segment_ids:
        milvus_insert_ids = list(map(_segment2insertId, segment_ids))
        milvus_insert_ids = [id for ids in milvus_insert_ids for id in ids]

    return milvus_insert_ids


get_insert_milvus_ids(milvus, collection_name)