# name=nano-controls-fl-studio
# url=https://github.com/JulienMeziere/nano-kontrol-2-fl-studio

from device import *
from midi import *
from transport import *
from arrangement import *
from mixer import *
from general import *
from ui import *
from controllers.managers.general_controls_manager import GeneralControlsManager
from controllers.managers.tracks_manager import TracksManager
from core.fl_studio_api import FLStudioAPI
from core.hardware_interface import HardwareInterface
from core.constants import *


def OnInit():
    print("*** nanoKONTROL2 script v1 by Julien MEZIERE ***")
    global tracksManager
    global controlsManager
    global hardwareInterface
    global flApi
    
    flApi = FLStudioAPI({
        'midiOutMsg': midiOutMsg,
        'MIDI_CONTROLCHANGE': MIDI_CONTROLCHANGE,
        'globalTransport': globalTransport,
        'start': start,
        'stop': stop,
        'record': record,
        'rewind': rewind,
        'fastForward': fastForward,
        'isPlaying': isPlaying,
        'isRecording': isRecording,
        'getLoopMode': getLoopMode,
        'setLoopMode': setLoopMode,
        'showWindow': showWindow,
        'hideWindow': hideWindow,
        'getSongPos': getSongPos,
        'setSongPos': setSongPos,
        'currentTime': currentTime,
        'selectionStart': selectionStart,
        'selectionEnd': selectionEnd,
        'liveSelection': liveSelection,
        'getTrackName': getTrackName,
        'isTrackArmed': isTrackArmed,
        'armTrack': armTrack,
        'isTrackMuted': isTrackMuted,
        'muteTrack': muteTrack,
        'isTrackSolo': isTrackSolo,
        'soloTrack': soloTrack,
        'setTrackVolume': setTrackVolume
    })
    hardwareInterface = HardwareInterface(flApi)
    
    tracksManager = TracksManager(hardwareInterface, flApi)
    controlsManager = GeneralControlsManager(
        hardwareInterface, flApi, tracksManager.scanMixerTrackNames)


def OnProjectLoad():
    tracksManager.scanMixerTrackNames()


def OnRefresh(flag):
    if flag == HW_Dirty_LEDs or flag == HW_DIRTY_LEDS_ALTERNATIVE:
        controlsManager.updateButtonStates()


def OnControlChange(event):
    event.handled = True
    button = event.data1

    if button >= TRACKS_FIRST_FADER and button <= TRACKS_LAST_FADER:  # Handle mixer faders
        tracksManager.volumeFader(event.data1, event.data2)
    elif button >= TRACKS_FIRST_BUTTON and button <= TRACKS_LAST_BUTTON:  # Handle S,M,R buttons
        if event.data2 == 0:
            return

        # trackButton = 0 --> 'S' button (Solo)
        # trackButton = 1 --> 'M' button (Mute)
        # trackButton = 2 --> 'R' button (Arm/Record)
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
    elif event.data2 > 0:  # PRESS START
        controlsManager.onPressStart(button)
