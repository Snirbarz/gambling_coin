'''
Stimuli: all presented at 80cm away from the screen
    fixation: black cross 10.1 d VA
              thickness will be 0.1 degress VA =
              500-1000ms (core.wait(1000),time.sleep(1))
    Stimulus: 8 images, 8 texts idenyifying the image
              text appear for 250-400 ms
              images appear for max 1000ms
              image at the center of the screen (size unknown)
              white backgroud (rgb --> 1,1,1)
              elvers.us/perception/visualAngleVA = figure out how to convert to cm and then pixels
              36 VA = (30.5425 cm) 1112 == 0

              calculate pixel density:
              vertical line - rgb(-1,-1,-1)
             Thickness of lines
              0.1 degrees VA


    Mask:     300ms (core.wait(300ms), win.flip())
              grey circle

    Response: keyboard --> 'd' is for match (also left button)
                           'k' is for non match (also right button)
    Task:
            80% trials ==> The image was correctly preceded by the identifying text
            20% of trials ==> The image was incorrectly preceded by a different text
    Experimental Session:
            at least 25 correct identification for each image
            Random order
    Triggers:
            fixation start
            word start
            mask start
            image start
            response type
            feedback start

    Monitor specification
            Screen Width = 37.632cm
            Screen Height = 30.106cm
            # Pixels wide = 1280 X 1024
            pixel_density_x (num_pixels per cm) = 1280/37.632 =34.02
    ParallelPort = 0x3EFC

            2- match fixation 00000001
            3- nonmatch fixation 00000010
            4- word 00000100
            5- mask 00001000
            6- image 00010000
            7- responsematch 00100000
            8- responsenonmatch 01000000
            10- feedback 10000001
            9- starttask 10000000
'''
# import some help
import os
# Clear the command output
from psychopy import logging, visual, core, event, clock, gui
from datetime  import datetime
from psychopy import parallel
import numpy as np
import pandas as pd

# set parallel port address
parallel.setPortAddress(0x3EFC)
parallel.setData(0)
date_val = datetime.now().strftime("%Y-%m-%d")

# we want to setup our experiment: sub_id, sub_gender, sub_age

my_Dlg = gui.Dlg(title = "word image matching task")
my_Dlg.addText("Subject info")
my_Dlg.addField("Exp Date",date_val)
my_Dlg.addField("ID","")

show_dlg = my_Dlg.show()
if my_Dlg.OK:
    print(show_dlg)
    # set up our save file date_sub_id_linetask.csv
    save_file_name = show_dlg[0]+"_"+show_dlg[1]+'_exposure_task.csv'
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


cur_time = datetime.now().strftime('%H%M%S')
# shuffle our stimulus presentation order
# declared and variables
no_trials = [0,0,0,0,0,0,0,0] # we will count each time participant was correct until we reach 25 correct responses for each image
correct_threshold = 25 # needs to change to 25 in the end !!!!!!!!!
image_array = [0,1,2,3,4,5,6,7]
max_trial_blocks = 100
total_num_trials = max_trial_blocks*8

cur_time_array = []
trial_no = []
sub_id_array = []
date_value_array=[]
sub_response_array=[] # subject reponse "left or right"
response_latency=[] # suject response latency
time_value_array =[]
block_array=[] # there is no block
final_image_array = []
final_text_array= []
final_match_array = []
final_fix_time_array = []
final_text_time_array = []
exp_task = ['training',"main"]
# Subject ID:
sub_id = show_dlg[1]

# create stim image array
stim_image = []
for n in range(max_trial_blocks):
    new_image_array = np.random.permutation(image_array)
    stim_image.append(new_image_array[0:8])
    cur_time_array.append(np.repeat(datetime.now().strftime('%H%M%S'),8))
stim_image = np.array(stim_image).flatten()
cur_time_array = np.array(cur_time_array).flatten()


# create match binary array
match_array = []

for n in range(total_num_trials):
    if n<160:
        match_array.append(0) # non matched
    if n>=160:
        match_array.append(1) # matched
match_array = np.random.permutation(match_array)

# create text array
text_array = []

for n in range(total_num_trials):
    if match_array[n]== 1:
        text_array.append(stim_image[n])
    if match_array[n]== 0:
        tmp_array = [0,1,2,3,4,5,6,7]
        tmp_array = list(filter(lambda a: a != stim_image[n], tmp_array))
        tmp_array = np.random.permutation(tmp_array)
        text_array.append(tmp_array[0])




logging.console.setLevel(logging.CRITICAL)
print("*************************************")
print("PSYCHOPY LOGGING set to : CRITICAL")
print(datetime.now())
print("Exposure TASK: version alpha")
print("*************************************")





