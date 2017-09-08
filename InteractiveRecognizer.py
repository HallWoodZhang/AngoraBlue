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

        if os.path.isfile(recognizerPath):
            self._recognizer.load(recognizerPath)
            self._recognizerTrained = True
        else:
            self._recognizerTrained = False

        self._detector = cv2.CascadeClassifier(cascadePath)
        self._scaleFactor = scaleFactor
        self._minNeighbors = minNeighbors

        minImageSize = min(self._imageHeight, self._imageWidth)
        self._minSize = (int(minImageSize * minSizeProportional[0]), int(minImageSize * minSizeProportional[1]))
        self._flags = flags
        self._rectColor = rectColor

        # gui events
        style = wx.CLOSE_BOX | wx.MINIMIZE_BOX | wx.CAPTION | wx.SYSTEM_MENU | wx.CLIP_CHILDREN
        wx.Frame.__init__(self, None, title = title, style = style, size = size)
        self.SetBackgroundColour(wx.Colour(232, 232, 232))

        self.Bind(wx.EVT_CLOSE, self._onCloseWindow)

        quitCommandID = wx.NewId()
        self.Bind(wx.EVT_MENU, self._onQuitCommand, id = quitCommandID)
        acceleratorTable = wx.AcceleratorTable ([
            (wx.ACCEL_NORMAL, wx.WXK_ESCAPE, quitCommandID)
        ])

        self.SetAcceleratorTable(acceleratorTable)

        # init gui tools
        self._staticBitmap = wx.StaticBitmap(self, size = size)
        self._showImag(None)

        self._referenceTextCtrl = wx.TextCtrl(self, style = wx.TE_PROCESS_ENTER)
        self._referenceTextCtrl.SetMaxLength(4)
        self._referenceTextCtrl.Bind(wx.EVT_KEY_UP, self._onReferenceTextCtrlKeyUp)

        self._predictionStaticText = wx.StaticText(self)

            # insert an endline for consistent spacing
        self._predictionStaticText.SetLabel('\n')

        self._updateModelButton = wx.Button(self, label = 'Add to Model')
        self._updateModelButton.Bind(wx.EVT_BUTTON, self._updateModel)

        self._updateModelButton.Disable()

        self._clearModelButton = wx.Button(self, label = 'Clear Model')
        self._clearModelButton.Bind(wx.EVT_BUTTON, self._clearModel)

        if not self._recognizerTrained:
            self._clearModelButton.Disable()

        # gui layout setting
        border = 12
        controlsSizer = wx.BoxSizer(wx.HORIZONTAL)
        controlsSizer.Add(self._referenceTextCtrl, 0, wx.ALIGN_CENTER_VERTICAL)
        controlsSizer.Add(self._updateModelButton, 0,
            wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border
        )
        controlsSizer.Add(self._predictionStaticText, 0, wx.ALIGN_CENTER_VERTICAL)
        controlsSizer.Add((0, 0), 1) # spacer
        controlsSizer.Add(self._clearModelButton, 0, wx.ALIGN_CENTER_VERTICAL)

        rootSizer = wx.BoxSizer(wx.VERTICAL)
        rootSizer.Add(self._staticBitmap)
        rootSizer.Add(controlsSizer, 0,
            wx.EXPAND | wx.ALL, border
        )

        self.SetSizerAndFit(rootSizer)

        # capture the thread
        self._captrueThread = threading.Thread(
            target = self._runCaptureLoop
        )

        self._captrueThread.start()

        # end __init__
        
