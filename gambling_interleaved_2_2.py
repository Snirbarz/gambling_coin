'''
Stimuli: all presented at 80cm away from the screen
    fixation: black cross 10.1 d VA
              thickness will be 0.1 degress VA =
              500-1000ms (core.wait(1000),time.sleep(1))
    instructions:
              participants recieve 20 shekels in the begining of the Experiment
              they are told that they are going to participate in a gambling task
              where they will choose to gamble or not to gamble on a result of a coin.
              They can receive half of a sure option. or bet on the coin. If they choose to gamble,
              The coin will be tossed and the amount generated on it will be lost.
    Stimulus: 10 images from the exposure task
              clustered into 5 pairs, each representing a single double sided coin
              for each coin participant view and imagine an outcome in different trials
=======


              images appears for uninterrupted time until participants press space
              image at the center of the screen (size unknown)
              black backgroud (rgb --> -1,-1,-1)
              elvers.us/perception/visualAngleVA = figure out how to convert to cm and then pixels
              36 VA = (30.5425 cm) 1112 == 0


    Mask:     no mask


    Response: keyboard --> 'space' for moving on to the next trial
                           'd' is for choosing to gamble
                           'k' for choosing to receive the sure loss
    Task:
            training (1 coin)  ==> 12 trials total
            block 1 (2 coins)  ==> 12 Imagination trials and 12 viewing trials per coin
            block 2 (2 coins)  ==> 12 Imagination trials and 12 viewing trials per coin
    Trial:
            show coin sides and whether it's an imagination or observation trial
            fixation start (500ms) # Snir 
            imagination/viewing trial
            rate mean (0-20; no time limit)
            confidence rating  (0-100 VAS; no time limit)
            choose range (0-20; no time limit)
            confidence rating (0-100 VAS; no time limit)
            gamble (show coin sides and choose to to either gamble or accept a specific loss; no time limit)
    Triggers:
    Monitor specification
            Screen Width = 37.632cm
            Screen Height = 30.106cm
            # Pixels wide = 1280 X 1024
            pixel_density_x (num_pixels per cm) = 1280/37.632 =34.02
    ParallelPort = 0x3EFC

            2- match fixation 00000001
            3- view trial 00000010
            4- img trial 00000100
            5- video 00001000
            6- outcome learning 00010000
            7- responsegamble 00100000
            8- responsenotgamble 01000000
            9- starttask 10000000
            10- instructions learning
            11- instructions gambling use imagery
            12- instructions gambling do not use imagery
            13- training trials all trials are relevant
            14- instructions gambling general
            15- rate mu
            16- rate range
            17- rate confidence
'''
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

# set parallel port address
parallel.setPortAddress()

# reset bits
parallel.setData(0) 

# obtain the current date
date_val = datetime.now().strftime("%Y-%m-%d") 

# create a dialog box to collect subject information
my_Dlg = gui.Dlg(title = "gambling task")
my_Dlg.addText("Subject info")
my_Dlg.addField("Exp Date",date_val)
my_Dlg.addField("ID","")

# show the dialog box and collect the user's ID
show_dlg = my_Dlg.show()

# if the user clicks OK, create a save file name using the current date and the user's ID
if my_Dlg.OK:
    print(show_dlg)
    save_file_name = show_dlg[0]+"_"+show_dlg[1]+'_gambling_task.csv'
    print(save_file_name)
# if the user clicks Cancel, print a message
else:
    print("user cancelled")

# print the experiment setup information
print("Experiment setup information")
print(show_dlg)

# create a save path for the data file
save_path = gui.fileSaveDlg(initFileName=save_file_name,
                            prompt = 'select Save File',
                            )

# print the output from the save dialog
print("Output from save dialog")
print(save_path)

# print that the setup is finished
print("setup finished")

# obtain the current time
cur_time = datetime.now().strftime('%H%M%S') 

# create variables
no_trials = 5 # number of total trials (equal to number of unique coins)
Mu = np.array([-10,-10,-10,-10,-10]) # the mean of the coin which is the same for both imagination and view trials.
SD = np.array(["MM","LH","HL","LH","HL"]) # The distribution width of the imagined and real outcomes the first letter is for the imagination trials.
coin_array = np.array(range(1,no_trials))# number of coins in test trials (4)
coin_sides = np.array([0,1,2,3,4,5,6,7])
coin_sides_training = np.array([8,9])
coin_sides = np.random.permutation(coin_sides)
coin_sides = np.append(coin_sides_training,coin_sides)
print("coin_sides",coin_sides)
coin_side_1 = np.array(coin_sides[[0,2,3,4,5]]) # side 1 index of the coin
print("coin_sides1",coin_side_1)
coin_side_2 = np.array(coin_sides[[1,6,7,8,9]]) # side 2 index of the coin
#  swaps the values of the sides of the coin if the side 1 of the coin is greater than the side 2 of the coin.
for i in range(no_trials):
    if coin_side_1[i] > coin_side_2[i]:
        tmp_side_1 = coin_side_1[i]
        coin_side_1[i] = coin_side_2[i]
        coin_side_2[i] = tmp_side_1

coin_heads = np.array([0,0,0,1,1]) # coin heads (1) or tails (0)
np.random.permutation(coin_heads) # permute which side is heads or tails

