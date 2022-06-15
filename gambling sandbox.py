import os
# Clear the command output
from psychopy import logging, visual, core, event, clock, gui
from datetime  import datetime
import numpy as np
import pandas as pd
import pathlib

win0 = visual.Window(size = (1280,1024),
                     units = "pix",
                     colorSpace = "rgb1",
                     color = (-1,-1,-1),
                     screen = 2,
                     monitor = 'testMonitor',
                     fullscr = True,
                     allowGUI = True
                     )
coin_flip = visual.VlcMovieStim(win = win0,
                                   filename = "data/coin000000.avi",
                                   units = "pix",
                                   pos = (0,0),
                                   autoStart=True)
coin_flip.draw()
win0.flip()
while  not coin_flip.isFinished:
    coin_flip.draw()
    win0.flip()
coin_flip._closeMedia()
