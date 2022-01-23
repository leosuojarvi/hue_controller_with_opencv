# hue_controller_with_opencv
Control your Philips Hue lights with your hand using webcam and OpenCV

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


Used libraries: cv2, time, numpy, phue
