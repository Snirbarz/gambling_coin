'''
Stimuli: all presented at 47cm away from the screen
    fixation: black cross 10.1 d VA
              thickness will be 0.1 degress VA =
              1000ms (core.wait(1000),time.sleep(1))
    Stimulus: 180 ms (core.wait(180))
              black horizontel line transected or bisected (rgb --> (-1,-1,-1))
              white backgroud (rgb --> 1,1,1)
              5 lengths
              elvers.us/perception/visualAngleVA = figure out how to convert to cm and then pixels
              36 VA = (30.5425 cm) 1112 == 0
              37 VA = (31.4520 cm) 1148 == 1
              38 VA = 1178 == 2
              39 VA =  1212 == 3
              40 VA =  1248 == 4
              calculate pixel density:
              vertical line - rgb(-1,-1,-1)
              2.20 VA =
              Thickness of lines
              0.1 degrees VA

              vert_offset = 1 degree VA

              The horizontal line change and the vertical always in midline

    Mask:     1000ms (core.wait(1000ms), win.flip())
              Bubble Mask
                    comprise multiple randomly placed overlapping circles of
                    different radii and colors.
                    Cover the all stimulus with this mask.
    Response: keyboard --> 'f' is for left side
                           'j' is for right side
    Task:
            Half trials ==> which side is longer? (left or right)
            Half of trials ==> which side is shorter (left or right)
    Experimental Session:
            4 Blocks of 40 trials --> two blocks are short and 2 are longer counterbalanced (7min)
                        10 were bisected = 0
                        15 were left-elongated = 1
                        15 were right elongated = 2
            Random order
    Monitor specification
            Screen Width = 29.376cm
            Screen Height = 16.524cm
            # Pixels wide = 1920 X 1080
            pixel_density_x (num_pixels per cm) = 1920/52.7





'''
# import some help
import os
# Clear the command output
from psychopy import logging, visual, core, event, clock, gui
from datetime  import datetime
import numpy as np
import pandas as pd

date_val = datetime.now().strftime("%Y-%m-%d")

# we want to setup our experiment: sub_id, sub_gender, sub_age

my_Dlg = gui.Dlg(title = "Line Bisection Task (version:alpha)")
my_Dlg.addText("Subject info")
my_Dlg.addField("Exp Date",date_val)
my_Dlg.addField("ID","")
my_Dlg.addField('Gender',choices = ['Male','Female','Prefer not to say'])
my_Dlg.addField("Age:","")

show_dlg = my_Dlg.show()
if my_Dlg.OK:
    print(show_dlg)
    # set up our save file date_sub_id_linetask.csv
    save_file_name = show_dlg[0]+"_"+show_dlg[1]+'_linetask.csv'
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
no_trials = 4
cur_time_array = []
trial_no = []
sub_id_array = []
date_value_array=[]
sub_response_array=[]
response_latency=[]
time_value_array =[]
block_array=[]
final_stim_side_array = []
final_stim_length_array= []
exp_task = ['shorter',"longer","shorter","longer"]
# Subject ID:
sub_id = show_dlg[1]
# create stim side array
stim_side = []
for n in range(no_trials):
    if n<15:
        stim_side.append(2)
        cur_time_array.append(datetime.now().strftime('%H%M%S'))

    if n>=15 and n<30:
        stim_side.append(1)
        cur_time_array.append(datetime.now().strftime('%H%M%S'))

    if n>=30:
        stim_side.append(0)
        cur_time_array.append(datetime.now().strftime('%H%M%S'))
# create line length array
line_length = []

for n in range(no_trials):
    if n<8:
        line_length.append(1112)
    if n>=8 and n<16:
        line_length.append(1148)
    if n>=16 and n<24:
        line_length.append(1178)
    if n>=24 and n<32:
        line_length.append(1212)
    if n>=32:
        line_length.append(1248)

logging.console.setLevel(logging.CRITICAL)
print("*************************************")
print("PSYCHOPY LOGGING set to : CRITICAL")
print(datetime.now())
print("LINE BISECTION TASK: version beta")
print("*************************************")





# create the window object
win0 = visual.Window(size = (600,600),
                     units = "pix",
                     color = (1,1,1),
                     screen = 2,
                     monitor = 'testMonitor',
                     fullscr = True,
                     allowGUI = True
                     )

