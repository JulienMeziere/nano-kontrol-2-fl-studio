# name=nano-controls-fl-studio
# url=https://github.com/JulienMeziere/nano-kontrol-2-fl-studio

from ui import *
from midi import *
from channels import *
from device import *
from mixer import *
from arrangement import *
from transport import *
from general import *
from time import sleep
import config
import math

# -->           HARDWARE
NEXT_TRACK_BUTTON = 0
PREV_TRACK_BUTTON = 1
MODE_BUTTON = 2
REWIND_BUTTON = 6
FORWARD_BUTTON = 7
STOP_BUTTON = 8
PLAY_BUTTON = 9
RECORD_BUTTON = 10

MARKER_SET_BUTTON = 3
MARKER_PREV_BUTTON = 4
MARKER_NEXT_BUTTON = 5

FIRST_KNOB = 11
LAST_KNOB = 18

TRACKS_FIRST_BUTTON = 19
TRACKS_LAST_BUTTON = 42

TRACKS_FIRST_FADER = 43
TRACKS_LAST_FADER = 50
# <--

# -->           CONSTANTS
MAX_VOLUME = 0.8
VOLUME_OFFSET = 0.003
SLEEP_TIME = 0.05
FL_TOTAL_NB_TRACKS = 125
TRANSPORT_CHANNEL = config.TransportChan - 1
MIDI_CHANNEL = config.MIDIChannel - 1
TOGGLE_MODE_BUTTONS = [PLAY_BUTTON, RECORD_BUTTON, MODE_BUTTON]
ONE_BAR_IN_TICKS = 384
FOUR_BARS_IN_TICKS = 1536
HW_DIRTY_LEDS_ALTERNATIVE = 260
# <--


def OnInit():
    print("*** nanoKONTROL2 script v1 by Julien MEZIERE ***")
    global tracksManager
    global controlsManager
    tracksManager = TracksManager()
    controlsManager = GeneralControlsManager(
        tracksManager.scanMixerTrackNames)


def OnProjectLoad():
    tracksManager.scanMixerTrackNames()


def OnRefresh(flag):
    if flag == HW_Dirty_LEDs or flag == HW_DIRTY_LEDS_ALTERNATIVE:
        controlsManager.updateButtonStates()


def updateButtonLight(button, turnOn=False):
    value = 0
    if turnOn:
        value = 127

    channel = TRANSPORT_CHANNEL
    if button >= TRACKS_FIRST_BUTTON:
        channel = MIDI_CHANNEL

    midiOutMsg(MIDI_CONTROLCHANGE, channel, button, value)


def updateTracksButtons(turnOn=False):
    value = 0
    if turnOn:
        value = 127
    for index in range(TRACKS_FIRST_BUTTON, TRACKS_LAST_BUTTON + 1):
        midiOutMsg(MIDI_CONTROLCHANGE, MIDI_CHANNEL, index, value)


class ButtonLightController:
    @staticmethod
    def updateLight(button, turnOn=False):
        updateButtonLight(button, turnOn)

    @staticmethod
    def updateTransportStates(init=False):
        if init:
            updateButtonLight(REWIND_BUTTON)
            updateButtonLight(FORWARD_BUTTON)
            updateButtonLight(STOP_BUTTON)

        updateButtonLight(RECORD_BUTTON, isRecording() != 0)
        updateButtonLight(PLAY_BUTTON, isPlaying() != 0)
        updateButtonLight(MODE_BUTTON, getLoopMode() == 0)


