#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Demo of MovieStim
MovieStim opens a video file and displays it on a window.
"""
# create the window object
# import some help
import os
# Clear the command output
from psychopy import logging, visual, core, event, clock, gui, parallel, constants
from datetime  import datetime
import numpy as np
import pandas as pd
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
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
def Value_slider_confidence():
    line_1 = "\n כמה בטוח/ה את/ה בהערכות שלך מ-0 עד 100 \n"
    line_2 = "\n כשאת/ה מסיים/ת לחצ/י SPACE \n"
    text = visual.TextStim(win = win0,text = line_1+line_2,
                           pos=(0,300),color = (1,1,1),
                           units = "pix", height = 32,wrapWidth = 1000,
                           alignText = "center",languageStyle='RTL'
                          )
    VAS = visual.Slider(win =win0,
                        ticks = range(20), # values are from 0 to 20, but they need to be multiplied by 5
                        labels = ["0-ללכב אל", "50-הדימב תינוניב","100-דואמ"],
                        granularity =.1,
                        units = "pix",
                        size = [1000,50],
                        pos = [0,0],font = "Times New Roman",
                        style=('rating'),labelWrapWidth = 30,labelHeight=30)
    VAS.marker.color="red"
    VAS.marker.size =30
    return VAS, text # rate your confidence trial
Value_conf, text_conf = Value_slider_confidence()
continueRoutine = True
while continueRoutine:
    Value_conf.draw()
    text_conf.draw()
    win0.flip()
    keys = event.getKeys()
    if 'space' in keys:
        if Value_conf.getRating() is not None:
            continueRoutine = False