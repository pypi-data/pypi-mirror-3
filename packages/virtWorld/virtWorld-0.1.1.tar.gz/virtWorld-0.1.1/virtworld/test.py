import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import *
from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.ai import *
from direct.gui.OnscreenImage import OnscreenImage


bullets = []
bulletSpeed = 20.0
bulletLife = 5.0

def addImage(imagePath, x, z):
    return OnscreenImage(image = imagePath, pos = (x, 0, z))


class FPS(object,DirectObject):
    def __init__(self):
        self.loadLevel()
        self.initPlayer()
        base.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        #props.setFullscreen(True)
        base.win.requestProperties(props)
        
    def loadLevel(self):
        m = loader.loadModel("level.egg")
        m.reparentTo(render)
        camera.setPos(0, 0, 0)
    def initPlayer(self):
        self.node = Player()    
        
class Player(object):
        FORWARD = Vec3(0,2,0)
        BACK = Vec3(0,-1,0)
        LEFT = Vec3(-1,0,0)
        RIGHT = Vec3(1,0,0)
        STOP = Vec3(0)
        walk = STOP
        strafe = STOP
        speed = 50
        readyToJump = False
        jump = 0

        def __init__(self):
            self.loadModel()
            self.setUpCamera()
            self.attachControls()
            self.gun()
            self.initCollision()
            self.createCollisions()
            self.AIModels()
            self.setAI()
            self.rcreateCollisions()
            taskMgr.add(self.mouseUpdate, 'mouse-task')
            taskMgr.add(self.moveUpdate, 'move-task')
            taskMgr.add(self.jumpUpdate, 'jump-task')

        def initCollision(self):
            base.cTrav = CollisionTraverser()
            base.pusher = CollisionHandlerPusher()
            collisionHandler = CollisionHandlerQueue()
        def loadModel(self):

            self.node = NodePath('player')
            self.node.reparentTo(base.render)
            self.node.setPos(0,0,1)
            self.node.setScale(.05)
            
        def setUpCamera(self):
            pl =  base.cam.node().getLens()
            pl.setFov(70)   
            base.cam.node().setLens(pl)
            base.camera.reparentTo(self.node)   
            base.camera.setPos(0, 0, 2)    
            leftColor = ColorWriteAttrib.CRed
            rightColor = ColorWriteAttrib.CBlue
            base.win.setRedBlueStereo(True, leftColor, rightColor)
            oldDr = base.cam.node().getDisplayRegion(0)
            oldDr.setCamera(NodePath())
            dr = base.win.makeStereoDisplayRegion()
            dr.setCamera(base.cam)
            dr.getRightEye().setClearDepthActive(True)
            dr.setStereoChannel(Lens.SCStereo)
 
        def mouseUpdate(self,task):
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            if base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2):
                self.node.setH(self.node.getH() -  (x - base.win.getXSize()/2)*0.1)
                base.camera.setP(base.camera.getP() - (y - base.win.getYSize()/2)*0.1)
            global hpr
            hpr = self.node.getHpr()
            global pos
            pos = self.node.getPos() 
            return task.cont 
        def attachControls(self):
            #base.accept( "s" , self.__setattr__,["walk",self.STOP] )
            base.accept( "w" , self.__setattr__,["walk",self.FORWARD])
            base.accept( "s" , self.__setattr__,["walk",self.BACK] )
            base.accept( "s-up" , self.__setattr__,["walk",self.STOP] )
            base.accept( "w-up" , self.__setattr__,["walk",self.STOP] )
            base.accept( "a" , self.__setattr__,["strafe",self.LEFT])
            base.accept( "d" , self.__setattr__,["strafe",self.RIGHT] )
            base.accept( "a-up" , self.__setattr__,["strafe",self.STOP] )
            base.accept( "d-up" , self.__setattr__,["strafe",self.STOP] )
        def moveUpdate(self,task): 
            self.node.setPos(self.node,self.walk*globalClock.getDt()*self.speed)
            self.node.setPos(self.node,self.strafe*globalClock.getDt()*self.speed)
            return task.cont
        
        def createCollisions(self):
            traverser = CollisionTraverser('trav')
            base.cTrav = traverser
            cn = CollisionNode('player')
            cn.addSolid(CollisionSphere(0,0,0,3))
            solid = self.node.attachNewNode(cn)
            base.cTrav.addCollider(solid,base.pusher)
            base.pusher.addCollider(solid,self.node, base.drive.node())
            

            ray = CollisionRay()
            ray.setOrigin(0,0,-.2)
            cn = CollisionNode('playerRay')
            cn.addSolid(ray)
            cn.setFromCollideMask(BitMask32.bit(0))
            cn.setIntoCollideMask(BitMask32.allOff())
            solid = self.node.attachNewNode(cn)
            self.nodeGroundHandler = CollisionHandlerQueue()
            traverser.addCollider(solid, self.nodeGroundHandler)
            
        def jumpUpdate(self,task):

            highestZ = -100
            for i in range(self.nodeGroundHandler.getNumEntries()):
                entry = self.nodeGroundHandler.getEntry(i)
                z = entry.getSurfacePoint(render).getZ()
                if z > highestZ and entry.getIntoNode().getName() == "Cube":
                    highestZ = z
            
            self.node.setZ(self.node.getZ()+self.jump*globalClock.getDt())
            self.jump -= 1*globalClock.getDt()
            if highestZ > self.node.getZ()-.3:
                self.jump = 0
                self.node.setZ(highestZ+.3)
                if self.readyToJump:
                    self.jump = 1
            return task.cont
            
            
        def AIModels(self):

            ralphStartPos = Vec3(-4, -1, 0)
            self.wanderer = Actor("models/ralph",
                                    {"run":"models/ralph-run"})
            self.wanderer.reparentTo(render)
            self.wanderer.setScale(0.25)
            self.wanderer.setPos(ralphStartPos)
                
        def setAI(self):

            self.AIworld = AIWorld(render)
         
            self.AIchar = AICharacter("wanderer",self.wanderer, 100, 0.0005, 5)
            self.AIworld.addAiChar(self.AIchar)
            self.AIbehaviors = self.AIchar.getAiBehaviors()
                
            self.AIbehaviors.wander(2, 0, 10, 1.0)
            self.wanderer.loop("run")
                
       
            taskMgr.add(self.AIUpdate,"AIUpdate")
                
 
        def AIUpdate(self,task):
            self.AIworld.update()            
            return Task.cont
        def rcreateCollisions(self):
            
            cn = CollisionNode('panda')
            cn.addSolid(CollisionSphere(0,0,0,2))
            solid = self.wanderer.attachNewNode(cn)
            base.cTrav.addCollider(solid,base.pusher)
            base.pusher.addCollider(solid,self.wanderer, base.drive.node())

            ray = CollisionRay()
            ray.setOrigin(0,0,-.2)
            ray.setDirection(0,0,-1)
            cn = CollisionNode('pandaRay')
            cn.addSolid(ray)
            cn.setFromCollideMask(BitMask32.bit(0))
            cn.setIntoCollideMask(BitMask32.allOff())
            solid = self.wanderer.attachNewNode(cn)
            self.nodeGroundHandler = CollisionHandlerQueue()
            base.cTrav.addCollider(solid, self.nodeGroundHandler)
            
            
            
            
        def gun(self):
            self.ptr = self.node.attachNewNode('point')
            self.ptr = loader.loadModel('smiley')
            self.ptr.setScale(0.02)
            self.ptr.reparentTo(base.cam)
            self.ptr.setPos(0,2,0)
            
        
        class Bullet(object):
            model = loader.loadModel("frowney")
           
            def __init__(self, pos, hpr, speed, life):
                self.node = Player.Bullet.model.copyTo(render)
                self.node.setPosHpr(pos, hpr)
                self.speed = speed
                self.life = life
                self.alive = True
           
            def update(self, dt):
                if not self.alive:
                    return
               
                self.life -= dt
               
                if self.life > 0:
                    self.node.setFluidY(self.node, self.speed * dt)
                else:
                    self.node.removeNode()
                    self.alive = False

        def updateBullets(task):
            dt = globalClock.getDt()
           
            for bullet in bullets:
                bullet.update(dt)
           
            return task.cont

        def shoot():
            global bullets
            bullets = [b for b in bullets if b.alive]
            bullets.append( Player.Bullet(pos, hpr, bulletSpeed, bulletLife) )

        base.accept("space", shoot)
        taskMgr.add(updateBullets, "updateBullets")
        
        

FPS()
#render.setShaderAuto()
run()