cur_time_array = []
trial_no = [] # current coin number (0-4)
sub_id_array = [] # subject id
date_value_array=[] # current date
sub_response_array=[] # subject reponse "Gamble or loss" also space for learning trials.
response_latency=[] # suject response latency
time_value_array =[] # time in HH:MM:SS
block_array=[] # is it a training or a test block
final_coin_side_1_array = [] #which side is it currently (index of image)
final_coin_side_2_array = [] #which side is it currently (index of image)
final_fix_time_array = [] # fixation time
final_Mu_array = [] # current Mu value
final_SD_array = [] # coin distribution ("HH","HL","LL" or "LH")
final_head_array = [] # which side is head (0 or 1)
final_task_array = [] # current task
final_task_comb_array = [] # is it an imagination or view trial
final_gamble_array = [] # did the participant decide to gamble or not ("yes" or "no")
final_outcome_array = [] # what is the outcome heads or tails (0 or 1)
final_loss_array = [] # how much points the participant lost in this learning or gambling trial?
final_estimation_mu = [] # participant estimation of mu
final_estimation_rangelow = [] # participant estimation of the low range
final_estimation_range_high = [] # participant estimation of the high range
final_estimation_confidence_mu = [] # participant confidence on mu estimation
final_estimation_confidence_range = [] # participant confidence on range estimation
final_use_imagery = [] # participant is instructed to use imagery or not (1 or 0)
final_sure_option = [] #what was the sure option presented to participants

# Subject ID:
sub_id = show_dlg[1]
# Order the 4 training coins and 24 test coins
stim_coin = []

new_coin_array = np.random.permutation(coin_array) # the coin sides themselves are completely random
new_coin_array = np.append(np.array(0),new_coin_array)
stim_generate = new_coin_array # decide which combination of mu and SD is selected for the current trial.
for n in range(no_trials):
    stim_coin.append(new_coin_array[n])
    
    cur_time_array.append(datetime.now().strftime('%H%M%S'))
stim_coin = np.array(stim_coin).flatten()
print("stim_coin",stim_coin)
stim_generate = np.array(stim_generate).flatten()
print("stim_generate",stim_generate)
cur_time_array = np.array(cur_time_array).flatten()

# create gamble array
logging.console.setLevel(logging.WARNING) # log warning messages
print("*************************************")
print("PSYCHOPY LOGGING set to : WARNING")
print(datetime.now())
print("Gambling TASK: version beta")
print("*************************************")

# create the window object
win0 = visual.Window(size = (1280,1024),
                     units = "pix",
                     colorSpace = "rgb1",
                     color = (-1,-1,-1),
                     screen = 2,
                     monitor = 'testMonitor',
                     fullscr = True,
                     allowGUI = True
                     )

# For some reason the experiment works better if we play a video in the beginning thus we display the empty coin.
flip = visual.VlcMovieStim(win = win0,
                filename = "data/coin000000.avi",
                units = "pix",
                pos = (0,0),
                autoStart=True)
flip.draw()
win0.flip()
while  not flip.isFinished:
     flip.draw()
     win0.flip()
flip._closeMedia()
# create our fixation cross
def save_results(save_file_name):
    # create a data frame:
    output_file = pd.DataFrame({'trial':trial_no,
                                'time': time_value_array,
                                'id':sub_id_array,
                                'Date':date_value_array,
                                'fix_time':final_fix_time_array,
                                'response':sub_response_array,
                                'side_1_stim':final_coin_side_1_array,
                                'side_2_stim':final_coin_side_2_array,
                                'latency':response_latency,
                                'Block':block_array,
                                'Mu':final_Mu_array,
                                'SD':final_SD_array,
                                'head':final_head_array,
                                'outcome':final_outcome_array,
                                'task':final_task_array,
                                'gamble_trial':final_gamble_array,
                                'loss':final_loss_array,
                                'est_mu':final_estimation_mu,
                                'est_low':final_estimation_rangelow,
                                'est_high':final_estimation_range_high,
                                'conf_mu':final_estimation_confidence_mu,
                                'conf_range':final_estimation_confidence_range,
                                'current_task':final_task_comb_array,
                                'use_imagery':final_use_imagery,
                                'sure_option':final_sure_option})
    # save the file
    output_file.to_csv(save_file_name,sep = ",",index=False)



def fixation_cross():
    '''
    We will create our fixation_cross
    '''
    fix_cross_horiz = visual.Rect(win = win0,
                                       width = 12,
                                       units = "pix",
                                       height = 1,
                                       lineColor = [1,1,1],
                                       fillColor = [1,1,1],
                                       pos = (0,0))
    fix_cross_vert = visual.Rect(win = win0,
                                       width = 1,
                                       units = "pix",
                                       height = 12,
                                       lineColor = [1,1,1],
                                       fillColor = [1,1,1],
                                       pos = (0,0))

    fix_cross_horiz.draw() # this will draw the horizontal bit onto the window
    fix_cross_vert.draw() # this will draw the vertical bit onto the window