# create the window object
win0 = visual.Window(size = (1280,1024),
                     units = "pix",
                     colorSpace = "rgb1",
                     color = (.6,.6,.6),
                     screen = 2,
                     monitor = 'testMonitor',
                     fullscr = True,
                     allowGUI = True
                     )

# 'wait for subjects to press enter when ready'
text_info = visual.TextStim(win0,text="לחץ/י ENTER בכדי להמשיך",
                             pos=(0,0),color = (-1,-1,-1),
                             units = "pix", height = 32,
                             alignHoriz = "center",languageStyle='RTL')

text_info.draw()
win0.flip()
key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()
# enter trigger here (start experiment)
# create our fixation cross
def fixation_cross():
    '''
    We will create out fixation_cross
    '''
    fix_cross_horiz = visual.Rect(win = win0,
                                       width = 12,
                                       units = "pix",
                                       height = 1,
                                       lineColor = [-1,-1,-1],
                                       fillColor = [-1,-1,-1],
                                       pos = (0,0))
    fix_cross_vert = visual.Rect(win = win0,
                                       width = 1,
                                       units = "pix",
                                       height = 12,
                                       lineColor = [-1,-1,-1],
                                       fillColor = [-1,-1,-1],
                                       pos = (0,0))

    fix_cross_horiz.draw() # this will draw the horizontal bit onto the window
    fix_cross_vert.draw() # this will draw the vertical bit onto the window

def image_stim(image_type):
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
    image_stim_name = ["data/Stim01.png","data/Stim02.png",
                       "data/Stim03.png","data/Stim04.png",
                       "data/Stim05.png","data/Stim06.png",
                       "data/Stim07.png","data/Stim08.png"
    ]
    image = visual.ImageStim(win = win0,
                                       image = image_stim_name[image_type],
                                       units = "pix",
                                       pos = (0,0))
    image.draw()# this will draw the image onto the window

def text_stim(text_type):
    '''
    We are preparing our Stimulus
    text_type == 0, Word01.png "frog"
    text_type == 1, Word02.png "face"
    text_type == 2, Word03.png "sign"
    text_type == 3, Word04.png "tomato"
    text_type == 4, Word05.png "hand"
    text_type == 5, Word06.png "pond"
    text_type == 6, Word07.png "wrench"
    text_type == 7, Word08.png "house"
    '''
    text_stim_name = [ "data/Word01.png","data/Word02.png",
                       "data/Word03.png","data/Word04.png",
                       "data/Word05.png","data/Word06.png",
                       "data/Word07.png","data/Word08.png"
    ]
    text = visual.ImageStim(win = win0,
                                       image = text_stim_name[text_type],
                                       units = "pix",
                                       pos = (0,0))
    text.draw()# this will draw the image onto the window

def masker_stim():
    '''
    We are creating our mask
    '''
    mask = visual.ImageStim(win = win0,
                                       image = "data/Circle.png",
                                       units = "pix",
                                       pos = (0,0))
    mask.draw()

def feedback_stim(response,match):
    '''
    We are creating our feedback stim
    correct = fback01.png
    incorrect = fback02.png
    '''
    if (response == 1 and match == 1) or (response == 0 and match == 0): # correct
        feedback = visual.ImageStim(win = win0,
                                           image = "data/fback01.png",
                                           units = "pix",
                                           pos = (0,0))
    if (response == 1 and match == 0) or (response == 0 and match == 1): #incorrect
        feedback = visual.ImageStim(win = win0,
                                           image = "data/fback02.png",
                                           units = "pix",
                                           pos = (0,0))

    feedback.draw()
def failed_task():
    line_1 = "לצערנו, לא עברת את קריטריון ההכלה שלנו. /n"
    line_2 = "המחקר יסתיים עכשיו. /n"
    line_3 = "יש לקרוא לנסיין. /n"
    text_info = visual.TextStim(win0,text=line_1 + line_2 + line_3,
                                 pos=(0,0),color = (-1,-1,-1),
                                 units = "pix", height = 32,
                                 alignHoriz = "center",languageStyle = "RTL")
    text_info.draw()
# task start (set data 9)

