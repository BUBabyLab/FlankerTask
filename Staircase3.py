"""measure your JND in orientation using a staircase method"""
from psychopy import core, visual, gui, data, event
from psychopy.tools.filetools import fromFile, toFile
import numpy, random

try:  # try to get a previous parameters file
    expInfo = fromFile('lastParams.pickle')
except:  # if not there then use a default set
    expInfo = {'observer':'jwp', 'refContrast':1}
expInfo['dateStr'] = data.getDateStr()  # add the current time
# present a dialogue to change params
dlg = gui.DlgFromDict(expInfo, title='Contrast Detection JND Exp', fixed=['dateStr'])
if dlg.OK:
    toFile('lastParams.pickle', expInfo)  # save params to file for next time
else:
    core.quit()  # the user hit cancel so exit

# make a text file to save data
fileName = expInfo['observer'] + expInfo['dateStr']
dataFile = open(fileName+'.csv', 'w')  # a simple text file with 'comma-separated-values'
dataFile.write('FlankerDist,trial,targetSide,oriIncrement,correct\n')

#  Parameters for Gabors
mySize = 128
#  0.03125 is 32 pixels per cyccle - lambda = 32
theSF = 0.03125
vOffset = 50

# create window and stimuli
win = visual.Window(size = [1440,900],allowGUI=True, fullscr= True,
                    monitor='testMonitor', units='pix')
                    

maskerTL = visual.GratingStim(win, tex='sin', sf=theSF, size=mySize, mask='gauss')
maskerTR = visual.GratingStim(win, tex='sin', sf=theSF, size=mySize, mask='gauss')
maskerBL = visual.GratingStim(win, tex='sin', sf=theSF, size=mySize, mask='gauss')
maskerBR = visual.GratingStim(win, tex='sin', sf=theSF, size=mySize, mask='gauss')
target = visual.GratingStim(win, tex='sin', sf=theSF, size=mySize, mask='gauss')
fixation = visual.GratingStim(win, color=-1, colorSpace='rgb',
                              tex=None, mask='circle', size=0.2)
                              
# and some handy clocks to keep track of time
globalClock = core.Clock()
trialClock = core.Clock()

# display instructions and wait
message1 = visual.TextStim(win, pos=[0,+vOffset],text='''
You will see two columns of patches
One will have 3, the other two
The middle of the 3 patches is the Target
Sit approximately one arm's length from the screen
Then press the left or right arrow to identify the target
Be ready!  They will flash quite briefly!
Hit a key when ready to start
''')
message2 = visual.TextStim(win, pos=[0,-vOffset], text="Hit a key when ready.")
message3 = visual.TextStim(win, pos=[0, -(vOffset*2)], text="Then press left or right to identify the target")
message1.draw()
#message2.draw()
#fixation.draw()
win.flip()#to show our newly drawn 'stimuli'
#pause until there's a keypress
event.waitKeys()

your_mouse = event.Mouse(visible = False)

##########################
## BLock 1 - lambda = 3
#########################
# All stimuli are vertical in first test
# Size in pixels!  vOffset is flanker dist
vOffset = 96
hOffset = 100

for trialLoop in range(2):
    formatString = 'Trial %i of 5.' %(trialLoop+1)
    messagetrial = visual.TextStim(win, pos=[0,+vOffset],text= formatString)
    messagetrial.draw()
    win.flip()
    event.waitKeys()
    
    staircase = data.StairHandler(startVal = 0.5,
                            #  Array as list alters the size of steps - do we want this?
                          nReversals = 4,
                          stepType = 'lin', stepSizes = [0.04,0.02,0.01,0.005],
                          minVal = 0, maxVal = 1,
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=10)
                          
    for thisIncrement in staircase:  # will continue the staircase until it terminates!
        # set location of stimuli
        targetSide= random.choice([-1,1])  # will be either +1(right) or -1(left)
        maskerTL.setPos([hOffset*targetSide, vOffset])
        maskerTL.setContrast(0.5)
        maskerTR.setPos([-hOffset*targetSide, vOffset])
        maskerTR.setContrast(0.5)
        maskerBL.setPos([hOffset*targetSide, -vOffset])
        maskerBL.setContrast(0.5)
        maskerBR.setPos([-hOffset*targetSide, -vOffset])
        maskerBR.setContrast(0.5)
        target.setPos([hOffset*targetSide, 0])  # in other location

        #  setContrast changes contrast!
        #  thisIncrement will be up or down depending upon thisResp
        target.setContrast(thisIncrement)

        # draw all stimuli
        maskerTL.draw()
        maskerTR.draw()
        maskerBL.draw()
        maskerBR.draw()
        target.draw()
        fixation.draw()
        win.flip()

        # wait 100ms; but use a loop of x frames for more accurate timing
        core.wait(0.1)

        # blank screen
        fixation.draw()
        win.flip()

        # get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                if thisKey=='left':
                    if targetSide==-1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey=='right':
                    if targetSide== 1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey in ['q', 'escape']:
                    core.quit()  # abort experiment
            event.clearEvents()  # clear other (eg mouse) events - they clog the buffer
    
        # add the data to the staircase so it can calculate the next level
        staircase.addData(thisResp)
        dataFile.write('3,%i,%i,%.3f,%i\n' %(trialLoop, targetSide, thisIncrement, thisResp))
        core.wait(1)

