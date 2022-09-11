# -*- encoding=utf-8 -*-
# ------------------------------------

from os.path import join, dirname, basename
import re
import pdb
import json
import math
import pkuseg
import numpy as np


class ChineseKeyPhrasesExtractor(object):
    """
    ChineseKeyPhrasesExtractor 类解决如下问题：
    关键短语提取在生成词云、提供摘要阅读、关键信息检索等任务中有重要作用，
    来作为文本的关键词。
    """
    def __init__(self, ):
        # 词性预处理
        self.pos_name = ['n', 't', 's', 'f', 'm', 'q', 'b', 'r', 'v', 'a', 'z',
                         'd', 'p', 'c', 'u', 'i', 'l', 'j', 'h', 'k', 'g', 'x',
                         'nr', 'ns', 'nt', 'nx', 'nz', 'vd', 'vx', 'ad', 'an']
        self.pos_exception = ['u', 'p', 'c', 'y', 'e', 'o']
        self.stricted_pos_name = ['a', 'n', 'j', 'nr', 'ns', 'nt', 'nx', 'nz', 
                                  'ad', 'an', 'vn', 'vd', 'vx']
        self.redundent_strict_pattern = re.compile('[\*\|`\;:丨－\<\>]')  # 有一个字符即抛弃
        self.redundent_loose_pattern = re.compile('[/\d\.\-:=a-z+,%]+')  # 全部是该字符即抛弃
        self.extra_date_ptn = re.compile('\d{1,2}[月|日]')
        self.exception_char_ptn = re.compile(
            '[^ ¥～「」％－＋\n\u3000\u4e00-\u9fa5\u0021-\u007e'
            '\u00b7\u00d7\u2014\u2018\u2019\u201c\u201d\u2026'
            '\u3001\u3002\u300a\u300b\u300e\u300f\u3010\u3011'
            '\uff01\uff08\uff09\uff0c\uff1a\uff1b\uff1f]')
        self._update_parentheses_ptn('{}「」[]【】()（）<>')
        self._gen_redundant_char_ptn(' -\t\n啊哈呀~')
        
        fine_punctuation='[，。;；…！、：!?？\r\n ]'
        self.puncs_fine_ptn = re.compile(fine_punctuation)
        self.idf_file_path = join(dirname(__file__), "source/idf.txt")
        self._load_idf()
        self.seg = pkuseg.pkuseg(postag=True)  # 北大分词器
        
        # 短语长度权重字典，调整绝大多数的短语要位于2~6个词之间
        self.phrases_length_control_dict = {
            1: 1, 2: 5.6, 3:1.1, 4:2.0, 5:0.7, 6:0.9, 7:0.48,
            8: 0.43, 9: 0.24, 10:0.15, 11:0.07, 12:0.05}
        self.phrases_length_control_none = 0.01  # 在大于7 时选取
        
        # 短语词性组合权重字典
        with open(join(dirname(__file__), 'source/pos_combine_weights.json'),'r', encoding='utf8') as f:
            self.pos_combine_weights_dict = json.load(f)
        
        # 读取停用词文件
        with open(join(dirname(__file__), 'source/stop_word.txt'),'r', encoding='utf8') as f:
            self.stop_words = list(set(f.read().split()))
            if '' in self.stop_words:
                self.stop_words.remove('')
            if '' not in self.stop_words:
                self.stop_words.append('\n')
                
        self._lda_prob_matrix()
        
    def _lda_prob_matrix(self):
        ''' 读取 lda 模型有关概率分布文件，并计算 unk 词的概率分布 '''
        # 读取 p(topic|word) 概率分布文件，由于 lda 模型过大，不方便加载并计算
        # 概率 p(topic|word)，所以未考虑 p(topic|doc) 概率，可能会导致不准
        # 但是，由于默认的 lda 模型 topic_num == 100，事实上，lda 模型是否在
        # 预测的文档上收敛对结果影响不大（topic_num 越多，越不影响）。
        with open(join(dirname(__file__), 'source/topic_word_weight.json'),'r', encoding='utf8') as f:
            self.topic_word_weight = json.load(f)
        self.word_num = len(self.topic_word_weight)
        
        # 读取 p(word|topic) 概率分布文件
        with open(join(dirname(__file__), 'source/word_topic_weight.json'),'r', encoding='utf8') as f:
            self.word_topic_weight = json.load(f)
        self.topic_num = len(self.word_topic_weight)
        self._topic_prominence()  # 预计算主题突出度
    
    def _load_idf(self):
        with open(self.idf_file_path, 'r', encoding='utf-8') as f:
            idf_list = [line.strip().split(' ') for line in f.readlines()]
        self.idf_dict = dict()
        for item in idf_list:
            self.idf_dict.update({item[0]: float(item[1])})
        self.median_idf = sorted(self.idf_dict.values())[len(self.idf_dict) // 2]
    
    def _update_parentheses_ptn(self, parentheses):
        ''' 更新括号权重 '''
        length = len(parentheses)
        assert len(parentheses) % 2 == 0

        remove_ptn_list = []
        remove_ptn_format = '{left}[^{left}{right}]*{right}'
        for i in range(0, length, 2):
            left = re.escape(parentheses[i])
            right = re.escape(parentheses[i + 1])
            remove_ptn_list.append(remove_ptn_format.format(left=left, right=right))
        remove_ptn = '|'.join(remove_ptn_list)
        
        self.remove_parentheses_ptn = re.compile(remove_ptn)
        self.parentheses = parentheses
        
    def _gen_redundant_char_ptn(self, redundant_char):
        """ 生成 redundant_char 的正则 pattern """
        pattern_list = []
        for char in redundant_char:
            pattern_tmp = '(?<={char}){char}+'.format(char=re.escape(char))
            # pattern_tmp = re.escape(char) + '{2,}'
            pattern_list.append(pattern_tmp)
        pattern = '|'.join(pattern_list)
        self.redundant_char_ptn = re.compile(pattern)
        
    def _preprocessing_text(self, text):
        ''' 使用预处理函数去除文本中的各种杂质 '''
        # 去除中文的异常字符
        text = self.exception_char_ptn.sub('', text)
        # 去除中文的冗余字符
        text = self.redundant_char_ptn.sub('', text)
        # 去除文本中的各种括号
        length = len(text)
        while True:
            text = self.remove_parentheses_ptn.sub('', text)
            if len(text) == length:
                break
            length = len(text)
            
        return text
    
    def _split_sentences(self, text):
        """ 将文本切分为若干句子 """
        tmp_list = self.puncs_fine_ptn.split(text)
        sentences = [sen for sen in tmp_list if sen != '']
        return sentences
    
    def extract_keyphrase(self, text, top_k=5, with_weight=False,
                          func_word_num=1, stop_word_num=0, 
                          max_phrase_len=25,
                          topic_theta=0.5, allow_pos_weight=True,
                          stricted_pos=True, allow_length_weight=True,
                          allow_topic_weight=True,
                          without_person_name=False,
                          without_location_name=False,
                          remove_phrases_list=None,
                          remove_words_list=None,
                          specified_words=dict(), bias=None):
        """
        抽取一篇文本的关键短语
        :param text: utf-8 编码中文文本
        :param top_k: 选取多少个关键短语返回，默认为 5，若为 -1 返回所有短语
        :param with_weight: 指定返回关键短语是否需要短语权重
        :param func_word_num: 允许短语中出现的虚词个数，stricted_pos 为 True 时无效
        :param stop_word_num: 允许短语中出现的停用词个数，stricted_pos 为 True 时无效
        :param max_phrase_len: 允许短语的最长长度，默认为 25 个字符
        :param topic_theta: 主题权重的权重调节因子，默认0.5，范围（0~无穷）
        :param stricted_pos: (bool) 为 True 时仅允许名词短语出现
        :param allow_pos_weight: (bool) 考虑词性权重，即某些词性组合的短语首尾更倾向成为关键短语
        :param allow_length_weight: (bool) 考虑词性权重，即 token 长度为 2~5 的短语倾向成为关键短语
        :param allow_topic_weight: (bool) 考虑主题突出度，它有助于过滤与主题无关的短语（如日期等）
        :param without_person_name: (bool) 决定是否剔除短语中的人名
        :param without_location_name: (bool) 决定是否剔除短语中的地名
        :param remove_phrases_list: (list) 将某些不想要的短语剔除，使其不出现在最终结果中
        :param remove_words_list: (list) 将某些不想要的词剔除，使包含该词的短语不出现在最终结果中
        :param specified_words: (dict) 行业名词:词频，若不为空，则仅返回包含该词的短语
        :param bias: (int|float) 若指定 specified_words，则可选择定义权重增加值
        :return: 关键短语及其权重
        """ 
        try:
            # 配置参数
            if without_location_name:
                if 'ns' in self.stricted_pos_name:
                    self.stricted_pos_name.remove('ns')
                if 'ns' in self.pos_name:
                    self.pos_name.remove('ns')
            else:
                if 'ns' not in self.stricted_pos_name:
                    self.stricted_pos_name.append('ns')
                if 'ns' not in self.pos_name:
                    self.pos_name.append('ns')

            if without_person_name:
                if 'nr' in self.stricted_pos_name:
                    self.stricted_pos_name.remove('nr')
                if 'nr' in self.pos_name:
                    self.pos_name.remove('nr')
            else:
                if 'nr' not in self.stricted_pos_name:
                    self.stricted_pos_name.append('nr')
                if 'nr' not in self.pos_name:
                    self.pos_name.append('nr')

            # step0: 清洗文本，去除杂质
            text = self._preprocessing_text(text)
            
            # step1: 分句，使用北大的分词器 pkuseg 做分词和词性标注
            sentences_list = self._split_sentences(text) ### 句子跌断
            sentences_segs_list = list() #### 分此后 +词性
            counter_segs_list = list()
            for sen in sentences_list:
                sen_segs = self.seg.cut(sen)
                sentences_segs_list.append(sen_segs)
                counter_segs_list.extend(sen_segs)

            # step2: 计算词频
            total_length = len(counter_segs_list)
            freq_dict = dict()
            for word_pos in counter_segs_list:
                word, pos = word_pos
                if word in freq_dict:
                    freq_dict[word][1] += 1
                else:
                    freq_dict.update({word: [pos, 1]})
            
            
            # step3: 计算每一个词的权重
            sentences_segs_weights_list = list()
            for sen, sen_segs in zip(sentences_list, sentences_segs_list):
                sen_segs_weights = list()
                for word_pos in sen_segs:
                    word, pos = word_pos
                    if pos in self.pos_name:  # 虚词权重为 0
                        if word in self.stop_words:  # 停用词权重为 0
                            weight = 0.0
                        else:
                            if word in specified_words:  # 为词计算权重
                                if bias is None:
                                    weight = freq_dict[word][1] * self.idf_dict.get(
                                        word, self.median_idf) / total_length + 1 / specified_words[word]
                                else:
                                    weight = freq_dict[word][1] * self.idf_dict.get(
                                        word, self.median_idf) / total_length + bias
                            else:
                                weight = freq_dict[word][1] * self.idf_dict.get(
                                    word, self.median_idf) / total_length
                    else:
                        weight = 0.0
                    sen_segs_weights.append(weight)
                sentences_segs_weights_list.append(sen_segs_weights)

            # step4: 通过一定规则，找到候选短语集合，以及其权重
            candidate_phrases_dict = dict()
            for sen_segs, sen_segs_weights in zip(
                sentences_segs_list, sentences_segs_weights_list):
                sen_length = len(sen_segs)

                for n in range(1, sen_length + 1):  # n-grams
                    for i in range(0, sen_length - n + 1):
                        candidate_phrase = sen_segs[i: i + n]

                        # 由于 pkuseg 的缺陷，日期被识别为 n 而非 t，故删除日期
                        res = self.extra_date_ptn.match(candidate_phrase[-1][0])
                        if res is not None:
                            continue

                        # 找短语过程中需要进行过滤，分为严格、宽松规则
                        if not stricted_pos:  
                            rule_flag = self._loose_candidate_phrases_rules(
                                candidate_phrase, func_word_num=func_word_num,
                                max_phrase_len=max_phrase_len,  
                                stop_word_num=stop_word_num)
                        else:
                            rule_flag = self._stricted_candidate_phrases_rules(
                                candidate_phrase, max_phrase_len=max_phrase_len)
                        if not rule_flag:
                            continue

                        # 由于 pkuseg 的缺陷，会把一些杂质符号识别为 n、v、adj，故须删除
                        redundent_flag = False
                        for item in candidate_phrase:
                            matched = self.redundent_strict_pattern.search(item[0])
                            if matched is not None:
                                redundent_flag = True
                                break
                            matched = self.redundent_loose_pattern.search(item[0])

                            if matched is not None and matched.group() == item[0]:
                                redundent_flag = True
                                
                                break
                        if redundent_flag:
                            continue
                            
                        # 如果短语中包含了某些不想要的词，则跳过
                        if remove_words_list is not None:
                            unwanted_phrase_flag = False
                            for item in candidate_phrase:
                                if item[0] in remove_words_list:
                                    unwanted_phrase_flag = True
                                    break
                            if unwanted_phrase_flag:
                                continue

                        # 如果短语中没有一个 token 存在于指定词汇中，则跳过
                        if specified_words != dict():
                            with_specified_words_flag = False
                            for item in candidate_phrase:
                                if item[0] in specified_words:
                                    with_specified_words_flag = True
                                    break
                            if not with_specified_words_flag:
                                continue

                        # 条件六：短语的权重需要乘上'词性权重'
                        if allow_pos_weight:
                            start_end_pos = None
                            if len(candidate_phrase) == 1:
                                start_end_pos = candidate_phrase[0][1]
                            elif len(candidate_phrase) >= 2:
                                start_end_pos = candidate_phrase[0][1] + '|' + candidate_phrase[-1][1]
                            pos_weight = self.pos_combine_weights_dict.get(start_end_pos, 1.0)
                        else:
                            pos_weight = 1.0

                        # 条件七：短语的权重需要乘上 '长度权重'
                        if allow_length_weight:
                            length_weight = self.phrases_length_control_dict.get(
                                len(sen_segs_weights[i: i + n]), 
                                self.phrases_length_control_none)
                        else:
                            length_weight = 1.0

                        # 条件八：短语的权重需要加上`主题突出度权重`
                        if allow_topic_weight:
                            topic_weight = 0.0
                            for item in candidate_phrase:
                                topic_weight += self.topic_prominence_dict.get(
                                    item[0], self.unk_topic_prominence_value)
                            topic_weight = topic_weight / len(candidate_phrase)
                        else:
                            topic_weight = 0.0

                        candidate_phrase_weight = sum(sen_segs_weights[i: i + n])
                        candidate_phrase_weight *= length_weight * pos_weight
                        candidate_phrase_weight += topic_weight * topic_theta

                        candidate_phrase_string = ''.join([tup[0] for tup in candidate_phrase])
                        if remove_phrases_list is not None:
                            if candidate_phrase_string in remove_phrases_list:
                                continue
                        if candidate_phrase_string not in candidate_phrases_dict:
                            candidate_phrases_dict.update(
                                {candidate_phrase_string: [candidate_phrase, 
                                                           candidate_phrase_weight]})

            # step5: 将 overlaping 过量的短语进行去重过滤
            # 尝试了依据权重高低，将较短的短语替代重复了的较长的短语，但效果不好，故删去
            candidate_phrases_list = sorted(
                candidate_phrases_dict.items(), 
                key=lambda item: len(item[1][0]), reverse=True)

            de_duplication_candidate_phrases_list = list()
            for item in candidate_phrases_list:
                sim_ratio = self._mmr_similarity(
                    item, de_duplication_candidate_phrases_list)
                if sim_ratio != 1:
                    item[1][1] = (1 - sim_ratio) * item[1][1]
                    de_duplication_candidate_phrases_list.append(item)

            # step6: 按重要程度进行排序，选取 top_k 个
            candidate_phrases_list = sorted(de_duplication_candidate_phrases_list, 
                                            key=lambda item: item[1][1], reverse=True)

            if with_weight:
                if top_k != -1:
                    final_res = [(item[0], item[1][1]) for item in candidate_phrases_list[:top_k]
                                 if item[1][1] > 0]
                else:
                    final_res = [(item[0], item[1][1]) for item in candidate_phrases_list
                                 if item[1][1] > 0]
            else:
                if top_k != -1:
                    final_res = [item[0] for item in candidate_phrases_list[:top_k]
                                 if item[1][1] > 0]
                else:
                    final_res = [item[0] for item in candidate_phrases_list
                                 if item[1][1] > 0]
            return final_res

        except Exception as e:
            print('the text is not legal. \n{}'.format(e))
            return []

    def _mmr_similarity(self, candidate_item, 
                        de_duplication_candidate_phrases_list):
        ''' 计算 mmr 相似度，用于考察信息量 '''
        sim_ratio = 0.0
        candidate_info = set([item[0] for item in candidate_item[1][0]])
        
        for de_du_item in de_duplication_candidate_phrases_list:
            no_info = set([item[0] for item in de_du_item[1][0]])
            common_part = candidate_info & no_info
            if sim_ratio < len(common_part) / len(candidate_info):
                sim_ratio = len(common_part) / len(candidate_info)
        return sim_ratio
        
    def _loose_candidate_phrases_rules(self, candidate_phrase,
                                       max_phrase_len=25, 
                                       func_word_num=1, stop_word_num=0):
        ''' 按照宽松规则筛选候选短语，对词性和停用词宽松 '''
        # 条件一：一个短语不能超过 12个 token
        if len(candidate_phrase) > 12:
            return False

        # 条件二：一个短语不能超过 25 个 char
        if len(''.join([item[0] for item in candidate_phrase])) > max_phrase_len:
            return False

        # 条件三：一个短语中不能出现超过一个虚词
        more_than_one_func_word_count = 0
        for item in candidate_phrase:
            if item[1] in self.pos_exception:
                more_than_one_func_word_count += 1
        if more_than_one_func_word_count > func_word_num:
            return False

        # 条件四：短语的前后不可以是虚词、停用词，短语末尾不可是动词
        if candidate_phrase[0][1] in self.pos_exception:
            return False
        if candidate_phrase[len(candidate_phrase)-1][1] in self.pos_exception:
            return False
        if candidate_phrase[len(candidate_phrase)-1][1] in ['v', 'd']:
            return False
        if candidate_phrase[0][0] in self.stop_words:
            return False 
        if candidate_phrase[len(candidate_phrase)-1][0] in self.stop_words:
            return False

        # 条件五：短语中不可以超过规定个数的停用词
        has_stop_words_count = 0
        for item in candidate_phrase:
            if item[0] in self.stop_words:
                has_stop_words_count += 1
        if has_stop_words_count > stop_word_num:
            return False
        return True
    
    def _stricted_candidate_phrases_rules(self, candidate_phrase, 
                                          max_phrase_len=25):
        ''' 按照严格规则筛选候选短语，严格限制在名词短语 '''
        # 条件一：一个短语不能超过 12个 token
        if len(candidate_phrase) > 12:
            return False

        # 条件二：一个短语不能超过 25 个 char
        if len(''.join([item[0] for item in candidate_phrase])) > max_phrase_len:
            return False

        # 条件三：短语必须是名词短语，不能有停用词
        for idx, item in enumerate(candidate_phrase):
            if item[1] not in self.stricted_pos_name:
                return False
            if idx == 0:  # 初始词汇不可以是动词
                if item[1] in ['v', 'vd', 'vx']:  # 动名词不算在内
                    return False
            if idx == len(candidate_phrase) - 1:  # 结束词必须是名词
                if item[1] in ['a', 'ad', 'vd', 'vx', 'v']:
                    return False

        # 条件四：短语中不可以有停用词
        #for item in candidate_phrase:
        #    if item[0] in self.stop_words and item[1] not in self.stricted_pos_name:
        #        return False
        return True
        
    def _topic_prominence(self):
        ''' 计算每个词语的主题突出度，并保存在内存 '''
        init_prob_distribution = np.array([self.topic_num for i in range(self.topic_num)])
        
        topic_prominence_dict = dict()
        for word in self.topic_word_weight:
            conditional_prob_list = list()
            for i in range(self.topic_num):
                if str(i) in self.topic_word_weight[word]:
                    conditional_prob_list.append(self.topic_word_weight[word][str(i)])
                else:
                    conditional_prob_list.append(1e-5)
            conditional_prob = np.array(conditional_prob_list)
            
            tmp_dot_log_res = np.log2(np.multiply(conditional_prob, init_prob_distribution))
            kl_div_sum = np.dot(conditional_prob, tmp_dot_log_res)  # kl divergence
            topic_prominence_dict.update({word: float(kl_div_sum)})
            
        tmp_list = [i[1] for i in tuple(topic_prominence_dict.items())]
        max_prominence = max(tmp_list)
        min_prominence = min(tmp_list)
        for k, v in topic_prominence_dict.items():
            topic_prominence_dict[k] = (v - min_prominence) / (max_prominence - min_prominence)
            
        self.topic_prominence_dict = topic_prominence_dict
        
        # 计算未知词汇的主题突出度，由于停用词已经预先过滤，所以这里不需要再考停用词无突出度
        tmp_prominence_list = [item[1] for item in self.topic_prominence_dict.items()]
        self.unk_topic_prominence_value = sum(tmp_prominence_list) / (2 * len(tmp_prominence_list))


if __name__ == '__main__':
    
    extractor_obj = ChineseKeyPhrasesExtractor()
    text = '张爱玲曾说人生有“三大恨”：一恨海棠无香；二恨鲥鱼多刺；三恨红楼梦未完。林青霞的床头总摆着一本《红楼梦》，以便不时翻看。《红楼梦》是一部天书，是中国最伟大的小说，魅力自不需多说，书中的丰厚积淀，也让文学大家为之倾倒，其中包括著名作家、名将白崇禧之子白先勇。著名小说家白先勇从小学五六年级就开始看《红楼梦》，著书之后笑谈：曹雪芹是我的“师父”，《红楼梦》是我的文学圣经、我写作的百科全书。在1965年至1994年间，白先勇在美国加州大学教《红楼梦》，这一教就是整整二十九年。电视剧《红楼梦》剧照2014年起，他受邀回到母校台湾大学开设通识课，将毕生对《红楼梦》的钻研体会倾囊相授。他不是所谓的红学家，也不执著于从考据出发来解读文本，只是从另一个小说家、文学创作者的角度，擦去经典的蒙尘之处，将历来被冷落的人物、被曲解的角色一一归还原本的个性姿彩，令其登台绽放。大家都知道，自《红楼梦》问世以来，关于后四十回是否是曹雪芹本人所写的问题，一直争论不断。很多红学家研究，说曹雪芹这本书后四十回不是他写的，是高鹗续的。但白先勇的观点是：除了曹雪芹，还有谁能把《红楼梦》后四十回写得这么好？他比较倾向的说法是，后四十回曹雪芹早有了稿子，这稿子佚失了，后来程伟元他们又去一点一点收回来，可能有一些未定稿，是由高鹗修订完成的。这个结论绝不是先生拍大腿所想，而是有着相对严密的逻辑，首先最重要的一点就是：前八十回的千里伏笔，后四十回都那么巧妙地收了回来。秦钟的再次出现、鸳鸯自杀前拿起曾绞下的头发等细节，不仅细致入微，还与前文形成了极好的呼应，续书者很难有如此细微的布局。电视剧《红楼梦》剧照第二点是：后四十回，人物说话的口气完全没有变。白先勇说，后面贾府逐渐衰败，文字风格确实与前八十回的花团锦簇不同，但是后面宝钗讲话、薛姨妈讲话，跟前面都对得起来，虽然后面讲的都是伤心的话，可是口气还是一样。从创作的角度出发，“人物语气的笔调”保持了连贯性，不得不说，这是白先生的慧眼独具。当然还有个原因，后面有几回写得相当精彩。曹雪芹写这本书，肯定有很深的自传成分在里头，所以他写起来等于是一本《追忆似水年华》，前面写得兴高采烈，后面写得满腔悲哀愁绪。某一种了悟之后，他对人世间有那么深刻的怜悯（compassion），如果是另外一个人，没有实际经历过像曹雪芹家里的事情，后面四十回哪有可能跟他一样，有那么深层的感情在里头。尤其宝玉别离的那一段，就够让人心酸的了。许多红学家，往往从考据的角度旁征博引，质疑与贬低后四十回，也只有白先勇这种同为小说家，而且人间阅历及其细腻与丰富的作者，才能看到这一层逻辑关系。电视剧《红楼梦》剧照曹雪芹在《红楼梦》里大量刻画女性角色，从金陵十二钗到各种太太姨娘，角色类型和层次可以说应有尽有。对于这种尝试，白先勇充满了赞扬：《红楼梦》在某方面是曹雪芹塑造的女儿乌托邦。第一次中国小说里头女性角色占有那么大的比例，而且是那么重要的位置。态度很要紧，曹雪芹这种对女性很爱慕、尊敬、怜惜的态度，在中国小说里面不太有。中国的传统里面，中国的文人对女性方面心理的描写，还有情感的认同，很特殊的。《水浒》《金瓶梅》这些著作对女性的看法，从现在来讲恐怕有点男性大沙文主义。曹雪芹却不是，曹雪芹对女孩非常体贴。女孩子对他来讲是一种精神上的素质，青春的，提升人的，很纯洁的。这种视角和突破，可以说曹雪芹本人的家世和心性不无关系，而且如果用现代人的视角来看，能写出《红楼梦》的曹雪芹，完全就是一个具备美学鉴赏的艺术家。白先勇说，大观园里面的春夏秋冬，有不同美景和享受，在贾府极盛的时候，这个冬天，是什么样的世界呢？是琉璃世界、白雪红梅，多么鲜艳的一幅景象。还加上这些女孩子穿上了各式各样的冬服，拥裘披氅，曹雪芹又大大展现了他写服装的功夫。白先勇还调侃道，说曹雪芹就是个时装设计师（fashiondesigner）。初读《红楼梦》的读者，应该都曾被书中人物的服装所震撼到，在黛玉刚进贾府的时候，看到“三春”姐妹的装扮，以及王熙凤出场，那一身穿金戴银的样精织细绣（elaborate），印象应该都非常深刻。白先勇一语道破这里的背景文化，所谓观衣观人，衣服就代表了人的身份、个性、气质，她的社会地位（socialstatus），所以服装在《红楼梦》里占有很重要的地位，不是随便写的。在重要的场合，要突出哪一个人的时候，就给她穿什么。试想如果王熙凤进来那个场合，随便写两笔，穿个褂子什么的，我们对王熙凤的印象就完全不对了，现在我们永远记得她的第一次亮相。从小细节到大格局，白先勇把《红楼梦》的里里外外讲得干净透彻，为我们复原了属于那个年代的中国美学式的生活史。此次，《白先勇细说红楼梦》的音频课，以白先勇在台湾大学《红楼梦》三学期授课的原始音频为底本，经过后期精修制作而成，配以课堂名词、诗词注释，升级播出。扫描图中二维码即可订阅课程八十岁的白先勇，遇见三百岁的曹雪芹，两位小说家跨越时空的心灵相印，我们有幸得以观赏。作家梁文道说：白先勇身为华人世界最优秀的作者之一，写了几十年小说，教了几十年的小说，穷毕生之力，终于现在跟大家一回一回地讲下来《红楼梦》这部中国古典文化集大成的宝库。我听过很多人讲《红楼梦》、也看过很多人写《红楼梦》，但我必须说，现在再听白老师讲《红楼梦》，真是耳目一新。在这档音频节目中，白先勇从小说艺术的角度细说曹雪芹的谋篇布局、人物形象与意涵等等，将自己对于中国传统文化艺术的知识与见解融贯其中，这是其他人讲解《红楼梦》难以做到的。课程亮点01120回原文逐回精细解读，极致品味红楼语言之美从叙事手法，到人物性格刻画、形象塑造、对话技巧以及《红楼梦》的悲剧色彩和艺术风格字句无巨细，具体有创见白先勇讲王熙凤出场“未见其人，先闻其声”——02小说家视角读小说，调转180°揣摩曹公创作之道以当代新潮文学观点、美学理论观照《红楼梦》创作手法、作品立意以通俗语言带你走进曹雪芹的内心众多红学疑问不言自明白先勇讲曹雪芹创作体感——03思想性艺术性高度结合，从红楼琼宇漫谈文化之景精读文本、但绝不拘泥于文本而是从《红楼梦》说开去勾连文学、美学、哲学、昆曲的枝枝蔓蔓漫步中国传统文化全景白先勇讲甄士隐命运——课程结构限时特惠：98元原价：128元扫描图中二维码即可订阅课程'
    text = '"原标题:《巩义市大南沟村举行生态文明建设推进会》记者报讯（阮中华）8月27日上午，秋高气爽，艳阳高照。大南沟村生态文明建设推进会在巩义市涉村镇大南沟村Hei金工坊举行。推进会上，北京绿十字宣传大使、中部生态保育联盟轮值主席叶榄向与会村民们讲解了环保酵素的制作方法，呼吁大家行动起来，利用水果皮、剩菜叶制作环保酵素，夯实垃圾分类，减少厨余，改良土壤，保护生态，把生态文明落实到乡村生活、生产的点点滴滴之中。大南沟村生态文明银行行长曹志红带领垃圾分类志愿者们现场制作了16桶1000余斤环保酵素。星空农道驻场设计师刘艳辉、赵乐乐，傲蓝得总公司技术部研究员曹云飞等也参加了推进会。推进会上，叶榄还就《大南沟村生态文明家庭公约》征求了村民们的意见，大家纷纷举手表决通过。据悉，这是首次在乡村开展的“生态文明家庭公约进家庭”活动，是乡村振兴的新尝试。本次推进会由河南省生态文明建设促进会千手行动组委会、北京绿十字、星空农道、中部生态保育联盟、大南沟村联合主Ban，目的是进一步推动生态文明在大南沟的落地，完善原种农业，夯实大南沟村生态文明银行已经取得的成果。“制作环保酵素，推广生态文明家庭公约，对于我们大南沟村的生态文明建设来说，具有十分重要的意义，我们会努力做好，向省市级文明村迈进。”大南沟村支部书记李向林信心满满地表示。编辑：陈菲记者报讯（阮中华）8月27日上午，秋高气爽，艳阳高照。大南沟村生态文明建设推进会在巩义市涉村镇大南沟村Hei金工坊举行。推进会上，北京绿十字宣传大使、中部生态保育联盟轮值主席叶榄向与会村民们讲解了环保酵素的制作方法，呼吁大家行动起来，利用水阅读全文注：《巩义市大南沟村举行生态文明建设推进会》一文由新都香城热线智能聚合数据系统收集整理于网络，版权归原作者、网站所有，不代表本站支持本文观点，如有疑问请与我们取得联系，我们将在第一时间处理您的诉求。处理诉求请提供有效身份证明与其他相关材料，联系方式：domain91#foxmail.com"'
    text = '"「金住奖-中国居住空间设计年度评选」是首个以业主宜居指数为评判标准的中国居住空间设计师大型年度盘点，秉承“房子是用来住的，不只是用来看的”的理念，倡导“做有温度的居住空间设计”，在全国范围寻找优秀的空间设计，发布并表彰全国各城市最具宜居设计力的居住空间设计师和机构，助力国内家居设计优秀力量的成长。2020金住奖自5月正式启动以来，四个月间一路乘风破浪，在全国近30个城市举办启动礼、圆桌会议、金住讲堂等系列活动，所到之处皆掀起居住空间设计活动热潮，得到了中国居住空间设计及相关业界的广泛认同和高度赞许，吸引了超过200个城市的居住空间设计师瞩目和参评。▲部分巡回活动现场图经过数日的严格审核和筛选，「金住奖-2020中国（城市）十大居住空间设计师」第四批获选名单公布！来自达州、恩施、广元、桂林、海宁、嘉善、江门、昆山、丽水、娄底、眉山、绵阳、南昌、南阳、宁乡、钦州、清远、三亚、厦门、上饶、顺德、苏州、遂宁、太仓、天津、桐乡、威海、文山、西宁、孝义、烟台、宜春、益阳、张家港、肇庆、中山、驻马店共37个城市的317位优秀设计师荣耀当选。（*按城市首字母排序）▼金住奖-2020中国（达州）十大居住空间设计师占光飞、庞毅、陈军、何杰、曹亚彬陈小明、陈海洋、唐秋林、孙凯、张祥平金住奖-2020中国（恩施）十大居住空间设计师毛莉萍、余敏、王为斌、徐士杰、张琴谢越、石驻、谭振、崔焕欣、康孟起金住奖-2020中国（广元）十大居住空间设计师许凡、易武、陈洋、王兰刘洋、张佩楠、徐莉琼金住奖-2020中国（桂林）十大居住空间设计师陆勇、刘强、周仁、周晓东、张三又徐润、叶小舟、彭德华、翟启秀金住奖-2020中国（海宁）十大居住空间设计师黄金、冷俊、马春杰、王帼嫔、王巍梅展、忻立明、叶球球、叶吴钢、张伟金住奖-2020中国（嘉善）十大居住空间设计师陈鑫刚、傅建明、高超、鲁留成、骆淑琴屠晓蔚、薛佳平、俞亮、周华东、朱未金住奖-2020中国（江门）十大居住空间设计师张竟成、区晓琳、黄杏玲、宋波、陆鑫金住奖-2020中国（昆山）十大居住空间设计师孙岩、黄小米、曾东、沈佳斌、陆敏谢文静、薄海、李玖洲、杜建亚、刘德彬金住奖-2020中国（丽水）十大居住空间设计师杜志涛、潘凯、谢维光、杨君、吕丽林璐、王春标、留旭丰、蒋涛、丁宝金住奖-2020中国（娄底）十大居住空间设计师刘文、周波、周卫煌、刘正华殷浩、李晨曦、王坚柱、朱平波金住奖-2020中国（眉山）十大居住空间设计师刘宇、余雪松、程应红、杨钦淋黄璜、王晓华、赵芝霞、蒋磊金住奖-2020中国（绵阳）十大居住空间设计师高萌、骆刚、尹雪梅、朱武元、何天均唐毓军、龚小红、吴松柏、赵婧、周江华金住奖-2020中国（南昌）十大居住空间设计师刘如月、陈经纬、彭玉婷、段翌、王忠黄俊宁、万仁涛、余静林、李合平、祝国华金住奖-2020中国（南阳）十大居住空间设计师王君乐、谢英顺、张俊朋、杨瑞娜、琚艳艳晋双喜、周迎深、陈二涛、刘志刚、赵杏金住奖-2020中国（宁乡）十大居住空间设计师陈涛、刘芳、刘韬刘晓明、王炫、许桂堂金住奖-2020中国（清远）十大居住空间设计师蔡家艺、江君城、刘建业、龙静梅、马智才戚亦龙、叶嘉俊、张亚平、钟宇健金住奖-2020中国（钦州）十大居住空间设计师陆涛、褚之零、卜俊文、梁昌览、高波施其星、谢永强、章海俊、潘胜官、苏奖城金住奖-2020中国（三亚）十大居住空间设计师文子天、莫琴珠、罗长城、成炜、余剑金住奖-2020中国（厦门）十大居住空间设计师王仁宏、张以辉、苏成溪、郑熹张盛浪、方盾、冯伟斌、卢北京金住奖-2020中国（上饶）十大居住空间设计师张燕苹、金佳鑫、何克飞、潘自平、徐亮陈文斯、冷凌峰、胡东平、童振锋、郑丽婷金住奖-2020中国（顺德）十大居住空间设计师黄陆强、罗咏梅、金石、周健嘉、黄铭超金住奖-2020中国（苏州）十大居住空间设计师邢雅婧、周冰、李文生、王晓燕、尉茗珈柳雨彤、阿布、叶婷、邢斐、周东付金住奖-2020中国（遂宁）十大居住空间设计师殷切、霍成、蔺伟谭海莉、蒲剑、陈炜金住奖-2020中国（太仓）十大居住空间设计师陈荣、张冰华、钱生、倪森钊、陈丽娟程磊、冷景光、唐维成、程军、张明涛金住奖-2020中国（天津）十大居住空间设计师王万飞、王庭栋、张俊熙、罗春、顾铄李凯、肖磊、高云皓、马鑫、闫凯金住奖-2020中国（桐乡）十大居住空间设计师李峰、刘炽、刘汉雨、强叶、吴堪吴子恒、徐燕、姚晓康、朱海鹏、朱洁媚金住奖-2020中国（威海）十大居住空间设计师王海桥、郝晓雷、马巍王晓龙、周建玲、余雲磊金住奖-2020中国（文山）十大居住空间设计师曾红霞、刘果、阮东林、张壮勇、李然金住奖-2020中国（西宁）十大居住空间设计师张宇飞、宋超、肖儒、张莉莉、靳聪吕云翔、廖峻辉、张海波、唐倍、陈夏金住奖-2020中国（烟台）十大居住空间设计师刘受星、唐远、朱万、肖燕华、刘亚洲薛雅之、李元芳、韩青华、夏宇、刘彬金住奖-2020中国（宜春）十大居住空间设计师陈健、李雯、梅江林、彭招兰、向磊肖朝晖、袁芳芳、郑旭、何征金住奖-2020中国（益阳）十大居住空间设计师周兵、谢蓝、熊雪姣、赵祎、郭时兵金住奖-2020中国（张家港）十大居住空间设计师曹翔宇、丁磊、邹闵娟、倪春燕、孙晓迎童一宸、杨磊、姜浩、聂丹、严政东金住奖-2020中国（肇庆）十大居住空间设计师徐鹏、谭程月、吴英翔、党月、吴敦良伍金明、冷小宁、熊华、刘婵金住奖-2020中国（中山）十大居住空间设计师林淑芹、宋红燕、林慧鑫、林伟维、杨淳智熊新华、麻新民、张吉旺、阮慧杰、陈勤勤金住奖-2020中国（驻马店）十大居住空间设计师陈洁、刘磊、林沐、刘晴李秀娟、乔楠、张琦‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍恭喜以上获选金住奖-2020中国（城市）十大居住空间设计师的优秀代表！至此，“金住奖-2020中国（城市）十大居住空间设计师”的获奖名单已全部发布完毕。接下来，“城市十大”获选设计师在评审委员会的严格评选下，在“金住奖-2020中国百杰居住空间设计师”评选中展开激烈竞逐，最终争夺“金住奖-2020中国十大居住空间设计师”殊荣，期待更多的荣誉绽放！2020金住奖榜单发布日程10月26日-11月11日金住奖-2020中国（城市）十大居住空间设计师获选名单公布「往期名单回顾」2020金住奖|翘首以盼，首批城市十大居住空间设计师荣誉揭晓！2020金住奖|荣誉待查收，第二批城市十大名单重磅出炉！2020金住奖|第三批城市十大名单强势来袭，51城荣誉发布11月20日金住奖-2020中国百杰居住空间设计师获选名单公布11月25日金住奖-2020中国十大居住空间设计师荣誉揭晓12月3-6日广州设计周现场金住奖-2020年度盛典▲2020金住奖中国居住空间设计年度盛典金住奖认为“房子是用来住的，不只是用来看的”，倡导“做有温度的居住空间设计”，是首个以业主宜居指数为评判标准的中国居住空间设计大型年度盘点。2020金住奖覆盖了200+城市居住空间设计圈层，为全国范围内的居住空间设计师们赋能。4天时间，将持续为200+城市的设计师授予“金住奖-2020中国（城市）十大居住空间设计师”荣誉，并进阶揭晓和颁发“金住奖-2020中国百杰居住空间设计师”及“金住奖-2020中国十大居住空间设计师”殊荣。年度盛典活动安排总览：（以最终通知为准）时间：2020年12月3-6日地点：广州国际采购中心10号馆▼金住奖-中国居住空间设计年度评选（简称：金住奖）由亚洲首屈一指的设计产业资源价值平台—广州设计周、装饰行业在线学习平台—饰道共同发起主办，金住奖认为“房子是用来住的，不只是用来看的”，倡导“做有温度的居住空间设计”，是首个以业主宜居指数为评判标准的中国居住空间设计师大型年度盘点。金住奖通过每年度举办“设计评选、交流论坛、在线讲堂”等系列活动内容，发布并表彰全国各城市最具宜居设计力的居住空间设计师和机构，同时促进全国居住空间设计优秀力量的联动成长，希冀打造最受业主青睐的居住空间设计师展示平台。组织机构主办单位：广州设计周、饰道承办单位：广州设计周文化传播有限公司、广州欣脉联信息科技有限公司城市运营机构：广州设计周全球伙伴联盟（GIA）战略合作媒体：设计纪元、搜狐焦点家居、建材天地战略合作伙伴：华鹏陶瓷奖杯荣誉承制：木里木外年度盛典合作伙伴：九牧、ING+照明、CBD、卡利亚不锈钢橱柜金住奖联合主办机构饰道-装饰行业在线学习平台，以知识点短视频为入口，以系统性课程为核心，同时提供行业全年论坛、峰会、大咖等视频直播分享，为室内设计师职业进阶赋能，目前平台已有29万+知识点短视频，用户超过30万。-END-请即刻扫码直通2020广州设计周"'
    
    key_phrases = extractor_obj.extract_keyphrase(text, top_k=20,
                                                  max_phrase_len = 10,
                                                  with_weight=True,
                                                  remove_phrases_list=['剧照曹雪芹'],
                                                  remove_words_list=['TEL', 'COM', '@'])
    
    print(key_phrases)
    
    