class SelectionManager:
    def __init__(self, lightController):
        self.lightController = lightController
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
            currentStart = selectionStart()
            currentEnd = selectionEnd()
            
            if currentEnd == -1 and self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
                liveSelection(self.prevSelectionStart, False)
                liveSelection(self.prevSelectionEnd, True)
            else:
                self.prevSelectionStart = currentStart
                self.prevSelectionEnd = currentEnd
                liveSelection(0, False)
                liveSelection(0, True)
            setSongPos(self.prevSelectionStart, 2)

    def startNewSelection(self):
        self.wasPlayingWhenSelectionStarted = isPlaying()
        if self.wasPlayingWhenSelectionStarted:
            start()

        self.prevSelectionStart = selectionStart()
        self.prevSelectionEnd = selectionEnd()
        liveSelection(0, False)
        liveSelection(0, True)
        
        currentPos = getSongPos(2)
        currentBar = round(currentPos / self.selectionStep)
        targetPos = currentBar * self.selectionStep
        setSongPos(targetPos, 2)
        
        self.newSelectionStart = currentTime(0)

    def endSelection(self):
        if self.newSelectionStart is not None:
            if not self.hasSelectionMoved:
                newEnd = currentTime(0)
                liveSelection(self.newSelectionStart, False)
                liveSelection(newEnd, True)
            if not isPlaying() and self.wasPlayingWhenSelectionStarted:
                start()
        self.newSelectionStart = None
        self.hasSelectionMoved = False

    def _moveSelection(self, direction):
        if self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
            selectionLength = self.prevSelectionEnd - self.prevSelectionStart
            offset = selectionLength * direction
            newStart = max(0, self.prevSelectionStart + offset)
            newEnd = max(0, self.prevSelectionEnd + offset)
            liveSelection(newStart, False)
            liveSelection(newEnd, True)
            setSongPos(newStart, 2)
            self.prevSelectionStart = newStart
            self.prevSelectionEnd = newEnd
            self.hasSelectionMoved = True

    def moveSelectionForward(self):
        self._moveSelection(1)

    def moveSelectionBackward(self):
        self._moveSelection(-1)

    def movePrevMarker(self):
        currentPos = getSongPos(2)
        currentBar = currentPos // self.selectionStep
        targetBar = max(0, currentBar - 1)
        targetPos = targetBar * self.selectionStep
        setSongPos(targetPos, 2)
        self.prevMarkerPressed = True
        self.checkIfShouldToggleSelection()

    def moveNextMarker(self):
        currentPos = getSongPos(2)
        currentBar = currentPos // self.selectionStep
        targetBar = currentBar + 1
        targetPos = targetBar * self.selectionStep
        setSongPos(targetPos, 2)
        self.nextMarkerPressed = True
        self.checkIfShouldToggleSelection()

    def releasePrevMarker(self):
        self.prevMarkerPressed = False

    def releaseNextMarker(self):
        self.nextMarkerPressed = False


class TransportController:
    def __init__(self, lightController):
        self.lightController = lightController

    def play(self):
        self.lightController.updateLight(PLAY_BUTTON, True)
        start()

    def stop(self):
        self.lightController.updateLight(PLAY_BUTTON, False)
        self.lightController.updateLight(RECORD_BUTTON, False)
        self.lightController.updateLight(STOP_BUTTON, True)
        stop()

    def record(self):
        self.lightController.updateLight(RECORD_BUTTON, True)
        record()

    def rewindStart(self):
        rewind(2)
        self.lightController.updateLight(REWIND_BUTTON, True)

    def rewindEnd(self):
        rewind(0)
        self.lightController.updateLight(REWIND_BUTTON, False)

    def fastForwardStart(self):
        fastForward(2)
        self.lightController.updateLight(FORWARD_BUTTON, True)

    def fastForwardEnd(self):
        fastForward(0)
        self.lightController.updateLight(FORWARD_BUTTON, False)


class NavigationController:
    def __init__(self, lightController, triggerMixerTracksScan):
        self.lightController = lightController
        self.triggerMixerTracksScan = triggerMixerTracksScan
        self.nextTrackPressed = False
        self.prevTrackPressed = False

    def checkIfShouldTriggerScan(self):
        if self.prevTrackPressed and self.nextTrackPressed:
            self.triggerMixerTracksScan()

    def prevTrack(self):
        globalTransport(102, 1, 2, 15)
        self.prevTrackPressed = True
        self.checkIfShouldTriggerScan()

    def nextTrack(self):
        globalTransport(102, -1, 2, 15)
        self.nextTrackPressed = True
        self.checkIfShouldTriggerScan()

    def releasePrevTrack(self):
        self.prevTrackPressed = False

    def releaseNextTrack(self):
        self.nextTrackPressed = False


class PatternController:
    def __init__(self):
        self.modeButtonPressed = False
        self.patternHasMoved = False

    def isModePressed(self):
        return self.modeButtonPressed

    def pressModeButton(self):
        self.modeButtonPressed = True

    def releaseModeButton(self):
        shouldToggleLoopMode = not self.patternHasMoved
        self.modeButtonPressed = False
        self.patternHasMoved = False
        return shouldToggleLoopMode

    def nextPattern(self):
        self.patternHasMoved = True
        globalTransport(100, 1, 2, 15)

    def prevPattern(self):
        self.patternHasMoved = True
        globalTransport(100, -1, 2, 15)


class LoopModeController:
    @staticmethod
    def toggleLoopMode():
        setLoopMode()
        if getLoopMode() == 0:
            showWindow(1)
        else:
            hideWindow(1)


