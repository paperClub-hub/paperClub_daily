# -*- coding=utf-8 -*-
##### 文本地址提取，补全与匹配

#
import os
import re
import copy
import collections



def read_file_by_line(file_path, line_num=None,
                      skip_empty_line=True, strip=True,
                      auto_loads_json=True):

    content_list = list()
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        line = f.readline()
        while True:
            if line == '':  # 整行全空，说明到文件底
                break
            if line_num is not None:
                if count >= line_num:
                    break

            if line.strip() == '':
                if skip_empty_line:
                    count += 1
                    line = f.readline()
                else:
                    try:
                        if auto_loads_json:
                            cur_obj = json.loads(line.strip())
                            content_list.append(cur_obj)
                        else:
                            if strip:
                                content_list.append(line.strip())
                            else:
                                content_list.append(line)
                    except:
                        if strip:
                            content_list.append(line.strip())
                        else:
                            content_list.append(line)

                    count += 1
                    line = f.readline()
                    continue
            else:
                try:
                    if auto_loads_json:
                        cur_obj = json.loads(line.strip())
                        content_list.append(cur_obj)
                    else:
                        if strip:
                            content_list.append(line.strip())
                        else:
                            content_list.append(line)
                except:
                    if strip:
                        content_list.append(line.strip())
                    else:
                        content_list.append(line)

                count += 1
                line = f.readline()
                continue

    return content_list




def china_location_loader(detail=False):
    """ 加载中国地名词典 china_location.txt
    Args:
        detail(bool): 若为 True，则返回 省、市、县区、乡镇街道、村社区 五级信息；
            若为 False，则返回 省、市、县区 三级信息
    """

    GRAND_DIR_PATH = os.getcwd()
    location_jio = read_file_by_line(
        os.path.join(GRAND_DIR_PATH, 'location_data/china_location.txt'),
        strip=False)

    cur_province = None
    cur_city = None
    cur_county = None
    cur_town = None
    cur_village = None
    location_dict = dict()

    for item in location_jio:
        if not item.startswith('\t'):  # 省
            if len(item.strip().split('\t')) != 3:
                continue
            province, admin_code, alias_name = item.strip().split('\t')
            cur_province = province
            location_dict.update(
                {cur_province: {'_full_name': province,
                                '_alias': alias_name,
                                '_admin_code': admin_code}})

        elif item.startswith('\t\t\t\t'):  # 村、社区
            if not detail:
                continue
            cur_village = item.strip()
            location_dict[cur_province][cur_city][cur_county][cur_town].update(
                {cur_village: None})

        elif item.startswith('\t\t\t'):  # 乡镇、街道
            if not detail:
                continue
            cur_town = item.strip()
            location_dict[cur_province][cur_city][cur_county].update(
                {cur_town: dict()})

        elif item.startswith('\t\t'):  # 县、区
            if len(item.strip().split('\t')) != 3:
                continue
            county, admin_code, alias_name = item.strip().split('\t')
            cur_county = county
            location_dict[cur_province][cur_city].update(
                {cur_county: {'_full_name': county,
                              '_alias': alias_name,
                              '_admin_code': admin_code}})

        else:  # 市
            if len(item.strip().split('\t')) != 3:
                continue
            city, admin_code, alias_name = item.strip().split('\t')
            cur_city = city
            location_dict[cur_province].update(
                {cur_city: {'_full_name': city,
                            '_alias': alias_name,
                            '_admin_code': admin_code}})
    # print(location_dict)
    return location_dict





