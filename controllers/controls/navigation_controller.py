class NavigationController:
    def __init__(self, lightController, flApi, triggerMixerTracksScan):
        self.lightController = lightController
        self.flApi = flApi
        self.triggerMixerTracksScan = triggerMixerTracksScan
        self.nextTrackPressed = False
        self.prevTrackPressed = False

    def checkIfShouldTriggerScan(self):
        if self.prevTrackPressed and self.nextTrackPressed:
            self.triggerMixerTracksScan()

    def prevTrack(self):
        self.flApi.globalTransport(102, 1, 2, 15)
        self.prevTrackPressed = True
        self.checkIfShouldTriggerScan()

    def nextTrack(self):
        self.flApi.globalTransport(102, -1, 2, 15)
        self.nextTrackPressed = True
        self.checkIfShouldTriggerScan()

    def releasePrevTrack(self):
        self.prevTrackPressed = False

    def releaseNextTrack(self):
        self.nextTrackPressed = False