class GeneralControlsManager:
    def __init__(self, triggerMixerTracksScan):
        self.lightController = ButtonLightController()
        self.selectionManager = SelectionManager(self.lightController)
        self.transportController = TransportController(self.lightController)
        self.navigationController = NavigationController(self.lightController, triggerMixerTracksScan)
        self.patternController = PatternController()
        self.loopModeController = LoopModeController()
        self.updateButtonStates(True)

    def updateButtonStates(self, init=False):
        self.lightController.updateTransportStates(init)

    def onPressStart(self, button):
        if button == PLAY_BUTTON:
            self.transportController.play()
        elif button == STOP_BUTTON:
            self.transportController.stop()
        elif button == RECORD_BUTTON:
            self.transportController.record()
        elif button == MODE_BUTTON:
            self.patternController.pressModeButton()
        elif button == PREV_TRACK_BUTTON:
            if self.patternController.isModePressed():
                self.patternController.nextPattern()
            elif self.selectionManager.isActive():
                self.selectionManager.moveSelectionForward()
            else:
                self.navigationController.prevTrack()
        elif button == NEXT_TRACK_BUTTON:
            if self.patternController.isModePressed():
                self.patternController.prevPattern()
            elif self.selectionManager.isActive():
                self.selectionManager.moveSelectionBackward()
            else:
                self.navigationController.nextTrack()
        elif button == REWIND_BUTTON:
            self.transportController.rewindStart()
        elif button == FORWARD_BUTTON:
            if self.selectionManager.isActive():
                self.selectionManager.setAccuracy(True)
            else:
                self.transportController.fastForwardStart()
            self.lightController.updateLight(button, True)
        elif button == MARKER_PREV_BUTTON:
            self.selectionManager.movePrevMarker()
        elif button == MARKER_NEXT_BUTTON:
            self.selectionManager.moveNextMarker()
        elif button == MARKER_SET_BUTTON:
            self.selectionManager.startNewSelection()
        else:
            self.lightController.updateLight(button, True)

    def onPressEnd(self, button):
        if button == PREV_TRACK_BUTTON:
            self.navigationController.releasePrevTrack()
        elif button == NEXT_TRACK_BUTTON:
            self.navigationController.releaseNextTrack()
        elif button == MARKER_PREV_BUTTON:
            self.selectionManager.releasePrevMarker()
        elif button == MARKER_NEXT_BUTTON:
            self.selectionManager.releaseNextMarker()
        elif button == MARKER_SET_BUTTON:
            self.selectionManager.endSelection()
        elif button == REWIND_BUTTON:
            self.transportController.rewindEnd()
        elif button == FORWARD_BUTTON:
            self.transportController.fastForwardEnd()
            self.selectionManager.setAccuracy(False)
        elif button == MODE_BUTTON:
            if self.patternController.releaseModeButton():
                self.loopModeController.toggleLoopMode()
        elif button not in TOGGLE_MODE_BUTTONS:
            self.lightController.updateLight(button, False)


