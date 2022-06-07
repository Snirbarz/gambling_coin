'''
Stimuli: all presented at 80cm away from the screen
    fixation: black cross 10.1 d VA
              thickness will be 0.1 degress VA =
              500-1000ms (core.wait(1000),time.sleep(1))
    instructions:
              participants recieve 200 credits in the begining of the Experiment
              they are told that they are going to participate in a gambling task
              where they will choose to gamble on a result of a coin.
              If they lose, they lost the amount, if they win, they lose a smaller amount.
              If they don't gamble they lost half of the amount.
    Stimulus: 8 images from the exposure task
              clustered into 28 pairs, each representing a single double sided coin
              for each coin participant view or imagine an outcome
              When coin lands on heads- an outcome of 0 will be presented
              When coin lands on tails an outcome mu ([-6,-8,-10]) and sd (1 or 2) will be generated
              10 trials total, non biased coin (pseudorandomized).

              images appear for max 1000ms
              image at the center of the screen (size unknown)
              white backgroud (rgb --> 1,1,1)
              elvers.us/perception/visualAngleVA = figure out how to convert to cm and then pixels
              36 VA = (30.5425 cm) 1112 == 0


    Mask:     no mask


    Response: keyboard --> 'space' for moving on to the next trial
                           'd' is for choosing to gamble
                           'k' for choosing to receive the sure loss
    Task:
            14.28% trials ==> training (2 imagination and 2 viewing; 4 coins)
            46.42% trials ==> Imagination trials (12 coins)
            46.42% of trials ==> Viewing trials (12 coins)
    Experimental Session:
            2 imagination trials
            Other trials are randomized within 4 blocks, 6 trials each with 30 seconds rest in between
            Presented in random order
    Trial:
            show coin sides and whether it's an imagination or observe trial
            fixation start (500ms)
            imagination/viewing trial
            rate mean (0-20; no time limit)
            confidence rating  (0-100 VAS; no time limit)
            choose range (0-20; no time limit)
            confidence rating (0-100 VAS; no time limit)
            gamble (show coin sides and choose to to either gamble or accept a specific loss; no time limit?)
            show result? (500ms)
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
from psychopy import logging, visual, core, event, clock, gui, parallel
from datetime  import datetime
import numpy as np
import pandas as pd
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
import pathlib

# set parallel port address
parallel.setPortAddress(0x3EFC)
parallel.setData(0) # reset bits
date_val = datetime.now().strftime("%Y-%m-%d") # obtain the current date

# we want to setup our experiment: sub_id, sub_gender, sub_age
# create list of file save
my_Dlg = gui.Dlg(title = "gambling task")
my_Dlg.addText("Subject info")
my_Dlg.addField("Exp Date",date_val)
my_Dlg.addField("ID","")

#obtain the ID from the user
show_dlg = my_Dlg.show()
if my_Dlg.OK:
    print(show_dlg)
    # set up our save file date_sub_id_linetask.csv
    save_file_name = show_dlg[0]+"_"+show_dlg[1]+'_gambling_task.csv'
    print(save_file_name)
else:
    print("user cancelled")
print("Experiment setup information")
print(show_dlg)
# create a save file save_path
save_path = gui.fileSaveDlg(initFileName=save_file_name,
                            prompt = 'select Save File',
                            )

print("Output from save dialog")
print(save_path)
print("finished")
cur_time = datetime.now().strftime('%H%M%S')

# create variables
no_trials = 28 # number of total trials (equal to number of unique coins)
Mu = np.array([-6,-6,-10,-10,-6,-6,-6,-6,-8,-8,-8,-8,-10,-10,-10,-10,-6,-6,-6,-6,-8,-8,-8,-8,-10,-10,-10,-10]) # the mean of the coin which is the same for both imagination and view trials.
SD = np.array(["LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL","LH","HL"]) # The distribution width of the imagined and real outcomes the first letter is for the imagination trials.
use_imagery = np.array([1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1]) # after imagination trials should the participant use imagery (1) or not (0) in his decisions
training_task = np.array(["view","img","comb","comb"])# task in the training block
test_task = np.random.permutation(np.array(["comb_1","comb_2","comb_3","comb_4"]))# task in the test blocks
coin_array = np.array(range(no_trials))# number of coins (28)
coin_side_1 = np.array([0,0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,3,3,3,3,4,4,4,5,5,6]) # side 1 index of the coin
coin_side_2 = np.array([1,2,3,4,5,6,7,2,3,4,5,6,7,3,4,5,6,7,4,5,6,7,5,6,7,6,7,7]) # side 2 index of the coin
coin_heads = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1]) # coin heads (1) or tails (0)
np.random.permutation(coin_heads) # permute which side is heads or tails

cur_time_array = []
trial_no = [] # current trial number (0-27)
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
stim_generate = [] # decide which combination of mu and SD is selected for the current trial.
new_coin_array = np.random.permutation(coin_array) # the coin sides themselves are completely random
new_generate_array = np.random.permutation(coin_array[4:28]) # the combination of mu and SD is deterministic for the first 4 trials and then random for the rest.
new_generate_array=np.concatenate((range(4),new_generate_array),axis = None) # create array separating the first 4 training trials from the last 24 trials
for n in range(no_trials):
    stim_coin.append(new_coin_array[n])
    stim_generate.append(new_generate_array[n])
    cur_time_array.append(datetime.now().strftime('%H%M%S'))
stim_coin = np.array(stim_coin).flatten()
stim_generate = np.array(stim_generate).flatten()
cur_time_array = np.array(cur_time_array).flatten()

# create gamble array
logging.console.setLevel(logging.WARNING) # log warning messages
print("*************************************")
print("PSYCHOPY LOGGING set to : WARNING")
print(datetime.now())
print("Gambling TASK: version alpha")
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


# create our fixation cross
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
def image_stim(image_type_1,image_type_2):
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
    image_stim_name = ["01","02","03","04","05","06","07","08"]

    image_right = visual.ImageStim(win = win0,
                                       image = "data/Circ" + image_stim_name[image_type_1] +".png",
                                       units = "pix",
                                       pos = (-270,0))
    image_left = visual.ImageStim(win = win0,
                                       image = "data/Circ" + image_stim_name[image_type_2] +".png",
                                       units = "pix",
                                       pos = (270,0))
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
    '''
    image_stim_name = ["01","02","03","04","05","06","07","08"]
    if side == 0: # is it the left image
        outcome_image = image_stim_name[image_type_1]
    else:  # is it the right image
        outcome_image = image_stim_name[image_type_2]
    coin_flip = visual.VlcMovieStim(win = win0,
                                       filename = "data/coin"+image_stim_name[image_type_1]+image_stim_name[image_type_2]+outcome_image+".avi",
                                       units = "pix",
                                       pos = (0,0),
                                       autoStart=True)
    return coin_flip
