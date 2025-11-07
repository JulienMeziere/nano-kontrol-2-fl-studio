from core.constants import *


class TransportController:
    def __init__(self, lightController, flApi):
        self.lightController = lightController
        self.flApi = flApi

    def play(self):
        self.lightController.updateLight(PLAY_BUTTON, True)
        self.flApi.start()

    def stop(self):
        self.lightController.updateLight(PLAY_BUTTON, False)
        self.lightController.updateLight(RECORD_BUTTON, False)
        self.lightController.updateLight(STOP_BUTTON, True)
        self.flApi.stop()

    def record(self):
        self.lightController.updateLight(RECORD_BUTTON, True)
        self.flApi.record()

    def rewindStart(self):
        self.flApi.rewind(2)
        self.lightController.updateLight(REWIND_BUTTON, True)

    def rewindEnd(self):
        self.flApi.rewind(0)
        self.lightController.updateLight(REWIND_BUTTON, False)

    def fastForwardStart(self):
        self.flApi.fastForward(2)
        self.lightController.updateLight(FORWARD_BUTTON, True)

    def fastForwardEnd(self):
        self.flApi.fastForward(0)
        self.lightController.updateLight(FORWARD_BUTTON, False)

