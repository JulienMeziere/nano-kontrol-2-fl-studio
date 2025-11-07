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
SLEEP_TIME = 0.05
FL_TOTAL_NB_TRACKS = 125
TRANSPORT_CHANNEL = config.TransportChan - 1
MIDI_CHANNEL = config.MIDIChannel - 1
TOGGLE_MODE_BUTTONS = [PLAY_BUTTON, RECORD_BUTTON, MODE_BUTTON]
ONE_BAR_IN_TICKS = 384
FOUR_BARS_IN_TICKS = 1536
# <--

TRACKS_AFFECTED = [3, 6, 23, 47, 55, 59, 67, 32]


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
    if flag == HW_Dirty_LEDs or flag == 260:
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


class GeneralControlsManager:
    def __init__(self, triggerMixerTracksScan):
        self.nextTrackPressed = False
        self.prevTrackPressed = False
        self.triggerMixerTracksScan = triggerMixerTracksScan
        self.updateButtonStates(True)
        self.prevSelectionStart = None
        self.prevSelectionEnd = None
        self.prevMarkerPressed = False
        self.nextMarkerPressed = False
        self.newSelectionStart = None
        self.wasPlayingWhenSelectionStarted = False
        self.selectionStep = FOUR_BARS_IN_TICKS
        self.hasSelectionMoved = False
        self.modeButtonPressed = False
        self.patternHasMoved = False

    def updateButtonStates(self, init=False):
        if init:
            updateButtonLight(REWIND_BUTTON)
            updateButtonLight(FORWARD_BUTTON)
            updateButtonLight(STOP_BUTTON)

        if isRecording() == 0:
            updateButtonLight(RECORD_BUTTON)
        else:
            updateButtonLight(RECORD_BUTTON, True)

        if isPlaying() == 0:
            updateButtonLight(PLAY_BUTTON)
        else:
            updateButtonLight(PLAY_BUTTON, True)

        if getLoopMode() == 0:
            updateButtonLight(MODE_BUTTON, True)
        else:
            updateButtonLight(MODE_BUTTON)

    def checkIfShouldTriggerScan(self):
        if self.prevTrackPressed and self.nextTrackPressed:
            self.triggerMixerTracksScan()
    
    def checkIfShouldManageSelection(self):
        if self.prevMarkerPressed and self.nextMarkerPressed:
            currentStart = selectionStart()
            currentEnd = selectionEnd()
            
            if currentEnd == -1 and self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
                # No current selection, restoring previous selection
                liveSelection(self.prevSelectionStart, False)
                liveSelection(self.prevSelectionEnd, True)
            else:
                # Save current selection and clear it
                self.prevSelectionStart = currentStart
                self.prevSelectionEnd = currentEnd
                liveSelection(0, False)
                liveSelection(0, True)
            setSongPos(self.prevSelectionStart, 2)

    def onPressStart(self, button):
        if button == PLAY_BUTTON:
            updateButtonLight(button, True)
            start()
        elif button == STOP_BUTTON:
            updateButtonLight(PLAY_BUTTON, False)
            updateButtonLight(RECORD_BUTTON, False)
            updateButtonLight(button, True)
            stop()
        elif button == RECORD_BUTTON:
            updateButtonLight(button, True)
            record()
        elif button == MODE_BUTTON:
            self.modeButtonPressed = True
        elif button == PREV_TRACK_BUTTON:
            if self.modeButtonPressed:
                self.patternHasMoved = True
                globalTransport(100, 1, 2, 15)  # Next pattern (FPT_PatternJog)
            elif self.newSelectionStart is not None:
                # Move selection forward by its own length using prevSelection values
                if self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
                    selectionLength = self.prevSelectionEnd - self.prevSelectionStart
                    newStart = self.prevSelectionStart + selectionLength
                    newEnd = self.prevSelectionEnd + selectionLength
                    liveSelection(newStart, False)
                    liveSelection(newEnd, True)
                    setSongPos(newStart, 2)
                    # Update the prevSelection values
                    self.prevSelectionStart = newStart
                    self.prevSelectionEnd = newEnd
                    self.hasSelectionMoved = True
            else:
                globalTransport(102, 1, 2, 15)
            self.prevTrackPressed = True
            self.checkIfShouldTriggerScan()
        elif button == NEXT_TRACK_BUTTON:
            if self.modeButtonPressed:
                self.patternHasMoved = True
                globalTransport(100, -1, 2, 15)  # Next pattern (FPT_PatternJog)
            elif self.newSelectionStart is not None:
                # Move selection back by its own length using prevSelection values
                if self.prevSelectionStart is not None and self.prevSelectionEnd is not None:
                    selectionLength = self.prevSelectionEnd - self.prevSelectionStart
                    newStart = max(0, self.prevSelectionStart - selectionLength)
                    newEnd = max(0, self.prevSelectionEnd - selectionLength)
                    liveSelection(newStart, False)
                    liveSelection(newEnd, True)
                    setSongPos(newStart, 2)
                    # Update the prevSelection values
                    self.prevSelectionStart = newStart
                    self.prevSelectionEnd = newEnd
                    self.hasSelectionMoved = True
            else:
                globalTransport(102, -1, 2, 15)
            self.nextTrackPressed = True
            self.checkIfShouldTriggerScan()
        elif button == REWIND_BUTTON:
            rewind(2)
            updateButtonLight(button, True)
        elif button == FORWARD_BUTTON:
            if self.newSelectionStart is not None:
                # if we are in a selection, we use that button to increase selection accuracy
                self.selectionStep = ONE_BAR_IN_TICKS
            else:
                fastForward(2)
            updateButtonLight(button, True)
        elif button == MARKER_PREV_BUTTON:
            # Move playhead back one bar and snap to bar boundary
            currentPos = getSongPos(2)
            currentBar = currentPos // self.selectionStep  # Calculate current bar
            targetBar = max(0, currentBar - 1)  # Previous bar (minimum 0)
            targetPos = targetBar * self.selectionStep  # Snap to bar start
            setSongPos(targetPos, 2)
            self.prevMarkerPressed = True
            self.checkIfShouldManageSelection()
        elif button == MARKER_NEXT_BUTTON:
            # Move playhead forward one bar and snap to bar boundary
            currentPos = getSongPos(2)
            currentBar = currentPos // self.selectionStep  # Calculate current bar
            targetBar = currentBar + 1  # Next bar
            targetPos = targetBar * self.selectionStep  # Snap to bar start
            setSongPos(targetPos, 2)
            self.nextMarkerPressed = True
            self.checkIfShouldManageSelection()
        elif button == MARKER_SET_BUTTON:
            # Pause playback and start new selection at nearest bar
            self.wasPlayingWhenSelectionStarted = isPlaying()
            if self.wasPlayingWhenSelectionStarted:
                start()
            

            # Clear current selection
            self.prevSelectionStart = selectionStart()
            self.prevSelectionEnd = selectionEnd()
            liveSelection(0, False)
            liveSelection(0, True)
            
            # Snap to nearest bar
            currentPos = getSongPos(2)
            currentBar = round(currentPos / self.selectionStep)  # Round to nearest bar
            targetPos = currentBar * self.selectionStep  # Snap to bar start
            setSongPos(targetPos, 2)
            
            self.newSelectionStart = currentTime(0)
        else:
            updateButtonLight(button, True)

    def onPressEnd(self, button):
        if button == PREV_TRACK_BUTTON:
            self.prevTrackPressed = False
        elif button == NEXT_TRACK_BUTTON:
            self.nextTrackPressed = False
        elif button == MARKER_PREV_BUTTON:
            self.prevMarkerPressed = False
        elif button == MARKER_NEXT_BUTTON:
            self.nextMarkerPressed = False
        elif button == MARKER_SET_BUTTON:
            if self.newSelectionStart is not None:
                if not self.hasSelectionMoved:
                    newEnd = currentTime(0)
                    liveSelection(self.newSelectionStart, False)
                    liveSelection(newEnd, True)
                if not isPlaying() and self.wasPlayingWhenSelectionStarted:
                    start()
            self.newSelectionStart = None
            self.hasSelectionMoved = False
        elif button == REWIND_BUTTON:
            rewind(0)
            updateButtonLight(button, False)
        elif button == FORWARD_BUTTON:
            fastForward(0)
            self.selectionStep = FOUR_BARS_IN_TICKS
            updateButtonLight(button, False)
        elif button == MODE_BUTTON:
            if self.patternHasMoved:
                self.patternHasMoved = False
            else:
                setLoopMode()
                # Toggle sequencer visibility based on loop mode
                if getLoopMode() == 0:
                    showWindow(1) 
                else:
                    hideWindow(1)
            self.modeButtonPressed = False
        else:
            try:
                TOGGLE_MODE_BUTTONS.index(button)
                return
            except:
                updateButtonLight(button, False)


