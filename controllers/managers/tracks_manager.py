from time import sleep
from core.constants import *


class TracksManager:
    def __init__(self, hardwareInterface, flApi):
        self.hardwareInterface = hardwareInterface
        self.flApi = flApi
        self.groupSoloed = -1
        self.mutedGroups = []
        self.armedGroups = []
        self.trackGroups = []
        self.trackGroupMasters = []
        self.hardwareInterface.updateTracksButtons(False)

    @staticmethod
    def getGroupIndexFromButton(button):
        return (button - TRACKS_FIRST_BUTTON) // 3

    @staticmethod
    def getSoloButton(groupIndex):
        return TRACKS_FIRST_BUTTON + groupIndex * 3

    @staticmethod
    def getMuteButton(groupIndex):
        return TRACKS_FIRST_BUTTON + groupIndex * 3 + 1

    @staticmethod
    def getArmButton(groupIndex):
        return TRACKS_FIRST_BUTTON + groupIndex * 3 + 2

    def validateGroupIndex(self, button):
        groupIndex = self.getGroupIndexFromButton(button)
        if groupIndex < 0 or groupIndex >= len(self.trackGroups):
            return None
        return groupIndex

    def findTracksOfGroup(self, groupIndex, onlyMasters=False):
        trackGroup = []
        textToFindGroupTrack = f"({groupIndex})"
        textToFindGroupMasterTrack = f"[{groupIndex}]"

        for trackIndex in range(0, FL_TOTAL_NB_TRACKS + 1):
            trackName = self.flApi.getTrackName(trackIndex)
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
            self.hardwareInterface.updateTracksButtons(True)
            sleep(0.1)
            self.hardwareInterface.updateTracksButtons(False)
            sleep(0.1)

    def armTrack(self, button):
        groupIndex = self.validateGroupIndex(button)
        if groupIndex is None:
            return

        armButton = self.getArmButton(groupIndex)
        
        if groupIndex in self.armedGroups:
            self.armedGroups.remove(groupIndex)
            self.hardwareInterface.updateButtonLight(armButton, False)

            for track in self.trackGroupMasters[groupIndex]:
                if self.flApi.isTrackArmed(track) != 0:
                    self.flApi.armTrack(track)
        else:
            self.armedGroups.append(groupIndex)
            self.hardwareInterface.updateButtonLight(armButton, True)

            for track in self.trackGroupMasters[groupIndex]:
                if self.flApi.isTrackArmed(track) == 0:
                    self.flApi.armTrack(track)

    def checkIfOnlyOneGroupUnmuted(self):
        if len(self.mutedGroups) != len(self.trackGroups) - 1:
            return

        for index in range(len(self.trackGroups)):
            if index not in self.mutedGroups:
                self.groupSoloed = index
                self.hardwareInterface.updateButtonLight(self.getSoloButton(index), True)
                break

    def muteGroup(self, button):
        groupIndex = self.validateGroupIndex(button)
        if groupIndex is None:
            return

        if self.groupSoloed > -1:
            self.hardwareInterface.updateButtonLight(self.getSoloButton(self.groupSoloed), False)
            self.groupSoloed = -1

        muteButton = self.getMuteButton(groupIndex)
        
        if groupIndex in self.mutedGroups:
            self.mutedGroups.remove(groupIndex)
            mute = False
        else:
            self.mutedGroups.append(groupIndex)
            mute = True

        self.hardwareInterface.updateButtonLight(muteButton, not mute)

        for track in self.trackGroups[groupIndex]:
            if mute and self.flApi.isTrackMuted(track) == 0:
                self.flApi.muteTrack(track)
            elif not mute and self.flApi.isTrackMuted(track) != 0:
                self.flApi.muteTrack(track)

        self.checkIfOnlyOneGroupUnmuted()

    def muteAllTracksExcept(self, exceptionGroupIndex):
        self.hardwareInterface.updateButtonLight(self.getMuteButton(exceptionGroupIndex), True)
        self.mutedGroups = []
        for index in range(len(self.trackGroups)):
            if index != exceptionGroupIndex:
                self.hardwareInterface.updateButtonLight(self.getMuteButton(index), False)
                self.mutedGroups.append(index)

    def clearAllMuteButtonLights(self):
        for index in range(len(self.trackGroups)):
            self.hardwareInterface.updateButtonLight(self.getMuteButton(index), True)
        self.mutedGroups = []

    def soloGroup(self, button):
        groupIndex = self.validateGroupIndex(button)
        if groupIndex is None or len(self.trackGroups[groupIndex]) == 0:
            return

        firstGroupTrack = self.trackGroups[groupIndex][0]

        if self.groupSoloed == groupIndex:
            self.hardwareInterface.updateButtonLight(button, False)
            self.clearAllMuteButtonLights()

            self.flApi.soloTrack(firstGroupTrack)

            sleep(SLEEP_TIME)
            if self.flApi.isTrackSolo(firstGroupTrack) != 0:
                self.flApi.soloTrack(firstGroupTrack)

            self.groupSoloed = -1
            return

        if self.groupSoloed >= 0:
            self.hardwareInterface.updateButtonLight(self.getSoloButton(self.groupSoloed), False)

        self.hardwareInterface.updateButtonLight(button, True)
        self.muteAllTracksExcept(groupIndex)

        self.groupSoloed = groupIndex
        if self.flApi.isTrackSolo(firstGroupTrack) == 0:
            self.flApi.soloTrack(firstGroupTrack)

        groupLength = len(self.trackGroups[groupIndex])
        if groupLength <= 1:
            return
        sleep(SLEEP_TIME)

        for index in range(1, groupLength):
            track = self.trackGroups[groupIndex][index]
            if self.flApi.isTrackMuted(track) != 0:
                self.flApi.muteTrack(track)

    def volumeFader(self, fader, value):
        groupIndex = fader - TRACKS_FIRST_FADER
        if groupIndex < 0 or groupIndex >= len(self.trackGroupMasters):
            return

        volume = (value / 127 - VOLUME_OFFSET) * MAX_VOLUME
        for track in self.trackGroupMasters[groupIndex]:
            self.flApi.setTrackVolume(track, volume)

