from controllers.ui.button_light_controller import ButtonLightController
from controllers.managers.selection_manager import SelectionManager
from controllers.controls.transport_controller import TransportController
from controllers.controls.navigation_controller import NavigationController
from controllers.controls.pattern_controller import PatternController
from controllers.controls.loop_mode_controller import LoopModeController
from core.constants import *


class GeneralControlsManager:
    def __init__(self, hardwareInterface, flApi, triggerMixerTracksScan):
        self.lightController = ButtonLightController(hardwareInterface, flApi)
        self.selectionManager = SelectionManager(self.lightController, flApi)
        self.transportController = TransportController(self.lightController, flApi)
        self.navigationController = NavigationController(self.lightController, flApi, triggerMixerTracksScan)
        self.patternController = PatternController(flApi)
        self.loopModeController = LoopModeController(flApi)
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

