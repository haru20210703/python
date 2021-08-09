#from flask import Flask, render_template, Response, url_for, redirect
from flask import Flask, flash, redirect, render_template, Response, request, url_for, stream_with_context
from flask import render_template, redirect
from time import sleep

from recognize_faces_video import VideoCamera
from build_face_dataset import BuildCamera

import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    #names = name(VideoCamera)
    #names = names
    #return render_template('index.html', names=names)
    #return Response(stream_with_context(stream_template('index.html', names=names)))
    return render_template('index.html')
    
    # "/" を呼び出したときには、indexが表示される。

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv

def gen(recognize_faces_video):
    while True:
        #result = recognize_faces_video.get_frame()
        frame = recognize_faces_video.get_frame()
        #frame = result[0]
        #if name:
            #return redirect(url_for('name'))
        #else:
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        
        #yield name

#def name(recognize_faces_video):
#    while True:
#        result = recognize_faces_video.get_frame()
#        name = result[1]
#        name = ''.join(name)
#        yield name

# returnではなくジェネレーターのyieldで逐次出力。
# Generatorとして働くためにgenとの関数名にしている
# Content-Type（送り返すファイルの種類として）multipart/x-mixed-replace を利用。
# HTTP応答によりサーバーが任意のタイミングで複数の文書を返し、紙芝居的にレンダリングを切り替えさせるもの。
#（※以下に解説参照あり）

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/touroku')
def touroku():
    return render_template('touroku.html')

#@app.route('/name')
#def name():
#    return render_template('name.html')

@app.route('/build')

def build():
    return render_template('build.html')

@app.route('/facedata')
def facedata():
    return render_template('facedata.html')

@app.route('/video_build')
def video_build():
    return Response(gen(BuildCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/finish')
def finish():
    return render_template('finish.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# 0.0.0.0はすべてのアクセスを受け付けます。    
# webブラウザーには、「localhost:5000」と入力
