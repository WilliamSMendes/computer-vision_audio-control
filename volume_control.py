import cv2 as cv
import time
import numpy as np
import hand_track_module as htm  # o arquivo precisa estar na mesma pasta para funcionar
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # biblioteca que controla o som do sistema


wCam, hCam = 640, 480

cap = cv.VideoCapture(0)   # abrir camera
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

if not cap.isOpened():
    print('Não foi possível abrir a câmera')
    exit()

detector = htm.DetectordeMaos(detecConf=0.7)

devices = AudioUtilities.GetSpeakers()    # pycaw
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0

while True:
    successo, imagem = cap.read()
    imagem = detector.acharMaos(imagem)
    lmLista = detector.acharPosicao(imagem, draw=False)
    if len(lmLista) != 0:
        print(lmLista[4], lmLista[8])   # os pontos 4 e 8 sao dedão e dedo indicador de acorco com a documentação do mediapipe

        x1, y1 = lmLista[4][1], lmLista[4][2]  # coordenadas do dedão
        x2, y2 = lmLista[8][1], lmLista[8][2]  # coordenadas do indicador
        cx, cy = (x1+x2)//2, (y1+y2)//2      # centro da linha

        cv.circle(imagem, (x1, y1), 7, (255, 0, 0), cv.FILLED)
        cv.circle(imagem, (x2, y2), 7, (255, 0, 0), cv.FILLED)
        cv.line(imagem, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv.circle(imagem, (cx, cy), 7, (255, 0, 0), cv.FILLED)

        compr = math.hypot(x2-x1, y2-y1)   # comprimento da barra de som
        print(compr)

        # valores das mãos variam de 50 ate 300 (min e max)
        # valores do volume variam de -65.25 ate 0 (min e max)

        vol = np.interp(compr, [50, 300], [minVol, maxVol])
        volBar = np.interp(compr, [50, 300], [400, 150])  # barra de volume
        volPer = np.interp(compr, [50, 300], [0, 100])  # porcentagem do volume na barra
        print(int(compr), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if compr < 50:    # se o volume chegar no valor mínimo:
            cv.circle(imagem, (cx, cy), 7, (255, 0, 255), cv.FILLED)

    cv.rectangle(imagem, (50, 150), (60, 400), (0, 255, 0), 3)
    cv.rectangle(imagem, (50, int(volBar)), (60, 400), (0, 255, 0), cv.FILLED)
    cv.putText(imagem, f"{int(volPer)} %", (40, 450), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    cTime = time.time() 
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv.putText(imagem, f"FPS: {int(fps)}", (40, 50), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

    if not successo:
        print('Não está funcionando')
        break

    cv.imshow('Imagem', imagem)
    cv.waitKey(1)
