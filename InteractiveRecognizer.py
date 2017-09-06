import numpy
import cv2
import os
import sys
import threading
import wx

import BinasciiUtils
import ResizeUtils
import WxUtils

class InteractiveRecognizer(wx.Frame):

    def __init__(self, recognizerPath, cascadePath,
                 scaleFactor = 1.3, minNeighbors = 4,
                 minSizeProportional = (0.25, 0.25),
                 flags = cv2.CASCADE_SCALE_IMAGE,
                 rectColor = (0, 255, 0),
                 cameraDeviceID = 0, imageSize = (1280, 720),
                 title = 'Interactive Recognizer'):
        '''
        doc:
        :param recognizerPath:          the path of Recognition model
        :param cascadePath:             the path of detection model
        :param scaleFactor:             the scale of image that the recognizer checking for
        :param minNeighbors:            the min num of Partial images that pass the face-checker
        :param minSizeProportional:     def the min propotion of the height and width from the face-image
        :param flags:                   some tech to accelerate the process
        :param rectColor:               the color of image matrix
        :param cameraDeviceID:          the ID of the camara
        :param imageSize:               the prefered(default) size of the image
        :param title:                   the tittle of the executable program
        '''

        # if the image we get from the camera is mirrored
        self.mirrored = True

        # if the exe proc is running
        self._running = True

        self._captrue = cv2.VideoCapture(cameraDeviceID)

        # size = tuple(width, height)
        size = ResizeUtils.cvResizeCapture(self._captrue, imageSize)

        self._imageWidth, self._imageHeight = size

        # the var about the recognizer
        self._currDetectedObject = None
        self._recognizerPath = recognizerPath
        self._recognizer = cv2.face.createLBPHFaceRecognizer()