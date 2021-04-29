import cv2 as cv
import time
import numpy as np
import mediapipe as mp 


class DetectordeMaos():
    def __init__(self, mode=False, maxHands=2, detecConf=0.5, trackConf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detecConf = detecConf
        self.trackConf = trackConf

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.detecConf, self.trackConf)
        self.mpDraw = mp.solutions.drawing_utils


    def acharMaos(self, imagem, draw=True):
        imgRGB = cv.cvtColor(imagem, cv.COLOR_BGR2RGB)  # pontos nas mãos
        self.results = self.hands.process(imgRGB)
        #print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:  # detectar as mãos
            for handLms in self.results.multi_hand_landmarks:  # apenas uma mão
                if draw:
                    self.mpDraw.draw_landmarks(imagem, handLms, self.mpHands.HAND_CONNECTIONS)  # plota as conexões 
                
        return imagem        

 
    def acharPosicao(self, imagem, handNo=0, draw=True):

        lmLista = []
        if self.results.multi_hand_landmarks:
            maos = self.results.multi_hand_landmarks[handNo] # mãos
            for id, lm in enumerate(maos.landmark):
                #print(id, lm)
                h, w, c = imagem.shape # para achar as coordenadas dos pontos x e y
                cx, cy = int(lm.x*w), int(lm.y*h)  # circulos nos pontos x e y
                #print(id, cx, cy)
                lmLista.append([id, cx, cy])
                if draw:
                    cv.circle(imagem, (cx, cy), 7, (255, 0, 0), cv.FILLED)
        
        return lmLista
            

    


def main():
    
    wCam, hCam = 640, 480
    pTime = 0
    cTime = 0

    cap = cv.VideoCapture(0)  # abrir webcam
    cap.set(3, wCam)
    cap.set(4, hCam)
    detector = acharMaos()

    while True:
        successo, imagem = cap.read()
        imagem = detector.acharMaos(imagem)
        lmLista = detector.acharPosicao(imagem)
        if len(lmLista) != 0:
            print(lmLista[4])

        cTime = time.time() 
        fps = 1/(cTime - pTime)
        pTime = cTime

        cv.putText(imagem, str(int(fps)), (40, 50), cv.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)  # plotando o fps na tela

    
        cv.imshow('Imagem', imagem)
        cv.waitKey(1)







if __name__ == "__main__":
    main()