# create our coin stim which displays two sides of the coin to the participant before the trial starts.
def image_stim(image_type_1,image_type_2,stage):
    '''
    We are preparing our Stimulus
    image_type == 0, Stim01.png "frog"
    image_type == 1, Stim02.png "face"
    image_type == 2, Stim03.png "sign"
    image_type == 3, Stim04.png "tomato"
    image_type == 4, Stim05.png "hand"
    image_type == 5, Stim06.png "pond"
    image_type == 6, Stim07.png "wrench"
    image_type == 7, Stim08.png "house"
    '''
    image_stim_name = ["01","02","03","04","05","06","07","08","09","10"]
    if stage == "learning":
        position_left = (-270,0)
        position_right = (270,0)
        image_right_size= (400,400)
        image_left_size= (400,400)
    elif stage == "gamble":
        position_left = (-300,125)
        position_right = (-100,125)
        image_right_size = (125,125)
        image_left_size= (125,125)
    else:
        position_left = (-100,125)
        position_right = (100,125)
        image_right_size= (125,125)
        image_left_size= (125,125)
    image_right = visual.ImageStim(win = win0,
                                       image = "data/Circ" + image_stim_name[image_type_1] +".png",
                                       pos = position_left,units = "pix"
                                       )
    image_left = visual.ImageStim(win = win0,
                                       image = "data/Circ" + image_stim_name[image_type_2] +".png",
                                       pos = position_right,units = "pix"
                                       )
    image_right.size= image_right_size
    image_left.size= image_left_size
    image_right.draw()# this will draw the right image onto the window
    image_left.draw()# this will draw the left image onto the window

# display the correct video when it is a view trial.
def flip_stim(image_type_1,image_type_2,side):
    '''
    We are preparing our Stimulus
    text_type == 0, "frog"
    text_type == 1, "face"
    text_type == 2, "sign"
    text_type == 3, "tomato"
    text_type == 4, "hand"
    text_type == 5, "pond"
    text_type == 6, "wrench"
    text_type == 7, "house"
    text_type == 8, "sun"
    text_type == 9, "pencil"
    '''
    image_stim_name = ["01","02","03","04","05","06","07","08","09","10"]
    if side == 0: # is it the left image
        outcome_image = image_stim_name[image_type_1]
    else:  # is it the right image
        outcome_image = image_stim_name[image_type_2]
    coin_flip = visual.MovieStim2(win = win0,
                                       filename = "data/coin"+image_stim_name[image_type_1]+image_stim_name[image_type_2]+outcome_image+".avi",
                                       units = "pix",
                                       pos = (0,0),
                                       loop=False,
                                       noAudio=True)
    return coin_flip
# create the outcome text for the learning trials.
def outcome_stim_learn(loss):
    '''
    We are creating our outcome in the learning trials
    '''
    loss_stim = visual.TextStim(win0,text=loss,
                                pos=(0,0),color = (1,1,1),
                                units = "pix", height = 32,
                                alignText = "center")
    return loss_stim, loss # this will draw the outcome onto the window
# create the outcome for the gambling trials
def outcome_stim_gamble(Mu_loss,loss_array,Gamble_type):
    '''
    We are creating our gambling outcome
    '''
    if Gamble_type == 1:
        outcome =np.random.permutation(loss_array)[0]

    if Gamble_type == 0:
        outcome = Mu_loss
    return outcome # this is the gambling trial
# estimate Mu
def Value_slider_mu():
    VAS = visual.Slider(win =win0,
                        ticks = [-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0],
                        labels = [-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,0],
                        granularity =.1,font = "Times New Roman",
                        units = "pix",
                        size = [1200,50],
                        style=('rating'))
    VAS.marker.color="green"
    VAS.marker.size =30
    text = visual.TextStim(win = win0,text = "בחר/י את ההפסד הממוצע של התוצאות האמיתיות (לא בדמיון) של המטבע בשלב הלמידה. \n בסיום לחצו SPACE",
                           pos=(0,300),color = (1,1,1),
                           units = "pix", height = 32,wrapWidth = 1200,
                           alignText = "center",languageStyle='RTL'
                          )
    return VAS, text # rate the average award trial
# estimate range of losses
def Value_slider_range():
        VAS_low = visual.Slider(win =win0,
                            ticks = [-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0],
                            labels = [-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,0],
                            granularity =.1,
                            units = "pix",
                            size = [1000,50],
                            pos = [0,-300],font = "Times New Roman",
                            style=('rating'))
        VAS_high = visual.Slider(win =win0,
                            ticks = [-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0],
                            labels = [-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,0],
                            granularity =.1,
                            units = "pix",
                            size = [1000,50],
                            pos = [0,0],font = "Times New Roman",
                            style=('rating'))
        VAS_low.marker.color="blue"
        VAS_high.marker.color="blue"
        VAS_low.marker.size =30
        VAS_high.marker.size =30
        line_1 = "\n בחר/י את ההפסד הגבוה והנמוך ביותר של התוצאות האמיתיות (לא בדמיון) בשלב הקודם \n"
        line_2 = "\n כשאת/ה מסיים/ת לחצ/י SPACE \n"
        text = visual.TextStim(win = win0,text = line_1+line_2,
                               pos=(0,300),color = (1,1,1),
                               units = "pix", height = 32,wrapWidth = 1200,
                               alignText = "center",languageStyle='RTL'
                              )
        text_low = visual.TextStim(win = win0,text = "ההפסד הגדול ביותר",
                               pos=(0,50),color = (1,1,1),
                               units = "pix", height = 32,wrapWidth = 1200,
                               alignText = "center",languageStyle='RTL'
                              )
        text_high = visual.TextStim(win = win0,text = "ההפסד הקטן ביותר",
                               pos=(0,-250),color = (1,1,1),
                               units = "pix", height = 32,wrapWidth = 1200,
                               alignText = "center",languageStyle='RTL'
                              )

        return VAS_low, VAS_high, text, text_low, text_high# rate the range trial
