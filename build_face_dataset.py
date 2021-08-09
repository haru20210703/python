from imutils.video import VideoStream
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
ap.add_argument("-o", "--output", default="face",
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
time.sleep(2.0)
total = 0

class BuildCamera(object):
    def __init__(self):
        #self.video = cv2.VideoCapture('http://192.168.12.152:8083')
        self.video = cv2.VideoCapture(0)

        # Opencvのカメラをセットします。(0)はノートパソコンならば組み込まれているカメラ

    def __del__(self):
        self.video.release()

    def get_frame(self):
        global total
        success, frame = self.video.read()
        frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_rects=face_cascade.detectMultiScale(gray,1.3,5)
        
        # loop over the face detections and draw them on the frame
        for (x, y, w, h) in face_rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        #cv2.imshow("Frame", frame)
        #key = cv2.waitKey(1) & 0xFF

        # if the `k` key was pressed, write the *original* frame to disk
        #if key == ord("k"):
            if total == 30:
                break
            p = os.path.sep.join([args["output"], "{}.jpg".format(
                str(total).zfill(5))])
            cv2.imwrite(p, frame)
            print(p)
            total += 1
            if total == 30:
                print('顔の撮影が完了しました。ホーム画面に戻って下さい。')
                total = 0
                sys.exit()
                #total = 0
                #time.sleep(5)
                break

        # if the `q` key was pressed, break from the loop
        #elif key == ord("q"):
           # break

        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes(), list()
                    
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
