from flask import Flask, render_template, request, jsonify
from key_words import get_key_words




app = Flask(__name__)



# 输出
# @app.route('/')
# def hello_world():
#     return 'Hello World!'

@app.route('/',methods=['GET','POST'])
def keyword():
    if request.method == 'POST':
        print("POST ")
        result = []
        input_text = request.form['username']
        print("input_text: ", input_text)
        if input_text:
            result = get_key_words(input_text)
            # result.append(words)
            # print(words)
            return render_template('keyword.html', name=1, results=result, input_text=input_text)
    return render_template('keyword.html', name=0)
    
    
    
    
    
    
if __name__ == '__main__':
    app.run()