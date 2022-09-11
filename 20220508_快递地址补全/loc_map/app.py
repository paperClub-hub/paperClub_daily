from flask import Flask, render_template, request, jsonify
from location_mapper import LocationParser

app = Flask(__name__)

loc = LocationParser()

# 输出
@app.route('/test')
def hello_world():
    return 'Hello World!'

#如果访问的是/search页面的post请求，则调用send_post（）方法
# @app.route('/search',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
def search():
    if request.method == 'POST':
        input_text = request.form['username']
        if input_text:
            dat = loc(input_text)
            result = []
            if dat.get("province"):
                result.append(dat)
            else:
                #print(dat.get("province"))
                dat['detail'] = 'None'
                dat['full_location'] = 'None'
                result.append(dat)
        
            return render_template('index.html', name=1, results=result)
        return render_template('index.html', name=0)
        
    print("GET ...")
    return render_template('index.html', name=0)
    
    
    
    

#封装请求百度接口的方法
def send_post(name):
    import requests
    url = 'http://sp0.baidu.com/common/api/yaohao'
    data = {
        'name': name,
        'city': '深圳'
    }
    #使用requests的get请求，返回json格式
    res = requests.get(url=url,params=data).json()
    #json.dumps将字典转换为json
    return "<h3>"+json.dumps(res)+"</h3>"

if __name__ == '__main__':
    app.run()