# 'wait for subjects to press enter when ready'
text_info = visual.TextStim(win0,text="Press Enter to continue",
                             pos=(0,0),color = (-1,-1,-1),
                             units = "pix", height = 32,
                             alignHoriz = "right")

text_info.draw()
win0.flip()
key = event.waitKeys(maxWait = 9999,keyList = ["return"],clearEvents = True)
if 'return' in key:
    pass
win0.flip()
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

    fix_cross_horiz.draw()# this will draw the horizontal bit onto the window
    fix_cross_vert.draw()

def bisect_stim(line_length,long_side):
    '''
    We are creating our Stimulus
    long_side == 0, bisected L==R
    long_side == 1, left_longer = L>R -30pix left
    long_side == 2, right longer L<R 30pix right
    '''

    if long_side ==0: # we need a bisected line
        bisec_cross_horiz = visual.Rect(win = win0,
                                       width = line_length,
                                       units = "pix",
                                       height = 3,
                                       lineColor = [-1,-1,-1],
                                       fillColor = [-1,-1,-1],
                                       pos = (0,0))

    if long_side == 1:
        bisec_cross_horiz = visual.Rect(win = win0,
                                           width = line_length,
                                           units = "pix",
                                           height = 3,
                                           lineColor = [-1,-1,-1],
                                           fillColor = [-1,-1,-1],
                                           pos = (-30,0))
    if long_side == 2:
        bisec_cross_horiz = visual.Rect(win = win0,
                                           width = line_length,
                                           units = "pix",
                                           height = 3,
                                           lineColor = [-1,-1,-1],
                                           fillColor = [-1,-1,-1],
                                           pos = (30,0))
    bisec_cross_vert = visual.Rect(win = win0,
                                      width = 3,
                                      units = "pix",
                                      height = 66,
                                      lineColor = [-1,-1,-1],
                                      fillColor = [-1,-1,-1],
                                      pos = (0,0))

    bisec_cross_horiz.draw()# this will draw the horizontal bit onto the window
    bisec_cross_vert.draw()
def masker_stim():
    '''
    We are creating our mask
    '''
    big_black_circ = visual.DotStim(win0,units = "pix",
                                    nDots = 500,
                                    coherence = 0,
                                    fieldPos= (0,0),
                                    fieldSize=(1920,1920),
                                    fieldShape = 'sqr',
                                    dotSize = 120,
                                    speed = 0,
                                    color = [-1,-1,-1])

    big_gray_circ = visual.DotStim(win0,units = "pix",
                                    nDots = 500,
                                    coherence = 0,
                                    fieldPos= (0,0),
                                    fieldSize=(1920,1920),
                                    fieldShape = 'sqr',
                                    dotSize = 120,
                                    speed = 0,
                                    color = [0,0,0])
    big_white_circ = visual.DotStim(win0,units = "pix",
                                    nDots = 500,
                                    coherence = 1,
                                    fieldPos= (0,0),
                                    fieldSize=(1920,1920),
                                    fieldShape = 'sqr',
                                    dotSize = 120,
                                    speed = 0,
                                    color = [.75,.75,.75])
    small_black_circ = visual.DotStim(win0,units = "pix",
                                    nDots = 100,
                                    coherence = 0,
                                    fieldPos= (0,0),
                                    fieldSize=(1920,1920),
                                    fieldShape = 'sqr',
                                    dotSize = 20,
                                    speed = 0,
                                    color = [-1,-1,-1]
                                    )
    small_gray_circ = visual.DotStim(win0,units = "pix",
                                    nDots = 100,
                                    coherence = 0,
                                    fieldPos= (0,0),
                                    fieldSize=(1920,1920),
                                    fieldShape = 'sqr',
                                    dotSize = 20,
                                    speed = 0,
                                    color = [0,0,0])
    small_white_circ = visual.DotStim(win0,units = "pix",
                                    nDots = 100,
                                    coherence = 0,
                                    fieldPos= (0,0),
                                    fieldSize=(1920,1920),
                                    fieldShape = 'sqr',
                                    dotSize = 20,
                                    speed = 0,
                                    color = [.75,0.75,0.75])
    upper_white_rect = visual.Rect(win0,width = 1920, height = 600,
                                    units = "pix",
                                    fillColor = [1,1,1],
                                    lineColor = [1,1,1],
                                    pos = (0,350),
                                    )
    lower_white_rect = visual.Rect(win0,width = 1920, height = 600,
                                    units = "pix",
                                    fillColor = [1,1,1],
                                    lineColor = [1,1,1],
                                    pos = (0,-350),
                                    )
    big_black_circ.draw()
    big_gray_circ.draw()
    big_white_circ.draw()
    small_black_circ.draw()
    small_gray_circ.draw()
    small_white_circ.draw()
    upper_white_rect.draw()
    lower_white_rect.draw()
