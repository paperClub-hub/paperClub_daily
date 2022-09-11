
from sklearn.model_selection import train_test_split
from IPython.display import Image
from sklearn.linear_model import Perceptron
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
# from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.metrics import accuracy_score
import pandas as pd

### 加载数据集
iris = pd.read_csv('../data/iris.csv')
iris.rename(columns={"sepal.length": "sepal_length",
                     "sepal.width": "sepal_width",
                     "petal.length": "petal_length",
                     "petal.width": "petal_width"},
            inplace=True)


X = iris.iloc[:, [2, 3]].values ## 第3/4列数据
# X = iris.iloc[:, [2]].values ## 第3/4列数据
y = iris['target'] = iris['variety'].astype('category').cat.codes
## 编码字典
target2label = dict(zip(iris['variety'].values, iris['target'].values))


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
sc = StandardScaler()   #初始化一个对象sc去对数据集作变换, 数据标准化，
sc.fit(X_train)
print(sc.scale_) ## 标准化后每列的标准差
print(sc.mean_) ### 标准化后每列的均值

X_train_std = sc.transform(X_train)
X_test_std = sc.transform(X_test)
print(X_train_std.shape, X_test_std.shape)


from sklearn.linear_model import Perceptron

ppn = Perceptron()  #y=w.x+b
ppn.fit(X_train_std, y_train)

y_pred = ppn.predict(X_test_std)  #对测试集做类别预测


print('Misclassified samples: %d' % (y_test != y_pred).sum())
#Output:Misclassified samples: 3
from sklearn.metrics import accuracy_score
print('Accuracy: %.2f' % accuracy_score(y_test, y_pred))  #预测准确度,(len(y_test)-3)/len(y_test):0.9333333333333333