# estimate confidence
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
# wait text screen every 6 trials
def wait_scr():
    text = visual.TextStim(win = win0,text = "בבקשה נוח/י למשך 30 שניות",
                           pos=(0,300),color = (1,1,1),
                           units = "pix", height = 32,wrapWidth = 1200,
                           alignText = "center",languageStyle='RTL'
                          )
    text.draw()

parallel.setData(9) #task start
core.wait(0.1)
parallel.setData(0)
# Our main program loop
text_info = visual.TextStim(win0,text="לחצ/י ENTER על מנת להתחיל",
                             pos=(0,0),color = (1,1,1),
                             units = "pix", height = 32,
                             alignText = "center",languageStyle='RTL')
text_info.draw()
win0.flip()

key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()
# update the subject on what to do:

image_ins = visual.ImageStim(win0, image="instructions_1.JPG")
image_ins.draw()
win0.flip()
parallel.setData(10) # instructions learning
key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()
parallel.setData(0)
image_ins = visual.ImageStim(win0, image="instructions_2.JPG")
image_ins.draw()
win0.flip()
parallel.setData(10) # instructions learning
key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()
parallel.setData(0)
def create_trials(low,high,trial_n):
    """
    This function creates a list of trials for learning.

    Parameters
    ----------
    low : int
        The lower bound of the range of coins to use.
    high : int
        The upper bound of the range of coins to use.
    trial_n : int
        The number of trials to create.

    Returns
    -------
    loss_array : np.array
        An array of losses for each trial.
    outcome : np.array
        An array of outcomes for each trial.
    current_coin : np.array
        An array of the current coin for each trial.
    task_array : np.array
        An array of the task for each trial.
    """
    break_flag=0
    # Create empty arrays to store the losses, outcomes, and current coins.
    loss_array = np.array([])
    outcome = np.array([])
    current_coin = np.array([])
    task_array = np.array([])
    # Iterate over the range of coins.
    for coin in range(low,high):
            # what is the mu for the current trial i
            loss_Mu  = Mu[stim_generate[coin]] 
            if SD[coin] == "LH":
                # set loss_SD_img and loss_SD_view based on value of SD
                loss_SD_img = 1 
                loss_SD_view = 6
            elif SD[coin] == "HL":
                loss_SD_img = 6
                loss_SD_view = 1
            elif SD[coin] == "MM":
                loss_SD_img = 3
                loss_SD_view = 3
            # create loss array for view trials, imagination trials.
            loss_array_tmp = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view+1,
                loss_Mu+loss_SD_view-1,loss_Mu+loss_SD_view-1,
                loss_Mu+loss_SD_view,loss_Mu+loss_SD_view,
                loss_Mu - loss_SD_view+1,loss_Mu-loss_SD_view+1,
                loss_Mu - loss_SD_view-1,loss_Mu-loss_SD_view-1,
                loss_Mu - loss_SD_view,loss_Mu-loss_SD_view,
                loss_Mu+loss_SD_img+1,loss_Mu+loss_SD_img+1,
                loss_Mu+loss_SD_img-1,loss_Mu+loss_SD_img-1,
                loss_Mu+loss_SD_img,loss_Mu+loss_SD_img,
                loss_Mu - loss_SD_img+1,loss_Mu-loss_SD_img+1,
                loss_Mu - loss_SD_img-1,loss_Mu-loss_SD_img-1,
                loss_Mu - loss_SD_img,loss_Mu-loss_SD_img])     
            # shuffle loss_array_tmp using randomize array
            # flip values in outcome_tmp if coin_heads is 0
            task_array_tmp = np.array(["view","view","view","view","view","view","view","view","view","view","view","view",
                "img","img","img","img","img","img","img","img","img","img","img","img"])
            if coin_heads[coin]==1: 
                # if coin heads is 1 then higher than avg loss is received whenever the right image is drawn as outcome
                outcome_tmp = np.array([0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1])
            else:
                outcome_tmp = np.array([1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0])
            # update loss_array, outcome, and current_coin with current coin's trials
            loss_array = np.append(loss_array,loss_array_tmp)
            outcome = np.append(outcome,outcome_tmp)
            current_coin = np.append(current_coin,np.repeat(stim_generate[coin],24))
            task_array = np.append(task_array,task_array_tmp)
    # shuffle all trials together using randomize array
    # Initialize lists to store indices for each category
    view_indices_coin_1 = []
    view_indices_coin_2 = []
    img_indices_coin_1 = []
    img_indices_coin_2 = []
    # shuffle outcome_tmp using randomize array
    for i, task in enumerate(task_array):
        if (high - low) > 1:
            if task == "view" and current_coin[i] == stim_generate[low]:
                view_indices_coin_1.append(i)
            elif task == "view" and current_coin[i] == stim_generate[high-1]:
                view_indices_coin_2.append(i)
            elif task == "img" and current_coin[i] == stim_generate[low]:
                img_indices_coin_1.append(i)
            elif task == "img" and current_coin[i] == stim_generate[high-1]:
                img_indices_coin_2.append(i)
        else:
            if task == "view":
                view_indices_coin_1.append(i)
            elif task == "img":
                img_indices_coin_1.append(i)
    # Shuffle the index lists
    np.random.shuffle(view_indices_coin_1)
    np.random.shuffle(img_indices_coin_1)
    np.random.shuffle(view_indices_coin_2)
    np.random.shuffle(img_indices_coin_2)
    # Select the first three indices from each shuffled list
    selected_indices = []
    for i in range(0, len(view_indices_coin_1)-3, 3):
        if (high - low) > 1:
            selected_indices += [view_indices_coin_1[i:i+3], img_indices_coin_1[i:i+3], view_indices_coin_2[i:i+3], img_indices_coin_2[i:i+3]]
        else:
            selected_indices += [view_indices_coin_1[i:i+3], img_indices_coin_1[i:i+3]]
    selected_indices = np.array(selected_indices).flatten()
    randomize =  np.arange(len(loss_array))       
    loss_array = loss_array[selected_indices]
    outcome = outcome[selected_indices]
    current_coin = current_coin[selected_indices]
    task_array = task_array[selected_indices]
    print("current_coin",current_coin)
    print("task_array",task_array)
    print("loss_array",loss_array)
    print("outcome",outcome)
    for trial in range(trial_n):
            phase = "training"
            task = "comb"
            parallel.setData(0)
            trial_no.append(f'trial_learning: {trial}')
            time_value_array.append(datetime.now().strftime("%H%M%S"))
            if "comb" in task:
                if task_array[trial]=="img": # now it only shows imagination trials
                    line_1 ="\n בבקשה דמיין/י כאילו התוצאה המסומנת בירוק היא התוצאה של ההטלה\n"
                    line_2 = "\nלחץ/י SPACE להמשיך\n"
                    text_view = visual.TextStim(win0,text=line_1+line_2,
                                    pos=(0,-300),color = (1,1,1),
                                    units = "pix", height = 32,wrapWidth=1500,
                                    alignText = "center",languageStyle='RTL')
                # draw the text onto the window
                    if outcome[trial]==0:
                        outcome_circle = visual.Circle(win = win0, lineColor = "green",edges = 360,
                                                        lineWidth = 30,
                                                        radius = 220,units = "pix",opacity = .8,
                                                        pos = (-270,0))
                        outcome_circle.draw()
                    else:
                        outcome_circle = visual.Circle(win = win0, lineColor = "green",edges = 360,
                                                        lineWidth = 30,
                                                        radius = 220,units = "pix",opacity = .8,
                                                        pos = (270,0))
                        outcome_circle.draw()
                if task_array[trial]=="view":
                    text_view = visual.TextStim(win0,text="על מנת לצפות בתוצאה האמיתית של המטבע, לחץ/י SPACE",
                                                pos=(0,-300),color = (1,1,1),
                                                units = "pix", height = 32,wrapWidth=1500,
                                                alignText = "center",languageStyle='RTL')

                # draw the text onto the window
                text_view.draw()
                # draw both coin sides onto the screen
                image_stim(coin_side_1[current_coin[trial].astype(int)],coin_side_2[current_coin[trial].astype(int)],stage = "learning")
                # flip window onto screen
                win0.flip()
                if task_array[trial]=="img":
                    parallel.setData(3)
                else:
                    parallel.setData(4)
                start_time = clock.getTime()
                key = event.waitKeys(maxWait = 9999,keyList = ["space"],clearEvents = True)
                parallel.setData(0)
                if 'space' in key:
                    sub_response_array.append(6666)
                    stop_time = clock.getTime()
                    response_latency.append(round(stop_time-start_time,4)*1000)
                    pass
                parallel.setData(0)
                core.wait(.2)
                if task_array[trial]=="view":
                    coin_flip = flip_stim(coin_side_1[current_coin[trial].astype(int)],coin_side_2[current_coin[trial].astype(int)],outcome[trial])
                else:
                    coin_flip = visual.MovieStim2(win = win0,
                                                       filename = "data/coin000000.avi",
                                                       units = "pix",
                                                       loop=False,
                                                       noAudio=True,
                                                       pos = (0,0))
                while coin_flip.status != constants.FINISHED:
                    # draw the movie
                    coin_flip.draw()
                    # flip buffers so they appear on the window
                    win0.flip()
                parallel.setData(5)
                parallel.setData(0)
                final_task_comb_array.append(task_array[trial])
                sub_id_array.append(sub_id)
                block_array.append(phase)
                final_gamble_array.append("no")
                date_value_array.append(date_val)
                loss = loss_array[trial]
                print("loss",loss)
                print("outcome[trial]",outcome[trial])
                print()
                print("coin_heads[current_coin[trial].astype(int)]",coin_heads[current_coin[trial].astype(int)])
                outcome_stim_l, loss = outcome_stim_learn(loss)
                outcome_stim_l.draw()
                win0.flip()
                parallel.setData(6) # show outcome learning
                core.wait(1.5)
                parallel.setData(0)
                final_head_array.append(outcome[trial]==coin_heads[current_coin[trial].astype(int)])
                final_loss_array.append(loss)
                final_Mu_array.append(Mu[stim_generate[current_coin[trial].astype(int)]])
                print("SD",SD[stim_generate==current_coin[trial].astype(int)])
                final_SD_array.append(SD[stim_generate==current_coin[trial].astype(int)])
                # clear the Screen
                fixation_cross()
                win0.flip()
                parallel.setData(2)
                core.wait(.1)
                parallel.setData(0)
                core.wait(.1)
                final_outcome_array.append("NA")
                final_task_array.append(task)
                final_coin_side_1_array.append(coin_side_1[stim_coin[current_coin[trial].astype(int)]])
                final_coin_side_2_array.append(coin_side_2[stim_coin[current_coin[trial].astype(int)]])
                final_fix_time_array.append("NA")
                final_estimation_mu.append("NA")
                final_estimation_rangelow.append("NA")
                final_estimation_range_high.append("NA")
                final_estimation_confidence_mu.append("NA")
                final_estimation_confidence_range.append("NA")
                final_use_imagery.append("NA")
                final_sure_option.append("NA")
            # gambling part:
    
    for trial_gamble in range(low,high):
        parallel.setData(0)
        line_1 ="\nלחץ/י D אם את/ה רוצה להמר על תוצאות המטבע\n"
        line_2 = "\nאחרת, לחצ/י K אם את/ה מעדיפ/ה לקבל את הההפסד למטה\n"
        line_3 = "\nלחץ/י ENTER להמשיך\n"
        text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
                             pos=(0,0),color = (1,1,1),
                            units = "pix", height = 32,wrapWidth=1500,
                            alignText = "center",languageStyle='RTL')
        text_info_start.draw()
        
        win0.flip()
        key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
        if 'return' in key:
            pass
        win0.flip()
        # Define loss_Mu as the Mu value for the current trial i
        loss_Mu  = Mu[stim_generate[trial_gamble]] # what is the mu for the current trial i
        # Determine the value of loss_SD_img and loss_SD_view based on the current trial's SD value
        if SD[trial_gamble] == "LH":
            loss_SD_img = 1 
            loss_SD_view = 6
        elif SD[trial_gamble] == "HL":
            loss_SD_img = 6
            loss_SD_view = 1
        elif SD[trial_gamble] == "MM":
            loss_SD_img = 3
            loss_SD_view = 3
        # Create an array of sure options based on the loss_Mu and loss_SD_view values
        sure_options = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view-1,
            loss_Mu+loss_SD_view,loss_Mu-loss_SD_view-1,
            loss_Mu-loss_SD_view+1,loss_Mu-loss_SD_view,
            loss_Mu+loss_SD_img+1,loss_Mu+loss_SD_img-1,
            loss_Mu+loss_SD_img,loss_Mu-loss_SD_img-1,
            loss_Mu-loss_SD_img+1,loss_Mu-loss_SD_img])
        loss_array_view = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view-1,
            loss_Mu+loss_SD_view,loss_Mu-loss_SD_view-1,
            loss_Mu-loss_SD_view+1,loss_Mu-loss_SD_view])
        loss_array_all = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view-1,
            loss_Mu+loss_SD_view,loss_Mu-loss_SD_view-1,
            loss_Mu-loss_SD_view+1,loss_Mu-loss_SD_view,
            loss_Mu+loss_SD_img+1,loss_Mu+loss_SD_img-1,
            loss_Mu+loss_SD_img,loss_Mu-loss_SD_img-1,
            loss_Mu-loss_SD_img+1,loss_Mu-loss_SD_img])
        sure_options = np.append(sure_options,sure_options)
        if trial_gamble == 0:
            image_ins = visual.ImageStim(win0, image="instructions_3.JPG")
            image_ins.draw()
            win0.flip()
            parallel.setData(10) # instructions learning
            key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
            if 'return' in key:
                pass
            win0.flip()
            parallel.setData(0)
        if trial_n ==24: # decide the length of training trials.
            gamble_blocks = 2
        else:
            gamble_blocks = 4
        for l in range(gamble_blocks):
            if l%2 == 0 :
                line_1 ="\n עכשיו, יש לך את ההזדמנות להשתמש במה שלמדת על תוצאות המטבע\n"
                line_2 = "\nאבל, התוצאות שהתקבלו בדמיון, אינם רלבנטיות להחלטה שלך\n"
                line_3 = "\nלחץ/י ENTER להמשיך\n"
                text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
                                        pos=(0,0),color = (1,1,1),
                                        units = "pix", height = 32,wrapWidth=1500,
                                        alignText = "center",languageStyle='RTL')
                pin = 12
            elif l % 2 == 1:
                line_1 ="\n עכשיו, יש לך את ההזדמנות להשתמש במה שלמדת על תוצאות המטבע\n"
                line_2 = "\nהתוצאות שהתקבלו בדמיון רלבנטיות במידה דומה לשאר התוצאות בהחלטה שלך\n"
                line_3 = "\nלחץ/י ENTER להמשיך\n"
                text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
                                        pos=(0,0),color = (1,1,1),
                                        units = "pix", height = 32,wrapWidth=1500,
                                        alignText = "center",languageStyle='RTL')
                pin = 11
            elif "comb" not in task:
                line_1 ="\n עכשיו, יש לך את ההזדמנות להשתמש במה שלמדת על תוצאות המטבע\n"
                line_2 = "\nכל צעדי הניסוי רלבנטיים להחלטה שלך\n"
                line_3 = "\nלחץ/י ENTER להמשיך\n"
                text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
                                        pos=(0,0),color = (1,1,1),
                                        units = "pix", height = 32,wrapWidth=1500,
                                        alignText = "center",languageStyle='RTL')
                pin = 13                    
            text_info_start.draw()
            win0.flip()
            parallel.setData(pin)
            key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
            if 'return' in key:
                pass
            win0.flip()
            # Shuffle the order of the sure options
            np.random.shuffle(sure_options)
            # Iterate through each option in the sure options array
            for s in range(24):
                fixation_cross()
                # flip window onto the screen
                win0.flip()
                parallel.setData(2)
                core.wait(.2)
                parallel.setData(0)
                time_fixation = 0.4
                # wait 1 sec
                core.wait(time_fixation-0.2)
                win0.flip()
                # Append the relevant information to the relevant arrays
                final_coin_side_1_array.append(coin_side_1[stim_coin[trial_gamble]])
                final_coin_side_2_array.append(coin_side_2[stim_coin[trial_gamble]])
                final_fix_time_array.append(time_fixation)
                trial_no.append(f'loop: {l}_option: {s}')
                time_value_array.append(datetime.now().strftime("%H%M%S"))
                sub_id_array.append(sub_id)
                date_value_array.append(date_val)
                block_array.append(phase)
                final_Mu_array.append(Mu[stim_generate[trial_gamble]])
                final_SD_array.append(SD[trial_gamble])
                final_head_array.append(coin_heads[trial_gamble])
                final_outcome_array.append("NA")
                final_task_array.append(task)
                final_sure_option.append(sure_options[s])
                # Create a visual text stimulus to display the current sure option
                text_mu = visual.TextStim(win0,text=sure_options[s],
                                             pos=(200,-20),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center")
                # Create a visual text stimulus to display the "loss" message in Hebrew
                text_half = visual.TextStim(win0,text="הפסד בטוח",
                                             pos=(200,20),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center",languageStyle="RTL")
                text_coin = visual.TextStim(win0,text="מטבע",
                                             pos=(-200,0),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center",languageStyle="RTL")
                text_half.draw()
                text_coin.draw()
                text_mu.draw()
                image_stim(coin_side_1[current_coin[trial_gamble].astype(int)],coin_side_2[current_coin[trial_gamble].astype(int)],
                    stage="gamble")
                win0.flip()
                parallel.setData(14)
                start_time = clock.getTime()
                core.wait(0.05)
                parallel.setData(0)
                key = event.waitKeys(clearEvents = True,keyList = ['q','d','k'],maxWait = 9999)
                if key is None:
                    print('did not press at all')
                    sub_response_array.append(999)
                    response_latency.append(99999)
                else:
                    if 'd' in key: # d is for match
                        print('pressed gamble')
                        gamble = 1
                        sub_response_array.append(1)
                        stop_time = clock.getTime()
                        response_latency.append(round(stop_time-start_time,4)*1000)
                        parallel.setData(7)
                    if 'k' in key: # j is for non match
                        print('pressed not gamble')
                        gamble = 0
                        sub_response_array.append(0)
                        stop_time = clock.getTime()
                        response_latency.append(round(stop_time-start_time,4)*1000)
                        parallel.setData(8)
                    if 'q' in key:
                        sub_response_array.append(9999)
                        stop_time = clock.getTime()
                        response_latency.append(round(stop_time-start_time,4)*1000)
                        break_flag = 1
                        break
                if gamble==1 and l%2 == 0:
                    loss = outcome_stim_gamble(sure_options[s],loss_array_view,1)
                elif gamble==1 and l%2 == 1:
                    loss = outcome_stim_gamble(sure_options[s],loss_array_all,1)
                elif gamble==0:
                    loss = outcome_stim_gamble(sure_options[s],loss_array_all,0)
                core.wait(0.05)
                parallel.setData(0)
                final_use_imagery.append(l%2)
                final_loss_array.append(loss)
                final_task_comb_array.append("NA")
                final_estimation_mu.append("NA")
                final_gamble_array.append("yes")
                final_estimation_rangelow.append("NA")
                final_estimation_range_high.append("NA")
                final_estimation_confidence_mu.append("NA")
                final_estimation_confidence_range.append("NA")
        win0.flip()
        if trial_gamble == 0:
            # update the subject on what to do:
            line_1 ="\n אנא קרא/י לנסיינ/ית\n"
            text_info_start = visual.TextStim(win0,text=line_1,
                                      pos=(0,0),color = (1,1,1),
                                      units = "pix", height = 32,wrapWidth=1500,
                                      alignText = "center",languageStyle='RTL')
            text_info_start.draw()
            win0.flip()
            key = event.waitKeys(maxWait = 9999,keyList = ["v"],clearEvents = True)
            if 'return' in key:
                pass
            win0.flip()
        Value_Mu, text_mu = Value_slider_mu()
        continueRoutine = True
        parallel.setData(15)
        while continueRoutine:
            Value_Mu.draw()
            text_mu.draw()
            image_stim(coin_side_1[current_coin[trial_gamble].astype(int)],coin_side_2[current_coin[trial_gamble].astype(int)],
                    stage = "rate")
            win0.flip()
            keys = event.getKeys()
            if 'space' in keys:
                if Value_Mu.getRating() is not None:
                    continueRoutine = False
        parallel.setData(0)
        final_estimation_mu.append(Value_Mu.getRating())
        Value_conf, text_conf = Value_slider_confidence()
        parallel.setData(17)
        continueRoutine = True
        while continueRoutine:
            Value_conf.draw()
            text_conf.draw()
            image_stim(coin_side_1[current_coin[trial_gamble].astype(int)],coin_side_2[current_coin[trial_gamble].astype(int)],
                    stage = "rate")
            win0.flip()
            keys = event.getKeys()
            if 'space' in keys:
                if Value_conf.getRating() is not None:
                    continueRoutine = False
        parallel.setData(0)
        final_estimation_confidence_mu.append(Value_conf.getRating())
        Value_range_low, Value_range_high, text_range, text_low, text_high= Value_slider_range()
        continueRoutine = True
        parallel.setData(16)
        while continueRoutine:
            Value_range_low.draw()
            Value_range_high.draw()
            text_range.draw()
            text_low.draw()
            text_high.draw()
            image_stim(coin_side_1[current_coin[trial_gamble].astype(int)],coin_side_2[current_coin[trial_gamble].astype(int)],
                    stage = "rate")
            win0.flip()
            keys = event.getKeys()
            if 'space' in keys:
                completed_ratings = 0
                for scale in [Value_range_low, Value_range_high]:
                    if scale.getRating() is not None:
                        completed_ratings = completed_ratings + 1

                    if completed_ratings == 2:
                        continueRoutine = False # end now
        parallel.setData(0)
        final_estimation_rangelow.append(Value_range_low.getRating())
        final_estimation_range_high.append(Value_range_high.getRating())
        Value_conf, text_conf = Value_slider_confidence()
        continueRoutine = True
        parallel.setData(17)
        while continueRoutine:
            Value_conf.draw()
            text_conf.draw()
            image_stim(coin_side_1[current_coin[trial_gamble].astype(int)],coin_side_2[current_coin[trial_gamble].astype(int)],
                    stage = "rate")
            win0.flip()
            keys = event.getKeys()
            if 'space' in keys:
                if Value_conf.getRating() is not None:
                    continueRoutine = False
        parallel.setData(0)
        final_estimation_confidence_range.append(Value_conf.getRating())
        block_array.append(phase)
        trial_no.append(f'loop: {l}')
        sub_id_array.append(sub_id)
        sub_response_array.append("NA")
        response_latency.append("NA")
        date_value_array.append(date_val)
        time_value_array.append(datetime.now().strftime("%H%M%S"))
        final_coin_side_1_array.append(coin_side_1[stim_coin[trial_gamble]])
        final_coin_side_2_array.append(coin_side_2[stim_coin[trial_gamble]])
        final_Mu_array.append(Mu[stim_generate[trial_gamble]])
        final_SD_array.append(SD[trial_gamble])
        final_head_array.append(coin_heads[trial_gamble])
        final_outcome_array.append(outcome[trial])
        final_task_comb_array.append("NA")
        final_task_array.append(task)
        final_gamble_array.append("no")
        final_loss_array.append("NA")
        final_use_imagery.append("NA")
        final_fix_time_array.append("NA")
        final_sure_option.append("NA")
        save_results(save_file_name)
        if break_flag==1:
            break
    return 
create_trials(low = 0,high = 1,trial_n = 24)
create_trials(low = 1,high = 3,trial_n = 48)
win0.flip()
# update the subject on what to do:
line_1 ="\n אנא קרא/י לנסיינ/ית\n"
text_info_start = visual.TextStim(win0,text=line_1,
                                  pos=(0,0),color = (1,1,1),
                                  units = "pix", height = 32,wrapWidth=1500,
                                  alignText = "center",languageStyle='RTL')
text_info_start.draw()
win0.flip()
key = event.waitKeys(maxWait = 9999,keyList = ["v"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()

create_trials(low = 3,high = 5,trial_n = 48)
'''
print(len(trial_no))
print(len(time_value_array))
print(len(sub_id_array))
print(len(date_value_array))
print(len(final_fix_time_array))
print(len(sub_response_array))
print(len(final_coin_side_1_array))
print(len(final_coin_side_2_array))
print(len(response_latency))
print(len(block_array))
print(len(final_Mu_array))
print(len(final_SD_array))
print(len(final_head_array))
print(len(final_outcome_array))
print(len(final_task_array))
print(len(final_loss_array))
print(len(final_task_comb_array))
print(len(final_estimation_mu))
print(len(final_estimation_rangelow))
print(len(final_estimation_range_high))
print(len(final_estimation_confidence_mu))
print(len(final_estimation_confidence_range))
print(len(final_sure_option))
'''
# create a data frame:
# save the file
save_results(save_file_name)
# tidy up our resorces
win0.close()
print("OK, program has now closed")
