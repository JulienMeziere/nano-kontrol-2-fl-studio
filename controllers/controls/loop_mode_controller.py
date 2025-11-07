class LoopModeController:
    def __init__(self, flApi):
        self.flApi = flApi
    
    def toggleLoopMode(self):
        self.flApi.setLoopMode()
        if self.flApi.getLoopMode() == 0:
            self.flApi.showWindow(1)
        else:
            self.flApi.hideWindow(1)

