import pyglet
from pyglet import clock
from pyglet.window import key
from pyglet.gl import *
import os
import math
import numpy as np
from PIL import Image
import io
pyglet.options['debug_gl'] = False


conditionsList = ["img","view"]
trialList = []
trialList.append(np.random.permutation(conditionsList)[0:2])
for i in range(5):
    trialList.append(np.random.permutation(conditionsList)[0:2])
trialList = np.array(trialList).flatten()
outcome_view = np.array([0,0,0,1,1,1])
outcome_view = np.random.permutation(outcome_view)
outcome_img = np.array([0,0,0,1,1,1])
outcome_img = np.random.permutation(outcome_img)
ind_view = np.where(trialList == "view")
ind_img = np.where(trialList == "img")
print(outcome_view)
print(ind_view)
print(outcome_img)
print(ind_img)
outcome = np.array([0,0,0,0,0,0,0,0,0,0,0,0])
outcome[ind_view] = outcome_view
outcome[ind_img] = outcome_img
print(outcome)