class TracksManager:
    def __init__(self):
        self.groupSoloed = -1
        self.mutedGroups = []
        self.armedGroups = []
        self.trackGroups = []
        self.trackGroupMasters = []
        updateTracksButtons(False)

    @staticmethod
    def _getGroupIndexFromButton(button):
        return (button - TRACKS_FIRST_BUTTON) // 3

    @staticmethod
    def _getSoloButton(groupIndex):
        return TRACKS_FIRST_BUTTON + groupIndex * 3

    @staticmethod
    def _getMuteButton(groupIndex):
        return TRACKS_FIRST_BUTTON + groupIndex * 3 + 1

    @staticmethod
    def _getArmButton(groupIndex):
        return TRACKS_FIRST_BUTTON + groupIndex * 3 + 2

    def findTracksOfGroup(self, groupIndex, onlyMasters=False):
        trackGroup = []
        textToFindGroupTrack = f"({groupIndex})"
        textToFindGroupMasterTrack = f"[{groupIndex}]"

        for trackIndex in range(0, FL_TOTAL_NB_TRACKS + 1):
            trackName = getTrackName(trackIndex)
            if (not onlyMasters and textToFindGroupTrack in trackName) or textToFindGroupMasterTrack in trackName:
                trackGroup.append(trackIndex)

        return trackGroup

    def scanMixerTrackNames(self):
        self.trackGroups = []
        self.trackGroupMasters = []

        for index in range(1, 9):
            self.trackGroups.append(self.findTracksOfGroup(index))
            self.trackGroupMasters.append(
                self.findTracksOfGroup(index, True))

        for index in range(0, 2):
            updateTracksButtons(True)
            sleep(0.1)
            updateTracksButtons(False)
            sleep(0.1)
    # <--- mixer scan methods

    def armTrack(self, button):
        groupIndex = self._getGroupIndexFromButton(button)
        if groupIndex < 0 or groupIndex >= len(self.trackGroups):
            return

        armButton = self._getArmButton(groupIndex)
        
        if groupIndex in self.armedGroups:
            self.armedGroups.remove(groupIndex)
            updateButtonLight(armButton, False)

            for track in self.trackGroupMasters[groupIndex]:
                if isTrackArmed(track) != 0:
                    armTrack(track)
        else:
            self.armedGroups.append(groupIndex)
            updateButtonLight(armButton, True)

            for track in self.trackGroupMasters[groupIndex]:
                if isTrackArmed(track) == 0:
                    armTrack(track)

    def checkIfOnlyOneGroupUnmuted(self):
        if len(self.mutedGroups) != len(self.trackGroups) - 1:
            return

        for index in range(len(self.trackGroups)):
            if index not in self.mutedGroups:
                self.groupSoloed = index
                updateButtonLight(self._getSoloButton(index), True)
                break

    def muteGroup(self, button):
        groupIndex = self._getGroupIndexFromButton(button)
        if groupIndex < 0 or groupIndex >= len(self.trackGroups):
            return

        if self.groupSoloed > -1:
            updateButtonLight(self._getSoloButton(self.groupSoloed), False)
            self.groupSoloed = -1

        muteButton = self._getMuteButton(groupIndex)
        
        if groupIndex in self.mutedGroups:
            self.mutedGroups.remove(groupIndex)
            mute = False
        else:
            self.mutedGroups.append(groupIndex)
            mute = True

        updateButtonLight(muteButton, not mute)

        for track in self.trackGroups[groupIndex]:
            if mute and isTrackMuted(track) == 0:
                muteTrack(track)
            elif not mute and isTrackMuted(track) != 0:
                muteTrack(track)

        self.checkIfOnlyOneGroupUnmuted()

    def muteAllTracksExcept(self, exceptionGroupIndex):
        updateButtonLight(self._getMuteButton(exceptionGroupIndex), True)
        self.mutedGroups = []
        for index in range(len(self.trackGroups)):
            if index != exceptionGroupIndex:
                updateButtonLight(self._getMuteButton(index), False)
                self.mutedGroups.append(index)

    def clearAllMuteButtonLights(self):
        for index in range(len(self.trackGroups)):
            updateButtonLight(self._getMuteButton(index), True)
        self.mutedGroups = []

    def soloGroup(self, button):
        groupIndex = self._getGroupIndexFromButton(button)
        if groupIndex < 0 or groupIndex >= len(self.trackGroups) or len(self.trackGroups[groupIndex]) == 0:
            return

        firstGroupTrack = self.trackGroups[groupIndex][0]

        if self.groupSoloed == groupIndex:
            updateButtonLight(button, False)
            self.clearAllMuteButtonLights()

            soloTrack(firstGroupTrack)

            sleep(SLEEP_TIME)
            if isTrackSolo(firstGroupTrack) != 0:
                soloTrack(firstGroupTrack)

            self.groupSoloed = -1
            return

        if self.groupSoloed >= 0:
            updateButtonLight(self._getSoloButton(self.groupSoloed), False)

        updateButtonLight(button, True)
        self.muteAllTracksExcept(groupIndex)

        self.groupSoloed = groupIndex
        if isTrackSolo(firstGroupTrack) == 0:
            soloTrack(firstGroupTrack)

        groupLength = len(self.trackGroups[groupIndex])
        if groupLength <= 1:
            return
        sleep(SLEEP_TIME)

        for index in range(1, groupLength):
            track = self.trackGroups[groupIndex][index]
            if isTrackMuted(track) != 0:
                muteTrack(track)

    def volumeFader(self, fader, value):
        groupIndex = fader - TRACKS_FIRST_FADER
        if groupIndex < 0 or groupIndex >= len(self.trackGroupMasters):
            return

        volume = (value / 127 - VOLUME_OFFSET) * MAX_VOLUME
        for track in self.trackGroupMasters[groupIndex]:
            setTrackVolume(track, volume)


def OnControlChange(event):
    event.handled = True
    button = event.data1

    if button >= TRACKS_FIRST_FADER and button <= TRACKS_LAST_FADER:  # Handle mixer faders
        tracksManager.volumeFader(event.data1, event.data2)
    elif button >= TRACKS_FIRST_BUTTON and button <= TRACKS_LAST_BUTTON:  # Handle S,M,R buttons
        if event.data2 == 0:
            return

        # trackButton =     0   -->     'S' button
        # trackButton =     1   -->     'M' button
        # trackButton =     2   -->     'R' button
        trackButton = (button - TRACKS_FIRST_BUTTON) % 3

        if trackButton == 0:
            tracksManager.soloGroup(button)
        elif trackButton == 1:
            tracksManager.muteGroup(button)
        elif trackButton == 2:
            tracksManager.armTrack(button)
    elif button >= FIRST_KNOB and button <= LAST_KNOB:
        event.handled = False
    elif event.data2 == 0:  # PRESS END
        controlsManager.onPressEnd(button)
    elif event.data2 > 0: # PRESS START
        controlsManager.onPressStart(button)
