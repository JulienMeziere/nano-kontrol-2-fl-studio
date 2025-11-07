class PatternController:
    def __init__(self, flApi):
        self.flApi = flApi
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
        self.flApi.globalTransport(100, 1, 2, 15)

    def prevPattern(self):
        self.patternHasMoved = True
        self.flApi.globalTransport(100, -1, 2, 15)

