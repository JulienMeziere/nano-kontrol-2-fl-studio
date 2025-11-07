from core.constants import *


class SelectionManager:
    def __init__(self, lightController, flApi):
        self.lightController = lightController
        self.flApi = flApi
        self.prevSelectionStart = None
        self.prevSelectionEnd = None
        self.prevMarkerPressed = False
        self.nextMarkerPressed = False
        self.newSelectionStart = None
        self.wasPlayingWhenSelectionStarted = False
        self.selectionStep = FOUR_BARS_IN_TICKS
        self.hasSelectionMoved = False

    def isActive(self):
        return self.newSelectionStart is not None

    def setAccuracy(self, useHighAccuracy):
        self.selectionStep = ONE_BAR_IN_TICKS if useHighAccuracy else FOUR_BARS_IN_TICKS

    def checkIfShouldToggleSelection(self):
        if self.prevMarkerPressed and self.nextMarkerPressed:
            currentStart = self.flApi.selectionStart()
            currentEnd = self.flApi.selectionEnd()
            
            if currentEnd == -1 and self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
                self.flApi.liveSelection(self.prevSelectionStart, False)
                self.flApi.liveSelection(self.prevSelectionEnd, True)
            else:
                self.prevSelectionStart = currentStart
                self.prevSelectionEnd = currentEnd
                self.flApi.liveSelection(0, False)
                self.flApi.liveSelection(0, True)
            self.flApi.setSongPos(self.prevSelectionStart, 2)

    def startNewSelection(self):
        self.wasPlayingWhenSelectionStarted = self.flApi.isPlaying()
        if self.wasPlayingWhenSelectionStarted:
            self.flApi.start()

        self.prevSelectionStart = self.flApi.selectionStart()
        self.prevSelectionEnd = self.flApi.selectionEnd()
        self.flApi.liveSelection(0, False)
        self.flApi.liveSelection(0, True)
        
        currentPos = self.flApi.getSongPos(2)
        currentBar = round(currentPos / self.selectionStep)
        targetPos = currentBar * self.selectionStep
        self.flApi.setSongPos(targetPos, 2)
        
        self.newSelectionStart = self.flApi.currentTime(0)

    def endSelection(self):
        if self.newSelectionStart is not None:
            if not self.hasSelectionMoved:
                newEnd = self.flApi.currentTime(0)
                self.flApi.liveSelection(self.newSelectionStart, False)
                self.flApi.liveSelection(newEnd, True)
            if not self.flApi.isPlaying() and self.wasPlayingWhenSelectionStarted:
                self.flApi.start()
        self.newSelectionStart = None
        self.hasSelectionMoved = False

    def moveSelection(self, direction):
        if self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
            selectionLength = self.prevSelectionEnd - self.prevSelectionStart
            offset = selectionLength * direction
            newStart = max(0, self.prevSelectionStart + offset)
            newEnd = max(0, self.prevSelectionEnd + offset)
            self.flApi.liveSelection(newStart, False)
            self.flApi.liveSelection(newEnd, True)
            self.flApi.setSongPos(newStart, 2)
            self.prevSelectionStart = newStart
            self.prevSelectionEnd = newEnd
            self.hasSelectionMoved = True

    def moveSelectionForward(self):
        self.moveSelection(1)

    def moveSelectionBackward(self):
        self.moveSelection(-1)

    def movePrevMarker(self):
        currentPos = self.flApi.getSongPos(2)
        currentBar = currentPos // self.selectionStep
        targetBar = max(0, currentBar - 1)
        targetPos = targetBar * self.selectionStep
        self.flApi.setSongPos(targetPos, 2)
        self.prevMarkerPressed = True
        self.checkIfShouldToggleSelection()

    def moveNextMarker(self):
        currentPos = self.flApi.getSongPos(2)
        currentBar = currentPos // self.selectionStep
        targetBar = currentBar + 1
        targetPos = targetBar * self.selectionStep
        self.flApi.setSongPos(targetPos, 2)
        self.nextMarkerPressed = True
        self.checkIfShouldToggleSelection()

    def releasePrevMarker(self):
        self.prevMarkerPressed = False

    def releaseNextMarker(self):
        self.nextMarkerPressed = False
