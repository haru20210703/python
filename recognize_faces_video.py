from imutils.video import VideoStream
from pyzbar import pyzbar
#from flask import Flask, flash, redirect, render_template, request, url_for
import face_recognition
import argparse
import imutils
import pickle
import datetime
import MySQLdb
import time
import cv2
import sys
import os

face_cascade=cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml")
ds_factor=0.6
datasets = 'datasets'

#データベース接続情報
connection = MySQLdb.connect(
    host='localhost',
    user='ubuntu',
    passwd='ubuntu',
    db='python',
    # テーブル内部で日本語を扱うために追加
    charset='utf8'
)
cursor = connection.cursor()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
#ap.add_argument("-e", "--encodings", required=True, default="encodings.pickle",
ap.add_argument("-e", "--encodings", default="encodings.pickle",
	help="path to serialized db of facial encodings")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
ap.add_argument("-y", "--display", type=int, default=1,
	help="whether or not to display output frame to screen")
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())


# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())
# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start()
#vs = VideoStream('http://192.168.12.152:8083').start()
writer = None
#time.sleep(2.0)

class VideoCamera(object):

    old_name = ''
    in_name = ''

    f_count = 0
    un_count = 0

    def __init__(self):
        #self.video = cv2.VideoCapture('http://192.168.12.150:8081')
        self.video = cv2.VideoCapture(0)

        # Opencvのカメラをセットします。(0)はノートパソコンならば組み込まれているカメラ

    def __del__(self):
        self.video.release()
        
    def write_name(self, name, kinmu):
        with open('static/facedata.html', 'r')as f:
            text = f.readlines()

            text.insert(0, name + 'さんの' + kinmu + 'を確認しました\n')
            text = text[:-1]

        with open('static/facedata.html', 'w')as f:
            f.writelines(text)

            print(datetime.datetime.now())
            print('')

    def insert_name(self, name):
        if self.old_name == name:
            self.f_count += 1
        elif self.old_name != name:
            self.f_count = 0

        if self.f_count == 3 and name != "Unknown":
            if self.in_name != name:

                if type(name) is int:
                    sql = "select name_id, name, status from name where code = " + str(name)
                else:
                    sql = "select name_id, name, status from name where face = '" + str(name) + "'"

                cursor.execute(sql)

                row = cursor.fetchall()

                name_id = row[0][0]
                write_name = row[0][1]
                status = row[0][2]
                if status == 0:
                    status = 1
                    kinmu = '出勤'
                else:
                    status = 0
                    kinmu = '退勤'

                #データベース制御
                # データの追加
                sql = ('''
                insert into test (name, time, name_id, status)
                values (%s, %s, %s, %s)
                ''')
                param = (name, datetime.datetime.now(), name_id, status)
                cursor.execute(sql, param)
                # 保存を実行
                connection.commit()

                sql = ('''
                update name
                set status = %s
                where name_id = %s
                ''')
                param = (status, name_id)
                cursor.execute(sql, param)
                connection.commit()

                self.f_count = 0
                self.un_count = 0
                self.in_name = name
                print(write_name + 'さんの' + kinmu + 'を確認しました')
                #f = open('static/facedata.html', 'a', encoding='UTF-8')
                #f.write(name  + 'さんを確認しました\n')
                #f.close()

                self.write_name(write_name, kinmu)

                #flash(name + 'さんを確認しました')
                #time.sleep(3)
        # update the list of names
        if name == "Unknown":
            self.un_count += 1
        if self.un_count == 3 and self.in_name != name:
            print('顔が未登録です　登録画面に移動してください')
            #f = open('static/facedata.html', 'a', encoding='UTF-8')
            #f.write('顔が未登録です　登録画面に移動してください\n')
            #f.close()
            self.write_name(name)

            self.un_count = 0
            self.f_count = 0
            self.in_name = name

        self.old_name = name

    def get_barcode(self, barcode, frame):
        font = cv2.FONT_HERSHEY_SIMPLEX
        x,y,w,h = barcode.rect
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
        barcodeData = barcode.data.decode('utf-8')
        frame = cv2.putText(frame,barcodeData,(x,y-10),font,.5,(0,0,255),2,cv2.LINE_AA)

        self.insert_name(int(barcodeData))

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


    def get_frame(self):

        success, frame = self.video.read()

        #バーコード認証
        d = pyzbar.decode(frame)
        if d:
            for barcode in d:
                self.get_barcode(barcode, frame)

        #顔認証

        frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_rects=face_cascade.detectMultiScale(gray,1.3,5)

        for (x,y,w,h) in face_rects:
        #cap.release()
            #顔を認識したら四角枠で囲う
            #cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

            # loop over frames from the video file stream
            #while True:
            # grab the frame from the threaded video stream
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)

            #リサイズ　処理時間がかかるのでコメントアウト
            #rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #rgb = imutils.resize(frame, width=750)
            r = frame.shape[1] / float(gray.shape[1])

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            
            #カメラ映像から顔を検出する
            boxes = face_recognition.face_locations(gray)
                    #model=args["detection_method"], number_of_times_to_upsample=2)

            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []
            
            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                #取得した顔と検出器で誰かを判定する
                #toleranceはしきい値で、数字が低くなると厳しくなる　デフォルトは0.6
                matches = face_recognition.compare_faces(data["encodings"],
                        encoding, tolerance=0.4)
                name = "Unknown"
                
                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    
                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                        # determine the recognized face with the largest number
                        # of votes (note: in the event of an unlikely tie Python
                        # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)

                    self.insert_name(name)
                names.append(name)
                        
            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):

                # rescale the face coordinates
                top = int(top * r)
                right = int(right * r)
                bottom = int(bottom * r)
                left = int(left * r)

                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),
                        (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name + " OK", (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)
                #ret, jpeg = cv2.imencode('.jpg', frame)
                #return jpeg.tobytes()
                #time.sleep(2)
                break

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()#, list(name)
                    
                    #ディスプレイ付きのＰＣの場合は以下のコメントアウトを外す
                    ## if the video writer is None *AND* we are supposed to write
                    ## the output video to disk initialize the writer
                    #if writer is None and args["output"] is not None:
                    #fourcc = cv2.VideoWriter_fourcc(*"MJPG")
                    #writer = cv2.VideoWriter(args["output"], fourcc, 20,
                            #(frame.shape[1], frame.shape[0]), True)
                    ## if the writer is not None, write the frame with recognized
                    ## faces to disk
                    #if writer is not None:
                        #writer.write(frame)
                    #check to see if we are supposed to display the output frame to
                    # the screen
                    #if args["display"] > 0:
                        #cv2.imshow("Frame", frame)
                        #key = cv2.waitKey(1) & 0xFF
                        # if the `q` key was pressed, break from the loop
                    #if key == ord("q"):
                        #break
                    # do a bit of cleanup
                #ret, jpeg = cv2.imencode('.jpg', image)
                #return jpeg.tobytes()
    #cv2.destroyAllWindows()
    #vs.stop()
    # check to see if the video writer point needs to be released
    #if writer is not None:
    #    writer.release()
