from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
from direct.task import Task
loadPrcFileData("", "load-file-type p3assimp")
from math import *
from direct.interval.IntervalGlobal import Sequence
import time
import os
import numpy as np
loadPrcFileData("", "win-size 1280 1024")
# ffmpeg -y -framerate 30 -f image2 -i frame_%04d.png -q:a 2 -q:v 4 -vcodec wmv2 -acodec wmav2 out.avi

class MyApp(ShowBase):
    def __init__(self):
        global i
        i = 0
        self.coin_side_1 = np.array([0,0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,3,3,3,3,4,4,4,5,5,6,8])
        self.coin_side_2 = np.array([1,2,3,4,5,6,7,2,3,4,5,6,7,3,4,5,6,7,4,5,6,7,5,6,7,6,7,7,9])
        ShowBase.__init__(self)
        self.model = self.loader.load_model("cointest1.obj")
        self.model.setScale(1, 1, 1)
        self.model.setPos(0, 0, 0)
        self.model.setHpr(self.model, 0,90,0)
        self.model.reparent_to(self.render)
        self.myInterval1 = self.model.hprInterval(2, Vec3(0,90,1080)) # change the first value in hprInterval to adjust the rotation time
        self.setBackgroundColor(0,0,0)
        # Add the spinCameraTask procedure to the task manager.
        self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
        self.taskMgr.add(self.update_texture,"update texture")


    def update_texture(self,task):
        global i
        self.side_1= str(self.coin_side_1[i]+1)
        self.side_2= str(self.coin_side_2[i]+1)
        texture = self.loader.loadTexture('coin0'+self.side_1+'0'+self.side_2+'.png')
        self.model.setTextureOff(1)
        self.model.setTexture(texture,1)
        rotateCoin = Sequence(self.myInterval1,name = "Rotate")
        rotateCoin.start()
        self.taskMgr.add(self.record,"record")
        i +=1

    def taskStop(task):
        base.graphicsEngine.removeAllWindows()
    def save(self,task):
        os.system("ffmpeg -y -framerate 30 -f image2 -i record/coin0"+self.side_1+'0'+self.side_2+'0'+self.side_1+"frame_%04d.png -q:v 1 -vcodec wmv2 coin0"+self.side_1+'0'+self.side_2+'0'+self.side_1+".avi")
        # Task.done
        # return Task.again
        # Define a procedure to move the camera.
    def record(self,task):
        base.movie(namePrefix='record/'+'coin0'+self.side_1+'0'+self.side_2+'0'+self.side_1+'frame', duration=3, fps=30, format='png')
        self.taskMgr.doMethodLater(3,self.save,"save_recording")
        self.taskMgr.doMethodLater(3, self.update_texture,"update texture")
    def spinCameraTask(self, task):
        angleDegrees = 0#task.time * 30.0
        angleRadians = angleDegrees * (pi / 180.0)
        self.camera.setPos(0, -10, 0)
        self.camera.setHpr(angleDegrees, 0, 0)
        return Task.cont

global side_1, side_2
app = MyApp()
app.run()