# create the outcome text for the learning trials.
def outcome_stim_learn(loss,side):
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
        outcome = Mu_loss/2
    return outcome # this is the gambling trial
# estimate Mu
def Value_slider_mu():
    VAS = visual.Slider(win =win0,
                        ticks = [-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0],
                        labels = [-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,0],
                        granularity =.1,
                        units = "pix",
                        size = [1200,50],
                        style=('rating'))
    VAS.marker.color="green"
    VAS.marker.size =30
    text = visual.TextStim(win = win0,text = "בחר/י את ההפסד הממוצע של התוצאות האמיתיות בשלב הקודם. \n בסיום לחצו SPACE",
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
                            pos = [0,-300],
                            style=('rating'))
        VAS_high = visual.Slider(win =win0,
                            ticks = [-20,-19,-18,-17,-16,-15,-14,-13,-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,-0],
                            labels = [-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,0],
                            granularity =.1,
                            units = "pix",
                            size = [1000,50],
                            pos = [0,0],
                            style=('rating'))
        VAS_low.marker.color="blue"
        VAS_high.marker.color="blue"
        VAS_low.marker.size =30
        VAS_high.marker.size =30
        line_1 = "\n בחר/י את ההפסד הגבוה והנמוך ביותר של התוצאות האמיתיות בשלב הקודם \n"
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
# estimate confidenct
def Value_slider_confidence():
    line_1 = "\n כמה בטוח/ה את/ה בערכות שלך מ-0 עד 100 \n"
    line_2 = "\n כשאת/ה מסיים/ת לחצ/י SPACE \n"
    text = visual.TextStim(win = win0,text = line_1+line_2,
                           pos=(0,300),color = (1,1,1),
                           units = "pix", height = 32,wrapWidth = 1000,
                           alignText = "center",languageStyle='RTL'
                          )
    VAS = visual.Slider(win =win0,
                        ticks = range(20), # values are from 0 to 20, but they need to be multiplied by 5
                        labels = ["0- אל חוטב ללכ","50 - חוטב הדימב תינוניב","100- חוטב דואמ "],
                        granularity =.1,
                        units = "pix",
                        size = [1000,50],
                        pos = [0,0],
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
break_flag=0
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

line_1 =" \nבמטלה הבאה, תתבקש/י ללמוד את הערכים השונים האפשריים בהטלת המטבע\n"
line_2 = "\nראשית, את/ה תצפה/י בשני צדי המטבע.\n"
line_3 = "\nשנית, תופיע בפניך הטלת המטבע עם תוצאה אקראית שתופיע על המסך.\n"
line_4 = "\nאחרי שלב הלמידה, תעבור/י לשלב הימורים הקשור למה שלמדת.\n"
line_5 = "\nלחץ/י ENTER להמשיך\n"
text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3+line_4+line_5,
				             pos=(0,0),color = (1,1,1),
                             units = "pix", height = 32,wrapWidth=1500,
                             alignText = "center",languageStyle='RTL')

