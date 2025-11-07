from core.constants import *


class ButtonLightController:
    def __init__(self, hardwareInterface, flApi):
        self.hardwareInterface = hardwareInterface
        self.flApi = flApi
    
    def updateLight(self, button, turnOn=False):
        self.hardwareInterface.updateButtonLight(button, turnOn)

    def updateTransportStates(self, init=False):
        if init:
            self.hardwareInterface.updateButtonLight(REWIND_BUTTON)
            self.hardwareInterface.updateButtonLight(FORWARD_BUTTON)
            self.hardwareInterface.updateButtonLight(STOP_BUTTON)

        self.hardwareInterface.updateButtonLight(RECORD_BUTTON, self.flApi.isRecording() != 0)
        self.hardwareInterface.updateButtonLight(PLAY_BUTTON, self.flApi.isPlaying() != 0)
        self.hardwareInterface.updateButtonLight(MODE_BUTTON, self.flApi.getLoopMode() == 0)

