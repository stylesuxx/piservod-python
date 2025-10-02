class PiServoDError(Exception):
    """Base exception for piservod errors"""
    pass


class InvalidChannelError(PiServoDError):
    """Channel number out of range"""
    pass


class InvalidGPIOError(PiServoDError):
    """Invalid GPIO pin number"""
    pass


class ChannelNotConfiguredError(PiServoDError):
    """Channel must be set up first"""
    pass


class PulseOutOfRangeError(PiServoDError):
    """Pulse value outside configured range"""
    pass


class InvalidRangeError(PiServoDError):
    """Range validation failed"""
    pass


class NotConnectedError(PiServoDError):
    """Not connected to daemon"""
    pass
