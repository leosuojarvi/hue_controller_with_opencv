# Credit for the idea and some parts of the module - Murtaza's Workshop Youtube channel

import math
import cv2
import mediapipe as mp
import time
import numpy as np


class handDetector():
    def __init__(self, mode=False, maxHands=2, complexity=1, detectionCon=0.6, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.complexity,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy, cz = int(lm.x * w*100), int(lm.y * h*100), int(lm.z*10000)
                self.lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return self.lmList

    def fingersUp(self):
        fingers = []

        x0, y0 = self.lmList[0][1], self.lmList[0][2]
        x1, y1 = self.lmList[1][1], self.lmList[1][2]
        x2, y2 = self.lmList[2][1], self.lmList[2][2]
        x3, y3 = self.lmList[3][1], self.lmList[3][2]
        x4, y4 = self.lmList[4][1], self.lmList[4][2]

        # Check is thumb is in a almost straight line (up) or curved (down)
        if math.hypot(x4 - x0, y4 - y0) > 0.9 * (
                math.hypot(x4 - x3, y4 - y3) + math.hypot(x3 - x2, y3 - y2) + math.hypot(x2 - x1, y2 - y1) + math.hypot(
                x1 - x0, y1 - y0)):
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers
        for id in range(1, 5):
            x0, y0 = self.lmList[0][1], self.lmList[0][2]
            x1, y1 = self.lmList[self.tipIds[id] - 2][1], self.lmList[self.tipIds[id] - 2][2]
            x2, y2 = self.lmList[self.tipIds[id]][1], self.lmList[self.tipIds[id]][2]

            if math.hypot(x2 - x0, y2 - y0) > math.hypot(x1 - x0, y1 - y0):
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers

    # Positive if palm is down, false if palm is up
    def handAngle(self, mirrored = True):
        handedness = self.results.multi_handedness[0].classification[0].label
        if mirrored:
            handedness = "Right" if handedness == "Left" else "Left"
        mainAngle = math.atan2(self.lmList[17][2]-self.lmList[0][2], self.lmList[17][1]-self.lmList[0][1])
        thumbAngle = math.atan2(self.lmList[1][2] - self.lmList[0][2], self.lmList[1][1] - self.lmList[0][1])
        angle = mainAngle - thumbAngle
        if handedness == "Right":
            angle = -1*angle
        angle = angle + 2 * math.pi if angle <= -math.pi else angle
        angle = angle - 2 * math.pi if angle >= math.pi else angle

        return angle




    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]  # Thumb
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]  # Index
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        length = math.hypot(x2 - x1, y2 - y1)

        if draw:
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 0), 3)

        return length, img, [x1, y1, x2, y2, cx, cy]
