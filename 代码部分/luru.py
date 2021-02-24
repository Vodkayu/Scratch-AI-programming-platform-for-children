import time
import cv2

def renlianluru(frame):
    frame_c = frame.copy()
    gray = cv2.cvtColor(frame_c, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier('opencv-files/lbpcascade_frontalface.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    renlian_flag = 0
    try:
        (x, y, w, h) = faces[0]
        cv2.rectangle(frame_c, (x, y), (x + w, y + h), (0, 255, 0), 2)
        renlian_flag = 1
    except:
        pass
    cv2.imshow('luru', frame_c)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        if renlian_flag:
            cv2.imwrite('./renlian/'+str(int(time.time()*100))+'.png', frame)