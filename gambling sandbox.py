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
                     color = (.6,.6,.6),
                     screen = 2,
                     monitor = 'testMonitor',
                     fullscr = True,
                     allowGUI = True
                     )

text_mu = visual.TextStim(win0,text="חצי" +"\n\n 1",
                             pos=(200,0),color = (-1,-1,-1),
                             units = "pix", height = 32,wrapWidth=1500,
                             alignText = "center",languageStyle="RTL")
# image_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]])
text_coin = visual.TextStim(win0,text="מטבע",
                             pos=(-200,0),color = (-1,-1,-1),
                             units = "pix", height = 32,wrapWidth=1500,
                             alignText = "center",languageStyle="RTL")
text_coin.draw()
text_mu.draw()
win0.flip()
core.wait(3)
win0.flip()
