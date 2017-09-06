import numpy
import cv2
import binascii

# The translator trans 4 char str to int

def fourCharToInt(s):
    return int(binascii.hexlify(str), 16)

def intToFourChar(i):
    return binascii.unhexlify(format(i, 'x'))