class LocationParser(object):

    def __init__(self):
        self.administrative_map_list = None
        self.town_village = False
        self.town_village_dict = dict()

    def _mapping(self, china_loc):
        # 整理行政区划码映射表
        self.administrative_map_list = list()  # 地址别称

        for prov in china_loc:
            if prov.startswith('_'):
                continue
            self.administrative_map_list.append(
                [china_loc[prov]['_admin_code'],
                 [prov, china_loc[prov]['_alias']],
                 [None, None],
                 [None, None]])
            for city in china_loc[prov]:
                if city.startswith('_'):
                    continue
                self.administrative_map_list.append(
                    [china_loc[prov][city]['_admin_code'],
                     [prov, china_loc[prov]['_alias']],
                     [city, china_loc[prov][city]['_alias']],
                     [None, None]])
                for county in china_loc[prov][city]:
                    if county.startswith('_'):
                        continue
                    self.administrative_map_list.append(
                        [china_loc[prov][city][county]['_admin_code'],
                         [prov, china_loc[prov]['_alias']],
                         [city, china_loc[prov][city]['_alias']],
                         [county, china_loc[prov][city][county]['_alias']]])

                    if self.town_village:  # 补充 self.town_village_list

                        key_name = prov + city + county
                        value_dict = china_loc[prov][city][county]
                        self.town_village_dict.update({key_name: value_dict})

    def _prepare(self):
        # 添加中国区划词典
        china_loc = china_location_loader(detail=self.town_village)
        self._mapping(china_loc)

        self.loc_level_key_list = ['省', '市', '县']
        if self.town_village:
            self.loc_level_key_list.extend(['乡', '村'])
        self.loc_level_key_dict = dict(
            [(loc_level, None) for loc_level in self.loc_level_key_list])
        self.municipalities_cities = ['北京', '上海', '天津', '重庆', '香港', '澳门']

    def get_candidates(self, location_text):
        """ 从地址中获取所有可能涉及到的候选地址 """

        if self.administrative_map_list is None:
            self._prepare()

        candidate_admin_list = list()  # 候选列表
        for admin_item in self.administrative_map_list:
            count = 0
            # offset 中的每一个元素，分别指示在地址中的索引，以及全名或别名
            offset_list = [[-1, -1], [-1, -1], [-1, -1]]
            for idx, name_item in enumerate(admin_item[1:]):
                match_flag = False
                cur_name = None
                cur_alias = None
                for alias_idx, name in enumerate(name_item):  # 别名与全名任意匹配一个
                    if name is not None and name in location_text:
                        match_flag = True
                        cur_name = name
                        cur_alias = alias_idx

                        # print("name: ", name)
                        
                        break
                if match_flag:#### 获取地址在字符串当中的位置
                    # print("location_text: ", location_text)
                    
                    count += 1
                    offset_list[idx][0] = location_text.index(cur_name)
                    offset_list[idx][1] = cur_alias
                    # print("offset_list: ", offset_list)

            if count > 0:
                cur_item = copy.deepcopy(admin_item)
                cur_item.extend([count, offset_list])
                # print("cur_item: ", cur_item)
                candidate_admin_list.append(cur_item)

        return candidate_admin_list

    def __call__(self, location_text, town_village=False):

        self.town_village = town_village
        if self.administrative_map_list is None:
            self._prepare()
        if self.town_village and self.town_village_dict == dict():
            self._prepare()

        # 获取文本中的省、市、县三级行政区划
        # rule: 命中匹配别名或全名，统计命中量，并假设省市县分别位于靠前的位置且依次排开
        candidate_admin_list = self.get_candidates(location_text)

        if len(candidate_admin_list) == 0:
            result = {'province': None,
                      'city': None,
                      'county': None,
                      'detail': location_text,
                      'full_location': location_text,
                      'orig_location': location_text}
            if self.town_village:
                result.update({'town': None, 'village': None})
            return result
        
        # 寻找匹配最多的候选地址，然后寻找匹配最靠前的候选地址，作为最终的省市县的判断结果
        candidate_admin_list = sorted(
            candidate_admin_list, key=lambda i:i[-2], reverse=True)
        max_matched_num = candidate_admin_list[0][-2]
        candidate_admin_list = [item for item in candidate_admin_list
                                if item[-2] == max_matched_num]
        candidate_admin_list = sorted(
            candidate_admin_list, key=lambda i:sum([j[0] for j in i[-1]]))

        min_matched_offset = sum([j[0] for j in candidate_admin_list[0][-1]])
        candidate_admin_list = [item for item in candidate_admin_list
                                if sum([j[0] for j in item[-1]]) == min_matched_offset]

        # rule: 县级存在重复名称，计算候选列表中可能重复的县名
        county_dup_list = [item[3][item[-1][-1][1]] for item in candidate_admin_list]
        county_dup_list = collections.Counter(county_dup_list).most_common()
        county_dup_list = [item[0] for item in county_dup_list if item[1] > 1]

        final_admin = candidate_admin_list[0]  # 是所求结果

        # 确定详细地址部分
        # rule: 根据已有的省市县，确定剩余部分为详细地址
        detail_idx = 0

        final_prov = None
        final_city = None
        final_county = None
        for admin_idx, i in enumerate(final_admin[-1]):
            if i[0] != -1:
                detail_idx = i[0] + len(final_admin[admin_idx + 1][i[1]])
                # rule: 全国地址省市无重复命名，而县级有，如鼓楼区、高新区等
                if admin_idx >= 0 and final_admin[admin_idx + 1][i[1]] not in county_dup_list:
                    final_prov = final_admin[1][0]
                if admin_idx >= 1 and final_admin[admin_idx + 1][i[1]] not in county_dup_list:
                    final_city = final_admin[2][0]
                if admin_idx >= 2 and final_admin[admin_idx + 1][i[1]] not in county_dup_list:
                    final_county = final_admin[3][0]
                else:
                    final_county = final_admin[3][i[1]]

        # 获取详细地址部分
        detail_part = location_text[detail_idx:]

        # 将地址中的 省直辖、市直辖，去掉
        if final_city is not None and '直辖' in final_city:
            final_city = None
        if final_county is not None and '直辖' in final_county:
            final_county = None

        # 获取省市区行政区划部分
        admin_part = ''
        if final_prov is not None:
            admin_part = final_prov
        if final_city is not None:
            match_muni_flag = False
            for muni_city in self.municipalities_cities:
                if muni_city in final_city:
                    match_muni_flag = True
                    break
            if not match_muni_flag:
                admin_part += final_city
        if final_county is not None:
            admin_part += final_county

        result = {'province': final_prov,
                  'city': final_city,
                  'county': final_county,
                  'detail': detail_part,
                  'full_location': admin_part + detail_part,
                  'orig_location': location_text}

        if town_village:
            result = self._get_town_village(result)

        return result

    def _get_town_village(self, result):
        # 从后续地址中，获取乡镇和村、社区信息
        town = None
        village = None

        prov = result['province']
        city = result['city'] if result['city'] is not None else '省直辖行政区划'
        county = result['county'] if result['county'] is not None else '市直辖行政区划'
        key_name = ''.join([prov, city, county])
        
        if key_name not in self.town_village_dict:
            result.update({'town': town, 'village': village})
            return result

        # 确定乡镇
        town_list = list(self.town_village_dict[key_name].keys())
        for _town in town_list:
            if _town in result['detail']:
                town = _town
                break

        # 确定村、社区
        if town is not None:
            village_list = list(self.town_village_dict[key_name][town].keys())
            for _village in village_list:
                if _village in result['detail']:
                    village = _village
                    break

        result.update({'town': town, 'village': village})
        return result


if __name__ == '__main__':
    import json
    
    lp = LocationParser()
    loc = '苏州是一座园林的城市,也是一座诗歌的城市。'
    loc = '吴江二手房出售信息。'
    loc = '秦皇岛经济技术开发区泰山路218号。'
    loc = '神木人人都很热情好客。'
    loc = '港闸区陈桥街道33号。'
    loc = '洋县谢村18号。'
    
    
    
    res = lp(loc)
    print(json.dumps(res, ensure_ascii=False,indent=4, separators=(',', ':')))
    
    province = res.get('province')
    city = res.get('city')
    county = res.get('county')
    
    print("province: {}, city: {}, county: {}".format(province, city, county))