# Our main program loop
break_flag=0
for b in range(len(exp_task)):
    # create the block stim side:

    stim_side = []
    for n in range(no_trials):
        if n<15:
            stim_side.append(2)
            cur_time_array.append(datetime.now().strftime('%H%M%S'))

        if n>=15 and n<30:
            stim_side.append(1)
            cur_time_array.append(datetime.now().strftime('%H%M%S'))

        if n>=30:
            stim_side.append(0)
            cur_time_array.append(datetime.now().strftime('%H%M%S'))
    # shuffle the length and side arrays:
    np.random.shuffle(stim_side)

    np.random.shuffle(line_length)
    # update the subject on what to do:
    text_info = visual.TextStim(win0,text="Which side is " + str(exp_task[b]) +"?",
                                 pos=(0,0),color = (-1,-1,-1),
                                 units = "pix", height = 32,
                                 alignHoriz = "right")
    text_info_start = visual.TextStim(win0,text="Press any key to start " ,
                                 pos=(0,-200),color = (-1,-1,-1),
                                 units = "pix", height = 32,
                                 alignHoriz = "right")
    text_info.draw()
    text_info_start.draw()
    win0.flip()
    event.waitKeys(maxWait = 9999)

    for i in range(0,no_trials): # remind us no_trial is 5. in Python the lower bound
    # is included but the upper bound doesnot
        # present the fixation cross
        block_array.append(b)
        trial_no.append(i)
        sub_id_array.append(sub_id)
        date_value_array.append(date_val)
        time_value_array.append(datetime.now().strftime("%H%M%S"))
        final_stim_side_array.append(stim_side[i])
        final_stim_length_array.append(line_length[i])
        print("Current Trial is: %d" %(i))
        print("Current Side is: %d" %(stim_side[i]))
        print("Current Line Length is: %d" %(line_length[i]))
        fixation_cross()
        # flip window onto the screen
        win0.flip()
        # wait 1 sec
        core.wait(1)

        # draw our stimulus onto the window
        bisect_stim(line_length[i],stim_side[i])
        # flip window onto screen
        win0.flip()
        start_time = clock.getTime()
        core.wait(0.180)

        masker_stim()
        win0.flip()

        # clear the Screen
        key = event.waitKeys(clearEvents = True,keyList = ['q','f','j'],
                             maxWait = 600)
        if 'f' in key: # f is for left size
            print('left pressed...')
            sub_response_array.append(1)
            stop_time = clock.getTime()
            response_latency.append(round(stop_time-start_time,4)*1000)
            print(response_latency[i])
        if 'j' in key: # j is for left size
            print('right pressed...')
            sub_response_array.append(2)
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
    if break_flag==1:
        break

'''
print(trial_no)
print(time_value_array)
print(sub_id_array)
print(date_value_array)
print(final_stim_length_array)
print(sub_response_array)
print(final_stim_side_array)
print(response_latency)
print(block_array)
'''
# create a data frame:
output_file = pd.DataFrame({'trial':trial_no,
                            'time': time_value_array,
                            'id':sub_id_array,
                            'Date':date_value_array,
                            'line_length':final_stim_length_array,
                            'response':sub_response_array,
                            'Stim_side':final_stim_side_array,
                            'latency':response_latency,
                            'Block':block_array})

# create the save file path


# save the file
output_file.to_csv(save_file_name,sep = ",",index=False)

# tidy up our resorces
win0.close()
print("OK, program has now closed")
