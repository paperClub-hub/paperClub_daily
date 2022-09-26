import collections


class TrieNode:
    """ 自定义格式 """

    def __init__(self):
        self.children = collections.defaultdict(TrieNode)
        self.is_w = False


class Trie:
    def __init__(self):
        self.root = TrieNode()
        print(self.root.children)

    def insert(self, w):
        """ 插入数据 """
        current = self.root
        for c in w:
            current = current.children[c]

        current.is_w = True

    def search(self, w):
        '''
        :param w:
        :return:
        -1:not w route
        0:subroute but not word
        1:subroute and word
        '''
        current = self.root
        for c in w:
            current = current.children.get(c)

            if current is None:
                return -1

        if current.is_w:
            return 1
        else:
            return 0

    def get_lexicon(self, sentence):
        result = []
        for i in range(len(sentence)):
            current = self.root
            for j in range(i, len(sentence)):
                current = current.children.get(sentence[j])
                if current is None:
                    break
                if current.is_w:
                    result.append([i, j, sentence[i:j + 1]])

        return result


if __name__ == '__main__':
    trie = Trie()

    words = ['北京市',
             '天津市',
             '河北省',
             '山西省',
             '内蒙古自治区',
             '辽宁省',
             '吉林省',
             '黑龙江省',
             '上海市',
             '江苏省',
             '浙江省',
             '安徽省',
             '福建省',
             '江西省',
             '山东省',
             '河南省',
             '湖北省',
             '湖南省',
             '广东省',
             '广西壮族自治区',
             '海南省',
             '重庆市',
             '四川省',
             '贵州省',
             '云南省',
             '西藏自治区',
             '陕西省',
             '甘肃省',
             '青海省',
             '宁夏回族自治区',
             '新疆维吾尔自治区', ]

    for word in words:
        trie.insert(word)
    sen = '江苏省吴中区观前街113号。'
    print(trie.get_lexicon(sen))