# give some output to user in the command line in the output window
print('reversals:')
print(staircase.reversalIntensities)
approxThreshold = numpy.average(staircase.reversalIntensities[-4:])
print('mean of final 4 reversals = %.3f' % (approxThreshold))

# give some on-screen feedback
feedback1 = visual.TextStim(
        win, pos=[0,+3],
        text='mean of final 6 reversals = %.3f' % (approxThreshold))

feedback1.draw()
fixation.draw()
win.flip()
event.waitKeys()  # wait for participant to respond

###########################
## Block 2 - lambda = 1.5
###########################
#  Lambda = 32; 1.5 lambda = 48
vOffset = 48

for trialLoop in range(2):
    formatString = 'Trial %i of 5.' %(trialLoop+1)
    messagetrial = visual.TextStim(win, pos=[0,+vOffset],text= formatString)
    messagetrial.draw()
    win.flip()
    event.waitKeys()
    
    # create the staircase handler for 2nd loop
    staircase2 = data.StairHandler(startVal = 0.5,
                        stepType = 'lin', stepSizes = [0.04,0.02,0.01,0.005],
                        #  This is the number of correct responses before stepping down 
                          #  (nDown) and incorrect for up (nUp)
                          nReversals = 4,
                          minVal = 0, maxVal = 1,
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=10)
                          
    for thisIncrement in staircase2:  # will continue the staircase until it terminates!
        # set location of stimuli
        targetSide= random.choice([-1,1])  # will be either +1(right) or -1(left)
        maskerTL.setPos([hOffset*targetSide, vOffset])
        maskerTL.setContrast(0.5)
        maskerTR.setPos([-hOffset*targetSide, vOffset])
        maskerTR.setContrast(0.5)
        maskerBL.setPos([hOffset*targetSide, -vOffset])
        maskerBL.setContrast(0.5)
        maskerBR.setPos([-hOffset*targetSide, -vOffset])
        maskerBR.setContrast(0.5)
        target.setPos([hOffset*targetSide, 0])  # in other location

        #  setContrast changes contrast!
        #  thisIncrement will be set to +1 or -1, depending on last trial
        #  Negative values decrease by 0.05, positive increase
        target.setContrast(thisIncrement)

        # draw all stimuli
        maskerTL.draw()
        maskerTR.draw()
        maskerBL.draw()
        maskerBR.draw()
        target.draw()
        fixation.draw()
        win.flip()

        # wait 100ms; but use a loop of x frames for more accurate timing
        core.wait(.1)

        # blank screen
        fixation.draw()
        win.flip()

        # get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                if thisKey=='left':
                    if targetSide==-1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey=='right':
                    if targetSide== 1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey in ['q', 'escape']:
                    core.quit()  # abort experiment
            event.clearEvents()  # clear other (eg mouse) events - they clog the buffer

        # add the data to the staircase so it can calculate the next level
        staircase2.addData(thisResp)
        dataFile.write('1.5,%i,%i,%.3f,%i\n' %(targetSide, trialLoop, thisIncrement, thisResp))
        core.wait(1)

#######################
## Block 3 - Lambda 6
#######################

#  Lambda = 32;1.5 lambda = 48
vOffset = 192

