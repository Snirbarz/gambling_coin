import os
# Clear the command output
from psychopy import logging, visual, core, event, clock, gui
from datetime  import datetime
import numpy as np
import pandas as pd
import pathlib
conditionsList = np.repeat("view",12)
print(conditionsList)
conditionsList= [conditionsList,np.repeat("img",12)]
print(np.array(conditionsList).flatten())