# Our main program loop
break_flag=0
parallel.setData(9)
core.wait(0.1)
parallel.setData(0)
for b in range(1):

    # update the subject on what to do:
    line_1 = "\nלחץ/י D אם התמונה תואמת לתמונה המקדימה אותה\n"
    line_2 = "אחרת לחץ/י K"
    text_info = visual.TextStim(win0,text=line_1 + line_2,
                                 pos=(0,0),color = (-1,-1,-1),
                                 units = "pix", height = 32,wrapWidth=1500,
                                 alignHoriz = "center",languageStyle = "RTL")
    text_info_start = visual.TextStim(win0,text="לחץ/י כל מקש להתחיל" ,
                                 pos=(0,-200),color = (-1,-1,-1),
                                 units = "pix", height = 32,
                                 alignHoriz = "center",languageStyle = "RTL")
    text_info.draw()
    text_info_start.draw()
    win0.flip()
    # enter trigger here (instruction)
    event.waitKeys(maxWait = 9999)

    for i in range(0,total_num_trials): # remind us no_trial is 5. in Python the lower bound
    # is included but the upper bound doesnot
        # present the fixation cross
        block_array.append(b)
        trial_no.append(i)
        sub_id_array.append(sub_id)
        date_value_array.append(date_val)
        time_value_array.append(datetime.now().strftime("%H%M%S"))
        final_image_array.append(stim_image[i])
        final_text_array.append(text_array[i])
        final_match_array.append(match_array[i])
        print("Current Trial is: %d" %(i))
        print("Current image is: %d" %(stim_image[i]))
        print("Current Text is: %d" %(text_array[i]))
        fixation_cross()
        # flip window onto the screen

        win0.flip()
        if match_array[i]==1:
            parallel.setData(2)
        else:
            parallel.setData(3)
        time_fixation = np.random.randint(500,1000)/1000
        # enter trigger here (fixation)
        # wait 1 sec
        core.wait(0.02)
        parallel.setData(0)
        core.wait(time_fixation-0.02)
        win0.flip()
        final_fix_time_array.append(time_fixation)
        # draw the text onto the window
        text_stim(text_array[i])
        # flip window onto screen
        win0.flip()
        parallel.setData(4)
        time_text = np.random.randint(250,400)/1000
        core.wait(0.02)
        parallel.setData(0)
        core.wait(time_text-0.02)
        final_text_time_array.append(time_text)
        # draw the mask onto the window
        masker_stim()
        # flip window onto screen
        win0.flip()
        parallel.setData(5)
        core.wait(0.02)
        parallel.setData(0)
        core.wait(.28)

        # draw the image onto the window
        image_stim(stim_image[i])
        # flip window onto screen
        win0.flip()
        parallel.setData(6)
        start_time = clock.getTime()
        core.wait(.02)
        parallel.setData(0)
        # clear the Screen
        key = event.waitKeys(clearEvents = True,keyList = ['q','d','k'],
                             maxWait = .98)

        if key is None:
            feedback_stim(1,0)
            print('did not press at all')
            sub_response_array.append(999)
            response_latency.append(1000)
            print(response_latency[i])
            win0.flip()
            parallel.setData(0)
            core.wait(.2)
        else:
            if 'd' in key: # d is for match
                parallel.setData(7)
                print('pressed match')
                sub_response_array.append(1)
                stop_time = clock.getTime()
                response_latency.append(round(stop_time-start_time,4)*1000)
                print(response_latency[i])
            if 'k' in key: # j is for non match
                parallel.setData(8)
                print('pressed non match')
                sub_response_array.append(0)
                stop_time = clock.getTime()
                response_latency.append(round(stop_time-start_time,4)*1000)
                print(response_latency[i])
            if 'q' in key:
                sub_response_array.append(9999)
                stop_time = clock.getTime()
                response_latency.append(round(stop_time-start_time,4)*1000)
                print(response_latency[i])
                break_flag = 1
                break

            feedback_stim(sub_response_array[i],match_array[i])

            win0.flip()
            parallel.setData(0)
            core.wait(.2)
            if match_array[i] == 1 and sub_response_array[i] == 1:
                no_trials[stim_image[i]] = no_trials[stim_image[i]] +1
                print(no_trials)
        reached_criterion = len(list(filter(lambda x: x < correct_threshold, no_trials))) > 0
        print(no_trials)

        if reached_criterion == False:
             break_flag = 1
             break

    if break_flag==1:
        break

if  reached_criterion == True:
    win0.flip()
    failed_task()
    win0.flip()
    key = event.waitKeys(clearEvents = True,keyList = ['q'],
                         maxWait = 99999999)
    win0.flip()
'''
print(trial_no)
print(time_value_array)
print(sub_id_array)
print(date_value_array)
print(final_text_array)
print(sub_response_array)
print(final_image_array)
print(response_latency)
print(block_array)
'''
# create a data frame:
output_file = pd.DataFrame({'trial':trial_no,
                            'time': time_value_array,
                            'id':sub_id_array,
                            'Date':date_value_array,
                            'text_stim':final_text_array,
                            'text_time':final_text_time_array,
                            'fix_time':final_fix_time_array,
                            'match_array':final_match_array,
                            'response':sub_response_array,
                            'image_stim':final_image_array,
                            'latency':response_latency,
                            'Block':block_array})

# create the save file path


# save the file
output_file.to_csv(save_file_name,sep = ",",index=False)

# tidy up our resorces
win0.close()
print("OK, program has now closed")