for trialLoop in range(2):
    formatString = 'Trial %i of 5.' %(trialLoop+1)
    messagetrial = visual.TextStim(win, pos=[0,+vOffset],text= formatString)
    messagetrial.draw()
    win.flip()
    event.waitKeys()
    
    # create the staircase handler for 2nd loop
    staircase2 = data.StairHandler(startVal = 0.5,
                        stepType = 'lin', stepSizes = [0.04,0.02,0.01,0.005],
                        #  This is the number of correct responses before stepping down 
                          #  (nDown) and incorrect for up (nUp)
                          nReversals = 4,
                          minVal = 0, maxVal = 1,
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=10)
                          
    for thisIncrement in staircase2:  # will continue the staircase until it terminates!
        # set location of stimuli
        targetSide= random.choice([-1,1])  # will be either +1(right) or -1(left)
        maskerTL.setPos([hOffset*targetSide, vOffset])
        maskerTL.setContrast(0.5)
        maskerTR.setPos([-hOffset*targetSide, vOffset])
        maskerTR.setContrast(0.5)
        maskerBL.setPos([hOffset*targetSide, -vOffset])
        maskerBL.setContrast(0.5)
        maskerBR.setPos([-hOffset*targetSide, -vOffset])
        maskerBR.setContrast(0.5)
        target.setPos([hOffset*targetSide, 0])  # in other location

        #  setContrast changes contrast!
        #  thisIncrement will be set to +1 or -1, depending on last trial
        #  Negative values decrease by 0.05, positive increase
        target.setContrast(thisIncrement)

        # draw all stimuli
        maskerTL.draw()
        maskerTR.draw()
        maskerBL.draw()
        maskerBR.draw()
        target.draw()
        fixation.draw()
        win.flip()

        # wait 100ms; but use a loop of x frames for more accurate timing
        core.wait(.1)

        # blank screen
        fixation.draw()
        win.flip()

        # get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                if thisKey=='left':
                    if targetSide==-1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey=='right':
                    if targetSide== 1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey in ['q', 'escape']:
                    core.quit()  # abort experiment
            event.clearEvents()  # clear other (eg mouse) events - they clog the buffer

        # add the data to the staircase so it can calculate the next level
        staircase2.addData(thisResp)
        dataFile.write('6,%i,%i,%.3f,%i\n' %(targetSide, trialLoop, thisIncrement, thisResp))
        core.wait(1)

##########################
## Block 4 - Lambda = 12
##########################

#  Lambda = 32;1.5 lambda = 48
vOffset = 384
#  THIS MAY NOT FIT!

for trialLoop in range(2):
    formatString = 'Trial %i of 5.' %(trialLoop+1)
    messagetrial = visual.TextStim(win, pos=[0,+vOffset],text= formatString)
    messagetrial.draw()
    win.flip()
    event.waitKeys()
    
    # create the staircase handler for 2nd loop
    staircase2 = data.StairHandler(startVal = 0.5,
                        stepType = 'lin', stepSizes = [0.04,0.02,0.01,0.005],
                        #  This is the number of correct responses before stepping down 
                          #  (nDown) and incorrect for up (nUp)
                          nReversals = 4,
                          minVal = 0, maxVal = 1,
                          nUp=1, nDown=3,  # will home in on the 80% threshold
                          nTrials=10)
                          
    for thisIncrement in staircase2:  # will continue the staircase until it terminates!
        # set location of stimuli
        targetSide= random.choice([-1,1])  # will be either +1(right) or -1(left)
        maskerTL.setPos([hOffset*targetSide, vOffset])
        maskerTL.setContrast(0.5)
        maskerTR.setPos([-hOffset*targetSide, vOffset])
        maskerTR.setContrast(0.5)
        maskerBL.setPos([hOffset*targetSide, -vOffset])
        maskerBL.setContrast(0.5)
        maskerBR.setPos([-hOffset*targetSide, -vOffset])
        maskerBR.setContrast(0.5)
        target.setPos([hOffset*targetSide, 0])  # in other location

        #  setContrast changes contrast!
        #  thisIncrement will be set to +1 or -1, depending on last trial
        #  Negative values decrease by 0.05, positive increase
        target.setContrast(thisIncrement)

        # draw all stimuli
        maskerTL.draw()
        maskerTR.draw()
        maskerBL.draw()
        maskerBR.draw()
        target.draw()
        fixation.draw()
        win.flip()

        # wait 100ms; but use a loop of x frames for more accurate timing
        core.wait(.1)

        # blank screen
        fixation.draw()
        win.flip()

        # get response
        thisResp=None
        while thisResp==None:
            allKeys=event.waitKeys()
            for thisKey in allKeys:
                if thisKey=='left':
                    if targetSide==-1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey=='right':
                    if targetSide== 1: thisResp = 1  # correct
                    else: thisResp = -1              # incorrect
                elif thisKey in ['q', 'escape']:
                    core.quit()  # abort experiment
            event.clearEvents()  # clear other (eg mouse) events - they clog the buffer

        # add the data to the staircase so it can calculate the next level
        staircase2.addData(thisResp)
        dataFile.write('12,%i,%i,%.3f,%i\n' %(targetSide, trialLoop, thisIncrement, thisResp))
        core.wait(1)

# staircase has ended
dataFile.close()
staircase.saveAsPickle(fileName)  # special python binary file to save all the info

# give some output to user in the command line in the output window
print('reversals:')
print(staircase.reversalIntensities)
approxThreshold = numpy.average(staircase.reversalIntensities[-4:])
print('mean of final 4 reversals = %.3f' % (approxThreshold))

# give some on-screen feedback
feedback1 = visual.TextStim(
        win, pos=[0,+3],
        text='mean of final 6 reversals = %.3f' % (approxThreshold))

feedback1.draw()
fixation.draw()
win.flip()
event.waitKeys()  # wait for participant to respond

win.close()
core.quit()