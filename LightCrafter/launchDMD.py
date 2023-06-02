# -*- coding: utf-8 -*-
"""
Created on Fri Apr 30 11:03:27 2021

@author: Microscope
"""

import socket
from Lightcrafter import Lightcrafter
import numpy as np
import time

TCP_IP = '192.168.7.2'
TCP_PORT = 0x5555

with open(r'C:\Users\Microscope\Desktop\DMD\mask_C.bmp','rb') as opened:
    tosend=np.fromfile(opened,np.uint8).flatten()
    
L=Lightcrafter(TCP_IP,TCP_PORT) 
L.connect()

L.setBMPImage(tosend)    

time.sleep(1)

L.disconnect()