class TracksManager:
    def __init__(self):
        self.groupSoloed = -1
        self.mutedGroups = []
        self.armedGroups = []
        self.trackGroups = []
        self.trackGroupMasters = []
        updateTracksButtons(False)

    # mixer scan methods --->
    def findTracksOfGroup(self, groupIndex, onlyMasters=False):
        trackGroup = []
        textToFindGroupTrack = "(" + str(groupIndex) + ")"
        textToFindGroupMasterTrack = "[" + str(groupIndex) + "]"

        for trackIndex in range(0, FL_TOTAL_NB_TRACKS + 1):
            trackName = getTrackName(trackIndex)
            if (onlyMasters == False and textToFindGroupTrack in trackName) or textToFindGroupMasterTrack in trackName:
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
        groupIndex = math.floor((button - TRACKS_FIRST_BUTTON) / 3)
        if groupIndex < 0 or groupIndex >= len(self.trackGroups):
            return

        armButton = TRACKS_FIRST_BUTTON + groupIndex * 3 + 2
        try:
            index = self.armedGroups.index(groupIndex)

            # unarm
            del self.armedGroups[index]
            updateButtonLight(armButton, False)

            for track in self.trackGroupMasters[groupIndex]:
                if (isTrackArmed(track) != 0):
                    armTrack(track)

        except:
            # arm
            self.armedGroups.append(groupIndex)
            updateButtonLight(armButton, True)

            for track in self.trackGroupMasters[groupIndex]:
                if (isTrackArmed(track) == 0):
                    armTrack(track)

    def checkIfOnlyOneGroupUnmuted(self):
        if len(self.mutedGroups) != len(self.trackGroups) - 1:
            return

        for index in range(0, len(self.trackGroups)):
            if (index in self.mutedGroups) == False:
                self.groupSoloed = index
                updateButtonLight(
                    TRACKS_FIRST_BUTTON + index * 3, True)
                break

    def muteGroup(self, button):
        groupIndex = math.floor((button - TRACKS_FIRST_BUTTON) / 3)
        if groupIndex < 0 or groupIndex >= len(self.trackGroups):
            return

        if self.groupSoloed > -1:
            updateButtonLight(
                TRACKS_FIRST_BUTTON + self.groupSoloed * 3, False)
            self.groupSoloed = -1

        muteButton = TRACKS_FIRST_BUTTON + groupIndex * 3 + 1
        mute = False
        try:
            index = self.mutedGroups.index(groupIndex)

            # unmute
            del self.mutedGroups[index]

        except:
            # mute
            self.mutedGroups.append(groupIndex)
            mute = True

        updateButtonLight(muteButton, not mute)

        for index in range(0, len(self.trackGroups[groupIndex])):
            track = self.trackGroups[groupIndex][index]
            if mute == True and isTrackMuted(track) == 0:
                muteTrack(track)
            elif mute == False and isTrackMuted(track) != 0:
                muteTrack(track)

        self.checkIfOnlyOneGroupUnmuted()

    def muteAllTracksExcept(self, exceptionGroupIndex):
        updateButtonLight(
            TRACKS_FIRST_BUTTON + exceptionGroupIndex * 3 + 1, True)
        self.mutedGroups = []
        for index in range(0, len(self.trackGroups)):
            if index != exceptionGroupIndex:
                updateButtonLight(
                    TRACKS_FIRST_BUTTON + index * 3 + 1, False)
                self.mutedGroups.append(index)

    def clearAllMuteButtonLights(self):
        for index in range(0, len(self.trackGroups)):
            updateButtonLight(
                TRACKS_FIRST_BUTTON + index * 3 + 1, True)
        self.mutedGroups = []

    def soloGroup(self, button):
        groupIndex = math.floor((button - TRACKS_FIRST_BUTTON) / 3)
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
            updateButtonLight(
                TRACKS_FIRST_BUTTON + self.groupSoloed * 3, False)

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

        volume = (value / 127 - 0.003) * MAX_VOLUME
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
