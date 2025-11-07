class FLStudioAPI:
    """Wrapper for FL Studio API functions to enable dependency injection"""
    
    def __init__(self, api_functions):
        """
        api_functions: dict containing all FL Studio API functions
        Example: {'midiOutMsg': midiOutMsg, 'globalTransport': globalTransport, ...}
        """
        for name, func in api_functions.items():
            setattr(self, name, func)
    
    def sendMidiMessage(self, message_type, channel, data1, data2):
        """Send a MIDI message"""
        self.midiOutMsg(message_type, channel, data1, data2)

