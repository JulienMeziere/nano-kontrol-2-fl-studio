from core.constants import *


class HardwareInterface:
    """Hardware interface for MIDI communication"""
    
    def __init__(self, flApi):
        self.flApi = flApi
    
    def updateButtonLight(self, button, turnOn=False):
        value = 127 if turnOn else 0
        channel = MIDI_CHANNEL if button >= TRACKS_FIRST_BUTTON else TRANSPORT_CHANNEL
        self.flApi.sendMidiMessage(self.flApi.MIDI_CONTROLCHANGE, channel, button, value)
    
    def updateTracksButtons(self, turnOn=False):
        value = 127 if turnOn else 0
        for index in range(TRACKS_FIRST_BUTTON, TRACKS_LAST_BUTTON + 1):
            self.flApi.sendMidiMessage(self.flApi.MIDI_CONTROLCHANGE, MIDI_CHANNEL, index, value)

