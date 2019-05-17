
# coding:utf-8

import cv2
from time import time, sleep, strftime, localtime

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)
cap.set(1, 10.0)


fourcc = cv2.VideoWriter_fourcc(*'MJPG')

out = cv2.VideoWriter(strftime("%Y-%m-%d %H:%M:%S", localtime())+'.avi', fourcc, 10, (640,480))

while True:
    ret, frame = cap.read()
    if ret == True:
        frame = cv2.flip(frame, 1)
        out.write(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
        
cap.release()
out.release()
cv2.destroyAllWindows()