text_info_start.draw()
win0.flip()
parallel.setData(10) # instructions learning
key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()
parallel.setData(0)
for i in range(2,3):
        # if trial i is between 0 and 3 (included) then it is training blocks
        # if trials i >=4 then it is test blcok
        if i<4:
            phase = "training"
            task = training_task[i]
        else:
            phase = "test"
            if i>=4 and i<10:
                task = test_task[0] # first 6 trials in the test trials
            elif  i>=10 and i<16:
                wait_scr() # wait 30 seconds
                win0.flip()
                core.wait(30)
                win0.flip()
                task = test_task[1]
            elif  i>=16 and i<22:
                wait_scr()
                win0.flip()
                core.wait(30)
                win0.flip()
                task = test_task[2]
            elif  i>=22 and i<28:
                wait_scr()
                win0.flip()
                core.wait(30)
                win0.flip()
                task = test_task[3]
        outcome = np.array([0,0,0,0,0,0,1,1,1,1,1,1])# is the outcome left or right (0 or 1)
        loss_Mu  = Mu[stim_generate[i]] # what is the mu for the current trial i
        if SD[stim_generate[i]] == "LH":
            loss_SD_img = 1 # low range
            loss_SD_view = 4
        elif SD[stim_generate[i]] == "HL":
            loss_SD_img = 4
            loss_SD_view = 1
        # create loss array for view trials, imagination trials, and combined imagination and view trials.
        loss_array = np.array([0,0,0,0,0,0,0,0,0,0,0,0])
        if i ==0: #view trial
            loss_array = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view+1,
                loss_Mu+loss_SD_view-1,loss_Mu+loss_SD_view-1,
                loss_Mu+loss_SD_view,loss_Mu+loss_SD_view,
                loss_Mu - loss_SD_view+1,loss_Mu-loss_SD_view+1,
                loss_Mu - loss_SD_view-1,loss_Mu-loss_SD_view-1,
                loss_Mu - loss_SD_view,loss_Mu-loss_SD_view])
            randomize = np.arange(len(outcome))
            np.random.shuffle(randomize)
            if coin_heads[i]==1:# if coin heads is 1 then higher than avg loss is received whenever the right image is drawn as outcome
                outcome = np.array([0,0,0,0,0,0,1,1,1,1,1,1])
            else:
                outcome = np.array([1,1,1,1,1,1,0,0,0,0,0,0])
            outcome = outcome[randomize]
            loss_array = loss_array[randomize]
            line_1 = "\n בבקשה שימ/י לב לתוצאות של הטלת המטבע \n"
            line_2 = "\n לחץ/י ENTER להמשיך \n"
            text_info_start = visual.TextStim(win0,text=line_1+line_2,
                                pos=(0,0),color = (1,1,1),
                                units = "pix", height = 32,wrapWidth=1500,
                                alignText = "center",languageStyle='RTL')
            text_info_start.draw()
            win0.flip()
            parallel.setData(10) # instructions learning
            key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
            if 'return' in key:
                pass
            win0.flip()
            parallel.setData(0)
        if i ==1: # imagination trial
            loss_array = np.array([loss_Mu + loss_SD_img+1,loss_Mu+loss_SD_img+1,
                loss_Mu + loss_SD_img-1,loss_Mu+loss_SD_img-1,
                loss_Mu + loss_SD_img,loss_Mu+loss_SD_img,
                loss_Mu - loss_SD_img+1,loss_Mu-loss_SD_img+1,
                loss_Mu - loss_SD_img-1,loss_Mu-loss_SD_img-1,
                loss_Mu - loss_SD_img,loss_Mu-loss_SD_img]) # 2 examples of each type of loss
            randomize = np.arange(len(outcome))
            np.random.shuffle(randomize)
            if coin_heads[i]==1:
                outcome = np.array([0,0,0,0,0,0,1,1,1,1,1,1])
            else:
                outcome = np.array([1,1,1,1,1,1,0,0,0,0,0,0])
            outcome = outcome[randomize]
            loss_array = loss_array[randomize]
            line_1 ="\nעכשיו המטלה תשתנה\n"
            line_2 = "\nבמקום לצפות בתוצאות ההטלה של המטבע\n"
            line_3 = "\nאתה תצטרך/י לדמיין בראשך כאילו למטבע יש תוצאה מסוימת\n"
            line_4 = "\nהתוצאה המסוימת תהיה מודגשת בירוק\n"
            line_5 = "\nלחץ/י ENTER להמשיך\n"
            text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3+line_4+line_5,
                pos=(0,0),color = (1,1,1),
                units = "pix", height = 32,wrapWidth=1500,
                alignText = "center",languageStyle='RTL')

            text_info_start.draw()
            win0.flip()
            parallel.setData(10) # instructions learning
            key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
            if 'return' in key:
                pass
            win0.flip()
            parallel.setData(0)
        if i ==2: # first training trial with combined instructions
            line_1 ="\nעכשיו, המטלה תכלול גם צעדי צפייה וצעדי דמיון\n"
            line_2 = "\nבכל פעם יודגש בפניך אם צריך רק לצפות או רק ולדמיין\n"
            line_3 = "\nלחץ/י ENTER להמשיך\n"
            text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
				     		        pos=(0,0),color = (1,1,1),
                             		units = "pix", height = 32,wrapWidth=1500,
                             		alignText = "center",languageStyle='RTL')

            text_info_start.draw()
            win0.flip()
            parallel.setData(10) # instructions learning
            key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
            if 'return' in key:
                pass
            win0.flip()
            parallel.setData(0)
        # create imagination and view trial such that no more than 2 trials in a row are img or view
        conditionsList = np.repeat("view",12)
        conditionsList= np.array([conditionsList,np.repeat("img",12)]).flatten()
        # create loss for imagination and view trials separately.
        if "comb" in task:
            outcome_view_tmp = []
            outcome_img_tmp = []
            loss_array_view_tmp = []
            loss_array_img_tmp = []
            loss_array_view = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view-1,
                loss_Mu+loss_SD_view,loss_Mu-loss_SD_view-1,
                loss_Mu-loss_SD_view+1,loss_Mu-loss_SD_view])
            loss_array_img = np.array([loss_Mu + loss_SD_img+1,loss_Mu+loss_SD_img-1,
                loss_Mu + loss_SD_img,loss_Mu-loss_SD_img-1,
                loss_Mu - loss_SD_img-1,loss_Mu-loss_SD_img])
            for i in range(2):
                randomize_view = np.arange(len(loss_array_view))
                randomize_img = np.arange(len(loss_array_img))
                np.random.shuffle(randomize_view)
                np.random.shuffle(randomize_img)
                if coin_heads[i]==1:
                    outcome_view = np.array([0,0,0,1,1,1])
                    outcome_img = np.array([0,0,0,1,1,1])
                else:
                    outcome_view = np.array([1,1,1,0,0,0])
                    outcome_img = np.array([1,1,1,0,0,0])
                outcome_view = outcome_view[randomize_view]
                loss_array_view = loss_array_view[randomize_view]
                outcome_img = outcome_img[randomize_img]
                loss_array_img = loss_array_img[randomize_img]
                outcome_view_tmp = [outcome_view_tmp,outcome_view]
                outcome_img_tmp = [outcome_img_tmp,outcome_img]
                loss_array_view_tmp = [loss_array_view_tmp,loss_array_view]
                loss_array_img_tmp  = [loss_array_img_tmp,loss_array_img]
            outcome = [outcome_view_tmp,outcome_img_tmp]
            loss_array = [loss_array_view_tmp,loss_array_img_tmp]
            print(np.array(outcome).flatten())
            print(loss_array)
        for j in range(len(outcome)):
            block_array.append(phase)
            trial_no.append(i)
            sub_id_array.append(sub_id)
            date_value_array.append(date_val)
            time_value_array.append(datetime.now().strftime("%H%M%S"))
            final_coin_side_1_array.append(coin_side_1[stim_coin[i]])
            final_coin_side_2_array.append(coin_side_2[stim_coin[i]])
            final_Mu_array.append(Mu[stim_generate[i]])
            final_SD_array.append(SD[stim_generate[i]])
            final_head_array.append(coin_heads[i])
            final_outcome_array.append(outcome[j])
            final_task_array.append(task)
            print("Current Trial is: %d" %(i))
            print("Current heads is: %d" %(coin_side_1[i]))
            print("Current outcome is: %d" %(outcome[j]))
            print("Current loss is: %d" %(loss_array[j]))
            print("Current condition is:" +test_task_comb[j])
            # print("Current Text is: %d" %(text_array[i]))
            fixation_cross()
            # flip window onto the screen
            win0.flip()
            parallel.setData(2) # fixation
            core.wait(0.2)
            parallel.setData(0)
            time_fixation = np.random.randint(500,1000)/1000
            # wait 1 sec
            core.wait(time_fixation-0.2)
            win0.flip()
            final_fix_time_array.append(time_fixation)

            if "view" in task:
                text_view = visual.TextStim(win0,text="על מנת לצפות בתוצאה האמיתית של המטבע, לחץ/י SPACE" ,
                                             pos=(0,-300),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center",languageStyle='RTL')
            # draw the text onto the window
                text_view.draw()
            # draw both coin sides onto the screen
                image_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]])
            # flip window onto screen
                win0.flip()
                parallel.setData(3) # view trial
                start_time = clock.getTime()
                key = event.waitKeys(maxWait = 9999,keyList = ["space"],clearEvents = True)
                if 'space' in key:
                    sub_response_array.append(6666)
                    stop_time = clock.getTime()
                    response_latency.append(round(stop_time-start_time,4)*1000)
                    pass
                win0.flip()
                parallel.setData(0)
                time_stim = np.random.randint(250,400)/1000
                core.wait(time_stim)
                coin_flip = flip_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]],outcome[j])
                coin_flip.draw()
                win0.flip()
                parallel.setData(5) # view trial
                while  not coin_flip.isFinished:
                    coin_flip.draw()
                    win0.flip()
                parallel.setData(0)
                final_task_comb_array.append("view")
            if "img" in task:
                line_1 ="\n בבקשה דמיין/י כאילו התוצאה המסומת בירוק היא התוצאה של ההטלה\n"
                line_2 = "\nלחץ/י SPACE להמשיך\n"
                text_info_start = visual.TextStim(win0,text=line_1+line_2,
				     		        pos=(0,-300),color = (1,1,1),
                            		units = "pix", height = 32,wrapWidth=1500,
                            		alignText = "center",languageStyle='RTL')
            # draw the text onto the window
                text_info_start.draw()
                if outcome[j]==0:
                    outcome_circle = visual.Circle(win = win0, lineColor = "green",edges = 180,
                                                    lineWidth = 30,
                                                     radius = 220,units = "pix",opacity = .8,
                                                    pos = (-270,0))
                    outcome_circle.draw()
                else:
                    outcome_circle = visual.Circle(win = win0, lineColor = "green",edges = 180,
                                                    lineWidth = 30,
                                                     radius = 220,units = "pix",opacity = .8,
                                                    pos = (270,0))
                    outcome_circle.draw()

            # draw both coin sides onto the screen
                image_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]])
            # flip window onto screen
                win0.flip()
                parallel.setData(4) # view trial
                start_time = clock.getTime()
                key = event.waitKeys(maxWait = 9999,keyList = ["space"],clearEvents = True)
                if 'space' in key:
                    sub_response_array.append(6666)
                    stop_time = clock.getTime()
                    response_latency.append(round(stop_time-start_time,4)*1000)
                    pass
                win0.flip()
                parallel.setData(0)
                coin_flip = visual.VlcMovieStim(win = win0,
                                                   filename = "data/coin000000.avi",
                                                   units = "pix",
                                                   pos = (0,0),
                                                   autoStart=True)
                coin_flip.draw()
                win0.flip()
                parallel.setData(5) #show video
                while  not coin_flip.isFinished:
                    coin_flip.draw()
                    win0.flip()
                final_task_comb_array.append("img")
                parallel.setData(0)
            if "comb" in task:
                if test_task_comb[j] =="img":
                    line_1 ="\n בבקשה דמיין/י כאילו התוצאה המסומת בירוק היא התוצאה של ההטלה\n"
                    line_2 = "\nלחץ/י SPACE להמשיך\n"
                    text_view = visual.TextStim(win0,text=line_1+line_2,
				     		        pos=(0,-300),color = (1,1,1),
                            		units = "pix", height = 32,wrapWidth=1500,
                            		alignText = "center",languageStyle='RTL')
                # draw the text onto the window
                    if outcome[j]==0:
                        outcome_circle = visual.Circle(win = win0, lineColor = "green",edges = 180,
                                                        lineWidth = 30,
                                                        radius = 220,units = "pix",opacity = .8,
                                                        pos = (-270,0))
                        outcome_circle.draw()
                    else:
                        outcome_circle = visual.Circle(win = win0, lineColor = "green",edges = 180,
                                                        lineWidth = 30,
                                                        radius = 220,units = "pix",opacity = .8,
                                                        pos = (270,0))
                        outcome_circle.draw()
                if test_task_comb[j] == "view":
                    text_view = visual.TextStim(win0,text="על מנת לצפות בתוצאה האמיתית של המטבע, לחץ/י SPACE",
                                                pos=(0,-300),color = (1,1,1),
                                                units = "pix", height = 32,wrapWidth=1500,
                                                alignText = "center",languageStyle='RTL')

            # draw the text onto the window
                text_view.draw()
            # draw both coin sides onto the screen
                image_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]])
            # flip window onto screen
                win0.flip()
                if test_task_comb[j] =="img":
                    parallel.setData(3)
                else:
                    parallel.setData(4)
                start_time = clock.getTime()
                key = event.waitKeys(maxWait = 9999,keyList = ["space"],clearEvents = True)
                if 'space' in key:
                    sub_response_array.append(6666)
                    stop_time = clock.getTime()
                    response_latency.append(round(stop_time-start_time,4)*1000)
                    pass
                parallel.setData(0)
                core.wait(.2)
                if test_task_comb[j] == "view":
                    coin_flip = flip_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]],outcome[j])
                else:
                    coin_flip = visual.VlcMovieStim(win = win0,
                                                       filename = "data/coin000000.avi",
                                                       units = "pix",
                                                       pos = (0,0),
                                                       autoStart=True)
                coin_flip.draw()
                win0.flip()
                parallel.setData(5)
                while  not coin_flip.isFinished:
                    coin_flip.draw()
                    win0.flip()
                parallel.setData(0)
                final_task_comb_array.append(test_task_comb[j])
            final_gamble_array.append("no")
            loss = loss_array[j]
            if outcome[j]==coin_heads[i]:
                outcome_stim_l, loss = outcome_stim_learn(loss,1)
            else:
                outcome_stim_l, loss = outcome_stim_learn(loss,0)
            outcome_stim_l.draw()
            final_loss_array.append(loss)
            win0.flip()
            parallel.setData(6) # show outcome learning
            core.wait(1.5)
            parallel.setData(0)
            # clear the Screen
            fixation_cross()
            win0.flip()
            parallel.setData(2)
            core.wait(.1)
            parallel.setData(0)
            core.wait(.1)
            final_estimation_mu.append("NA")
            final_estimation_rangelow.append("NA")
            final_estimation_range_high.append("NA")
            final_estimation_confidence_mu.append("NA")
            final_estimation_confidence_range.append("NA")
            final_use_imagery.append("NA")
            final_sure_option.append("NA")
        # gambling part:
        if use_imagery[i]==0 and "comb" in task:
            line_1 ="\n עכשיו, יש לך את ההזדמנות להשתמש במה שלמדת על תוצאות המטבע\n"
            line_2 = "\nאבל, התוצאות שהתקבלו בדמיון, אינם רלבנטיות להחלטה שלך\n"
            line_3 = "\nלחץ/י ENTER להמשיך\n"
            text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
				     		        pos=(0,0),color = (1,1,1),
                             		units = "pix", height = 32,wrapWidth=1500,
                             		alignText = "center",languageStyle='RTL')
            pin = 12
        elif use_imagery[i]==1 and "comb" in task:
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
        parallel.setData(0)
        line_1 ="\nלחץ/י D אם את/ה רוצה להמר על תוצאות המטבע\n"
        line_2 = "\nאחרת, לחצ/י K אם את/ה מעדיפ/ה לקבל חצי מההפסד למטה\n"
        line_3 = "\nלחץ/י ENTER להמשיך\n"
        text_info_start = visual.TextStim(win0,text=line_1+line_2+line_3,
                             pos=(0,0),color = (1,1,1),
                            units = "pix", height = 32,wrapWidth=1500,
                            alignText = "center",languageStyle='RTL')
        text_info_start.draw()
        win0.flip()
        parallel.setData(pin)
        key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
        if 'return' in key:
            pass
        win0.flip()
        sure_options = np.array([loss_Mu+loss_SD_view+1,loss_Mu+loss_SD_view-1,
            loss_Mu+loss_SD_view,loss_Mu-loss_SD_view-1,
            loss_Mu-loss_SD_view+1,loss_Mu-loss_SD_view])
        if i==1: # for the one trial where there is only imagery
            sure_options = np.array([loss_Mu+loss_SD_img+1,loss_Mu+loss_SD_img-1,
                loss_Mu+loss_SD_img,loss_Mu-loss_SD_img-1,
                loss_Mu-loss_SD_img+1,loss_Mu-loss_SD_img])
        print("gamble")
        for l in range(5):
            np.random.shuffle(sure_options)
            for s in range(6):
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
                final_coin_side_1_array.append(coin_side_1[stim_coin[i]])
                final_coin_side_2_array.append(coin_side_2[stim_coin[i]])
                final_fix_time_array.append(time_fixation)
                trial_no.append(i)
                time_value_array.append(datetime.now().strftime("%H%M%S"))
                sub_id_array.append(sub_id)
                date_value_array.append(date_val)
                block_array.append(phase)
                final_Mu_array.append(Mu[stim_generate[i]])
                final_SD_array.append(SD[stim_generate[i]])
                final_head_array.append(coin_heads[i])
                final_outcome_array.append("NA")
                final_task_array.append(task)
                final_sure_option.append(sure_options[s])
                text_mu = visual.TextStim(win0,text=sure_options[s],
                                             pos=(200,-20),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center")
                text_half = visual.TextStim(win0,text="חצי",
                                             pos=(200,20),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center",languageStyle="RTL")
                # image_stim(coin_side_1[stim_coin[i]],coin_side_2[stim_coin[i]])
                text_coin = visual.TextStim(win0,text="מטבע",
                                             pos=(-200,0),color = (1,1,1),
                                             units = "pix", height = 32,wrapWidth=1500,
                                             alignText = "center",languageStyle="RTL")
                text_half.draw()
                text_coin.draw()
                text_mu.draw()
                win0.flip()
                parallel.setData(14)
                start_time = clock.getTime()
                core.wait(0.05)
                parallel.setData(0)
                key = event.waitKeys(clearEvents = True,keyList = ['q','d','k'],
                                         maxWait = 9999)
                if key is None:
                    print('did not press at all')
                    sub_response_array.append(999)
                    response_latency.append(1000)
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
                final_use_imagery.append(use_imagery[i])
                if gamble==1 and use_imagery[i]==0:
                    loss = outcome_stim_gamble(sure_options[s],loss_array_view,1)
                elif gamble==1 and use_imagery[i]==1:
                    loss = outcome_stim_gamble(sure_options[s],loss_array,1)
                elif gamble==0:
                    loss = outcome_stim_gamble(sure_options[s],loss_array,0)
                core.wait(0.05)
                parallel.setData(0)
                final_loss_array.append(loss)
                final_task_comb_array.append("NA")
                final_estimation_mu.append("NA")
                final_gamble_array.append("yes")
                final_estimation_rangelow.append("NA")
                final_estimation_range_high.append("NA")
                final_estimation_confidence_mu.append("NA")
                final_estimation_confidence_range.append("NA")
                final_use_imagery.append("NA")
        Value_Mu, text_mu = Value_slider_mu()
        continueRoutine = True
        parallel.setData(15)
        while continueRoutine:
            Value_Mu.draw()
            text_mu.draw()
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
            win0.flip()
            keys = event.getKeys()
            if 'space' in keys:
                if Value_conf.getRating() is not None:
                    continueRoutine = False
        parallel.setData(0)
        final_estimation_confidence_range.append(Value_conf.getRating())
        block_array.append(phase)
        trial_no.append(i)
        sub_id_array.append(sub_id)
        sub_response_array.append("NA")
        response_latency.append("NA")
        date_value_array.append(date_val)
        time_value_array.append(datetime.now().strftime("%H%M%S"))
        final_coin_side_1_array.append(coin_side_1[stim_coin[i]])
        final_coin_side_2_array.append(coin_side_2[stim_coin[i]])
        final_Mu_array.append(Mu[stim_generate[i]])
        final_SD_array.append(SD[stim_generate[i]])
        final_head_array.append(coin_heads[i])
        final_outcome_array.append(outcome[j])
        final_task_comb_array.append("NA")
        final_task_array.append(task)
        final_gamble_array.append("no")
        final_loss_array.append("NA")
        final_use_imagery.append("NA")
        final_fix_time_array.append("NA")
        final_sure_option.append("NA")
        if break_flag==1:
            break
'''
print(len(trial_no))
print(len(time_value_array))
print(len(sub_id_array))
print(len(date_value_array))
print(len(final_fix_time_array))
print(len(sub_response_array))
print(len(final_coin_side_1_array))
print(len(final_coin_side_2_array))
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
                            'sure_option':final_sure_option})

# create the save file path

# save the file
output_file.to_csv(save_file_name,sep = ",",index=False)
# tidy up our resorces
win0.close()
print("OK, program has now closed")
