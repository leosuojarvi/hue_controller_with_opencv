# To use this program, you will have to connect your Hue Bridge to phue
# Guide: https://github.com/studioimaginaire/phue

# You will also have to add a credentials.py file containing
# 1. bridgeIP as a string, e.g. bridgeIP = "192.168.1.100"
# 2. cameraNum as an int, normally 0, e.g. cameraNum = 0

# Controls:
# 1. One finger up to control single light, tilting the hand left or right switches the current lamp, hand up and down
# changes the brightness
# 2. All fingers up to control all the lights, hand up and down changes the brightness
# 3. Only thumb up when you are ready, the lamps wont react to movement (helps taking the hand off the camera)
# 4. Fist up and down changes brightness of the one selected lamp (selection in the 1. control)


import cv2
import time
import numpy as np
from phue import Bridge

import htmModule as htm
from info import bridgeIP, cameraNum

b = Bridge(bridgeIP)

lights = b.get_light_objects()

wCam, hCam = 640, 480
cap = cv2.VideoCapture(cameraNum)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector()

lastSend = 0
lastCheck = 0
lastMove = 0

lightIDs = list(map(lambda x: x.light_id, lights))
curIndex = 0
curAll = False

lastBri = -1
lastHue = -1
brightness = 100


def sendBri(bri):
    global lastBri
    if brightness != lastBri:
        if brightness != 0:
            command = {'transitiontime': 3, 'on': True, 'bri': brightness}
        else:
            command = {'on': False}
        send(command)
        lastBri = brightness


def sendHue(hue):
    global lastHue
    if hue != lastHue:
        command = {'on': True, 'hue': hue}
        send(command)
        lastHue = hue


def send(command):
    global lastSend
    global curIndex

    if time.time() - lastSend > 0.05:
        if curAll:
            for lightID in lightIDs:
                b.set_light(lightID, command)
        else:
            b.set_light(lightIDs[curIndex], command)

        lastSend = time.time()


def moveAndFlash(toLeft):
    global curIndex
    global lastMove

    if time.time() - lastMove > 1:
        command = {'alert': "none"}
        b.set_light(lightIDs[curIndex], command)

        if toLeft:
            curIndex = (curIndex - 1) % len(lightIDs)
        else:
            curIndex = (curIndex + 1) % len(lightIDs)
        command = {'alert': "select"}
        b.set_light(lightIDs[curIndex], command)

        lastMove = time.time()

        print(curIndex)


while True:
    # updateBris()
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        fingers = detector.fingersUp()

        # If the hand is open -> control all of the lights
        curAll = fingers.count(1) == 5

        # Just thumb -> no action
        if not (fingers[0] == 1 and fingers.count(1) == 1):
            # Tilting the hand -> choose light
            # TODO: tweak parameters
            if lmList[5][3] - lmList[17][3] < -800:
                moveAndFlash(True)
            elif lmList[5][3] - lmList[17][3] > 1000:
                moveAndFlash(False)

            # Brightness
            elif fingers.count(1) > 0:
                distance = max(detector.findDistance(0, 5, img)[0], detector.findDistance(5, 17, img)[0] * 220 / 145)
                print(distance)
                brightness = 254 - int(np.interp(distance, [10000, 19000], [0, 254]))
                sendBri(brightness)

            # Color
            elif fingers.count(1) == 0:
                distance = max(detector.findDistance(0, 5, img)[0], detector.findDistance(5, 17, img)[0] * 220 / 145)
                hue = int(np.interp(distance, [9000, 23000], [0, 65535]))
                sendHue(hue)

    cv2.imshow("Img", img)
    cv2.waitKey(10)
