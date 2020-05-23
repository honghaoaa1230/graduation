from flask import Flask
from flask import redirect
from flask import jsonify
from flask import request

import tensorflow as tf
from PIL import Image
import numpy as np
import os
import requests
import json

from train import CNN

app = Flask.Flask(__name__)

picnum = 10
class Predict(object):
    def __init__(self):
        latest = tf.train.latest_checkpoint('./ckpt')
        self.cnn = CNN()
        # 恢复网络权重
        self.cnn.model.load_weights(latest)

    def predict(self, image_path):
        # 以黑白方式读取图片
        img = Image.open(image_path).convert('L')
        img = img.resize((28, 28),Image.ANTIALIAS)
        flatten_img = np.reshape(img, (28, 28, 1))
        x = np.array([1 - flatten_img])

        # API refer: https://keras.io/models/model/
        y = self.cnn.model.predict(x)

        # 因为x只传入了一张图片，取y[0]即可
        # np.argmax()取得最大值的下标，即代表的数字
        print(image_path)
        print(y[0])
        print('        -> Predict digit', np.argmax(y[0]))
        result = str(y[0]) + '\n' + '        -> Predict digit ' + str(np.argmax(y[0]))
        return result

# class Predict1(object):
#     def __init__(self):
#         latest = tf.train.latest_checkpoint('./ckpt')
#         self.cnn = CNN()
#         # 恢复网络权重
#         self.cnn.model.load_weights(latest)

#     def predict(self,image_url):
#         # 以黑白方式读取图片
#         global picnum
#         urlretrieve(image_url, '../test_images/%s.png' % picnum)
#         image_path1 = '../test_images/' + str(picnum) + '.png'
#         img = Image.open(image_path1).convert('L')
#         img = img.resize((28, 28),Image.ANTIALIAS)
#         flatten_img = np.reshape(img, (28, 28, 1))
#         x = np.array([1 - flatten_img])
#         # API refer: https://keras.io/models/model/
#         y = self.cnn.model.predict(x)

#         # 因为x只传入了一张图片，取y[0]即可
#         # np.argmax()取得最大值的下标，即代表的数字
#         print(image_path1)
#         print(y[0])
#         print('        -> Predict digit ', np.argmax(y[0]))
#         picnum +=1


def downloadpic(image_url):
    import random
    def get_random_string(length):
        string = ""
        for i in range(0, length):
            code = random.randint(97, 122)
            string += chr(code)
        return string
    filename = get_random_string(20)+'.png'
    relativepath = '/home/ubuntu/flaskdemo/static/'
    filepath = os.path.join(app.root_path,relativepath,filename)
    html = requests.get(image_url)
    with open(filepath,'wb') as file:
        file.write(html.content)
    return str(filepath)

def predictnumber(filepath):
    app = Predict()
    result = app.predict(filepath)
    string = str(result).split('->')
    string[0] = string[0].strip()
    string[1] = string[1].strip()
    string.append(string[1].split(' ')[-1])
    keys = ['array','result','number']
    jsondata = json.dumps(dict(zip(keys,string)))
    return jsondata

@app.route('/')
def hello_world():
   return 'Hello World'

@app.route('/json',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        a = request.get_data()
        dict1 = json.loads(a)
        return json.dumps(dict1["data"])
    else:
        return '<h1>只接受post请求！</h1>'

@app.route('/user/<name>')
def user(name):
    return'<h1>hello, %s</h1>' % name


@app.route('/root_path')
def root():
    filepath = os.path.join(app.root_path,'/workspace/flaskdemo/mnist/v4_cnn/static/','0.png')
    print(filepath)
    return app.root_path

# @app.route('/hello')
# def hello():
#    app1 = Predict()
#    filename = '4.png'
#    filepath = os.path.join(app.root_path,'/workspace/flaskdemo/mnist/v4_cnn/static/',filename)
#    return app1.predict(filepath)
#     # app = Predict()
#     # app.predict('/static/0.png') 
#     # return 'Hello World'

# @app.route('/download')
# def download():
#     return predictnumber(downloadpic('https://i.ibb.co/WggQGff/wx62560d5ec422c283-o6z-AJs1w-HFDKm96-D5l-Jj-Lpm-UDq8w-y-OTa5-Q86-Bcc-Uf8c47562add6796c1a34020671a6ccc8.png'))


@app.route('/predict',methods=['GET','POST'])
def predictnum():
    if request.method == 'POST':
        # if str(request.get_data()) == '{}':
        #     return '0'
        # else:
        #     return '1'

        a = request.get_data()
        image_url = json.loads(a)["data"]["url"]
        return predictnumber(downloadpic(image_url))
    else:
        return '<h1>只接受post请求！</h1>'

if __name__ == '__main__':
   app.run( debug=True)