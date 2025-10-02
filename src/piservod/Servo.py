from typing import Optional, Tuple, Dict, Union

from piservod.PiServoD import PiServoD
from piservod.errors import PiServoDError


class Servo:
    """
    High-level servo control interface with shared daemon connection.

    The daemon connection is shared across all Servo instances as a class variable.
    Call Servo.connect() once before creating any servos.

    Args:
        channel: Channel number (0-7)
        gpio: GPIO pin number (optional, only needed if not already setup)
        min_pulse: Minimum pulse width in microseconds (default: 1000)
        max_pulse: Maximum pulse width in microseconds (default: 2000)

    Example:
        Servo.connect()

        servo1 = Servo(channel=0, gpio=17)
        servo2 = Servo(channel=1, gpio=27)

        servo1.enable()
        servo2.enable()

        servo1.set_pulse(1500)
        servo2.set_pulse(1800)

        Servo.disconnect()
    """

    # Class variables shared across all instances
    _daemon: Optional[PiServoD] = None

    @classmethod
    def connect(cls, socket_path: str = '/tmp/piservod.sock', timeout: float = 1.0) -> None:
        """
        Establish connection to the daemon (shared across all Servo instances).

        Args:
            socket_path: Path to the Unix domain socket
            timeout: Socket timeout in seconds

        Raises:
            PiServoDError: If the daemon is not running or connection fails
        """
        if cls._daemon is None:
            cls._daemon = PiServoD(socket_path, timeout)

        cls._daemon.connect()

    @classmethod
    def disconnect(cls) -> None:
        """Close connection to the daemon"""
        if cls._daemon:
            cls._daemon.disconnect()

    @classmethod
    def is_connected(cls) -> bool:
        """
        Check if connected to daemon.

        Returns:
            True if connected, False otherwise
        """
        return cls._daemon is not None and cls._daemon.is_connected()

    def __init__(
        self,
        channel: int,
        gpio: int,
        min_pulse: int = 1000,
        max_pulse: int = 2000
    ):
        """
        Create a servo instance.

        Args:
            channel: Channel number (0-7)
            gpio: GPIO pin number
            min_pulse: Minimum pulse width in microseconds
            max_pulse: Maximum pulse width in microseconds

        Raises:
            PiServoDError: If not connected to daemon or setup fails
        """
        if self._daemon is None or not self._daemon.is_connected():
            raise PiServoDError(
                "Not connected to daemon. Call Servo.connect() before creating servos."
            )

        self.channel = channel
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse

        self._setup(gpio)
        self.set_range(min_pulse, max_pulse)

    def enable(self) -> bool:
        """
        Enable PWM output for this servo.

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.enable(self.channel)

    def disable(self) -> bool:
        """
        Disable PWM output for this servo.

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.disable(self.channel)

    def set_range(self, min_pulse: int, max_pulse: int) -> bool:
        """
        Set the pulse width range for this servo.

        Args:
            min_pulse: Minimum pulse width in microseconds
            max_pulse: Maximum pulse width in microseconds

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            InvalidRangeError: If min_pulse >= max_pulse
            PiServoDError: If communication with daemon fails
        """
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        return self._daemon.set_range(self.channel, min_pulse, max_pulse)

    def set_pulse(self, pulse: int) -> bool:
        """
        Set the pulse width for this servo.

        Args:
            pulse: Pulse width in microseconds

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PulseOutOfRangeError: If pulse is outside the configured min/max range
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.set_pulse(self.channel, pulse)

    def get_range(self) -> Tuple[int, int]:
        """
        Get the pulse width range for this servo.

        Returns:
            Tuple of (min_pulse, max_pulse) in microseconds

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.get_range(self.channel)

    def get_pulse(self) -> int:
        """
        Get the current pulse width for this servo.

        Returns:
            Current pulse width in microseconds

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.get_pulse(self.channel)

    def get_state(self) -> Dict[str, Union[int, bool]]:
        """
        Get the current state of this servo.

        Returns:
            Dictionary with keys: 'gpio' (int), 'enabled' (bool)

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.get_state(self.channel)

    # Convenience methods - not part of the actual daemon

    def is_enabled(self) -> bool:
        """
        Check if this servo is enabled.

        Returns:
            True if enabled, False otherwise

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        state = self.get_state()
        return state['enabled']

    def center(self) -> bool:
        """
        Move this servo to center position.

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PulseOutOfRangeError: If center pulse is outside configured range
            PiServoDError: If communication with daemon fails
        """
        center_pulse = (self.min_pulse + self.max_pulse) // 2
        return self.set_pulse(center_pulse)

    def _setup(self, gpio: int) -> bool:
        """
        Setup this servo channel on a specific GPIO pin.

        Args:
            gpio: GPIO pin number

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            InvalidGPIOError: If GPIO pin number is invalid
            PiServoDError: If communication with daemon fails
        """
        return self._daemon.setup(self.channel, gpio)

    def __enter__(self) -> "Servo":
        """
        Context manager entry - enables PWM.

        Returns:
            Self for use in with statement

        Raises:
            PiServoDError: If enable fails
        """
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - disable servo"""
        self.disable()
