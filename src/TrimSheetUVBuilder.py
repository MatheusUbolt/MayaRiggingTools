import maya.cmds as mc
import maya.mel as mel
from maya.OpenMaya import MVector
import maya.OpenMayaUI as omui
from PySide2.QtWidgets import QVBoxLayout, QWidget, QPushButton, QMainWindow, QHBoxLayout, QGridLayout, QLineEdit, QLabel, QSlider
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance

#copy/paste the following on the MEL Maya script Editor to connect VSC to Maya then Alt + Shift + M to run the code
#commandPort -n "localhost:7001" -stp "mel";

class TrimSheetBuilderWidget(QWidget):
    def __init__(self):
        mainWindow: QMainWindow = TrimSheetBuilderWidget.GetMayaMainWindow()

        for existing in mainWindow.findChildren(QWidget, TrimSheetBuilderWidget.GetWindowUniqueId()):
            existing.deleteLater()

        super().__init__(parent=mainWindow)
        
        self.setWindowTitle("Trim sheet Builder")
        self.setWindowFlags(Qt.Window)
        self.setObjectName(TrimSheetBuilderWidget.GetWindowUniqueId())
        
        self.shell = []

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        self.CreateInitializationSection()
        self.CreateManipulationSection()

    def FillShellToU1V1(self):
        width, height = self.GetShellSize()
        su = 1 / width
        sv = 1 / height
        self.ScaleShell(su, sv)
        self.MoveToOrigin()

    def GetShellSize(self):
        min, max = self.GetShellBound()
        height = max[1] - min[1]
        width = max [0] - min[0]

        return width, height


    def ScaleShell(self, u, v):
        mc.polyEditUV(self.shell, su = u, sv = v, r=True)

    def MoveShell(self, u, v):
        width, height = self.GetShellSize()
        uAmt = u * width
        vAmt = v * height
        mc.polyEditUV(self.shell, u = uAmt, v = vAmt)

    def CreateManipulationSection(self):
        sectionLayout = QVBoxLayout()
        self.masterLayout.addLayout(sectionLayout)
        turnBtn = QPushButton("Turn")
        turnBtn.clicked.connect(self.TurnShell)
        sectionLayout.addWidget(turnBtn)

        moveToOriginBtn = QPushButton("Move to Origin")
        moveToOriginBtn.clicked.connect(self.BackToOrigin)
        sectionLayout.addWidget(moveToOriginBtn)

        fillU1V1Btn = QPushButton("Fill UV")
        fillU1V1Btn.clicked.connect(self.FillShellToU1V1)
        sectionLayout.addWidget(fillU1V1Btn)

        halfUBtn = QPushButton("Half U")
        halfUBtn.clicked.connect(lambda : self.ScaleShell(0.5, 1))
        sectionLayout.addWidget(halfUBtn)

        halfVBtn = QPushButton("Half V")
        halfVBtn.clicked.connect(lambda : self.ScaleShell(1, 0.5))
        sectionLayout.addWidget(halfVBtn)

        doubleUBtn = QPushButton("Double U")
        doubleUBtn.clicked.connect(lambda : self.ScaleShell(2, 1))
        sectionLayout.addWidget(doubleUBtn)

        doubleVBtn = QPushButton("Double V")
        doubleVBtn.clicked.connect(lambda : self.ScaleShell(1, 2))
        sectionLayout.addWidget(doubleVBtn)

        moveSection = QGridLayout()
        sectionLayout.addLayout(moveSection)

        moveUpBtn = QPushButton("^")
        moveUpBtn.clicked.connect(lambda : self.MoveShell(0, 1))
        moveSection.addWidget(moveUpBtn, 0 , 1)

        moveDownBtn = QPushButton("v")
        moveDownBtn.clicked.connect(lambda : self.MoveShell(0, -1))
        moveSection.addWidget(moveDownBtn, 2 , 1)

        moveLeftBtn = QPushButton("<")
        moveLeftBtn.clicked.connect(lambda : self.MoveShell(-1, 0))
        moveSection.addWidget(moveLeftBtn, 1 , 0)

        moveRightBtn = QPushButton(">")
        moveRightBtn.clicked.connect(lambda : self.MoveShell(1, 0))
        moveSection.addWidget(moveRightBtn, 1 , 2)

    def GetShellBound(self):
        uvs = mc.polyListComponentConversion(self.shell, toUV=True)
        uvs = mc.ls(uvs, fl=True)
        firstUV = mc.polyEditUV(uvs[0], q=True)
        minU = firstUV[0]
        maxU = firstUV[0]
        minV = firstUV[1]
        maxV = firstUV[1]
        for uv in uvs:
            uvCoord = mc.polyEditUV(uv, q=True)
            if uvCoord[0] < minU:
                minU = uvCoord[0]
            
            if uvCoord[0] >maxU:
                minU = uvCoord[0]

            if uvCoord [1] < minV:
                minU = uvCoord[1]

            if uvCoord[1] > maxV:
                minU = uvCoord[1]
        return [minU, minV], [maxU, maxV]
    
    def BackToOrigin(self):
        minCoord, maxCoord = self.GetShellBound()
        mc.polyEditUV(self.shell, u=-minCoord[0], v=-minCoord[1])

    def TurnShell(self):
        mc.select(self.shell, r=True)
        mel.eval("polyRotateUVs 90 0")

    def CreateInitializationSection(self):
        sectionLayout = QHBoxLayout()
        self.masterLayout.addLayout(sectionLayout)

        selectShellBtn = QPushButton("Select Shell")
        selectShellBtn.clicked.connect(self.SelectShell)
        sectionLayout.addWidget(selectShellBtn)

        unfoldBtn = QPushButton("Unfold")
        unfoldBtn.clicked.connect(self.UnfoldShell)
        sectionLayout.addWidget(unfoldBtn)

        cutAndUnfoldBtn = QPushButton("Cut and Unfold")
        cutAndUnfoldBtn.clicked.connect(self.CutAndUnfoldShell)
        sectionLayout.addWidget(cutAndUnfoldBtn)

    def CutAndUnfoldShell(self):
        edges = mc.ls(sl=True)
        mc.polyProjection(self.shell, type="Planar", md="c")
        mc.polyMapCut(edges)
        mc.u3dUnfold(self.Shell)
        mel.eval("textOrientShells")

    def UnfoldShell(self):
        mc.polyProjection(self.shell, type="Planar", md="c")
        mc.u3dUnfold(self.shell)


    def SelectShell(self):
        self.shell = mc.ls(sl=True, fl=True)


    @staticmethod
    def GetMayaMainWindow():
        mainWindow = omui.MQtUtil.mainWindow()
        return wrapInstance(int(mainWindow), QMainWindow)
    
    @staticmethod
    def GetWindowUniqueId():
        return "53ef72c88116817fe7265383a6591a6f"

def Run():
    TrimSheetBuilderWidget().show()
    
