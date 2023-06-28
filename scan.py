import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mysql.connector

db = mysql.connector.connect(host='localhost', user='root', password='teste', database='lanali')
cursor = db.cursor(dictionary=True) 

def scaner():
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)
    while True:
        success, img = cap.read()
        cv2.imshow('Result',img)    
        cv2.waitKey(1)
        for barcode in decode(img):
            myData = barcode.data.decode('utf-8')
            pts = np.array([barcode.polygon], np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(img,[pts], True,(255,0,255),5)
            pts2 = barcode.rect
            cv2.putText(img,myData,(pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9,(255,0,255),2)

            cv2.imshow('Result',img)    
            cv2.waitKey(1) 

            if myData != '':
                cursor.execute('''SELECT codEnsaio, descricao, idItemEnsaio FROM mvt_item_ensaio 
                            INNER JOIN cad_ensaio USING(idensaio)
                            WHERE idsolicitacao = {}
                            ORDER BY codensaio'''.format(myData))
                resultado = cursor.fetchall()
                cv2.destroyAllWindows()
                return resultado


