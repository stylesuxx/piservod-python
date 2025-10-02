import socket
from typing import Tuple, Dict, Union

from piservod.errors import (
    PiServoDError,
    NotConnectedError,
    InvalidChannelError,
    InvalidGPIOError,
    ChannelNotConfiguredError,
    PulseOutOfRangeError,
    InvalidRangeError,
)


class PiServoD:
    """
    Client for communicating with the piservod daemon.

    Args:
        socket_path: Path to the Unix domain socket (default: /tmp/piservod.sock)
        timeout: Socket timeout in seconds (default: 1.0)
    """

    BUFFER_SIZE = 1024

    def __init__(self, socket_path: str = '/tmp/piservod.sock', timeout: float = 1.0):
        self.socket_path = socket_path
        self.timeout = timeout
        self._socket = None

    def connect(self) -> None:
        """
        Establish connection to the daemon.

        Raises:
            PiServoDError: If the daemon is not running or connection fails
        """
        if self._socket is not None:
            return

        try:
            self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self._socket.settimeout(self.timeout)
            self._socket.connect(self.socket_path)

        except FileNotFoundError:
            raise PiServoDError(
                f"Cannot connect to piservod at {self.socket_path}. "
                "Is the daemon running? (sudo piservod)"
            )

        except Exception as e:
            raise PiServoDError(f"Connection failed: {e}")

    def is_connected(self) -> bool:
        """
        Check if currently connected to the daemon.

        Returns:
            True if connected, False otherwise
        """
        return self._socket is not None

    def disconnect(self) -> None:
        """Close connection to the daemon"""
        if self._socket:
            self._socket.close()
            self._socket = None

    def setup(self, channel: int, gpio: int) -> bool:
        """
        Setup a servo channel on a specific GPIO pin.

        Args:
            channel: Channel number (0-7)
            gpio: GPIO pin number (0-27)

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            InvalidGPIOError: If GPIO pin number is invalid
            PiServoDError: If communication with daemon fails
        """
        response = self._send_command(f"SETUP {channel} GPIO {gpio}")
        return response == "OK"

    def enable(self, channel: int) -> bool:
        """
        Enable PWM output on a channel.

        Args:
            channel: Channel number (0-7)

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        response = self._send_command(f"ENABLE {channel}")
        return response == "OK"

    def disable(self, channel: int) -> bool:
        """
        Disable PWM output on a channel.

        Args:
            channel: Channel number (0-7)

        Returns:
            True on success

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        response = self._send_command(f"DISABLE {channel}")
        return response == "OK"

    def set_range(self, channel: int, min_pulse: int, max_pulse: int) -> bool:
        """
        Set the pulse width range for a channel.

        Args:
            channel: Channel number (0-7)
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
        response = self._send_command(f"SET {channel} RANGE {min_pulse} {max_pulse}")
        return response == "OK"

    def set_pulse(self, channel: int, pulse: int) -> bool:
        """
        Set the pulse width for a channel.

        Args:
            channel: Channel number (0-7)
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
        response = self._send_command(f"SET {channel} PULSE {pulse}")
        return response == "OK"

    def get_range(self, channel: int) -> Tuple[int, int]:
        """
        Get the pulse width range for a channel.

        Args:
            channel: Channel number (0-7)

        Returns:
            Tuple of (min_pulse, max_pulse) in microseconds

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        # Response format: "RANGE 1000 2000"
        response = self._send_command(f"GET {channel} RANGE")
        parts = response.split()
        return (int(parts[1]), int(parts[2]))

    def get_pulse(self, channel: int) -> int:
        """
        Get the current pulse width for a channel.

        Args:
            channel: Channel number (0-7)

        Returns:
            Current pulse width in microseconds

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        # Response format: "PULSE 1500"
        response = self._send_command(f"GET {channel} PULSE")
        return int(response.split()[1])

    def get_state(self, channel: int) -> Dict[str, Union[int, bool]]:
        """
        Get the current state of a channel.

        Args:
            channel: Channel number (0-7)

        Returns:
            Dictionary with keys: 'gpio', 'enabled'

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range (0-7)
            ChannelNotConfiguredError: If channel has not been setup yet
            PiServoDError: If communication with daemon fails
        """
        # Response format: "GPIO 17 ENABLE 1"
        response = self._send_command(f"GET {channel} STATE")
        parts = response.split()
        return {
            'gpio': int(parts[1]),
            'enabled': bool(int(parts[3]))
        }

    def _send_command(self, command: str) -> str:
        """
        Send a command to the daemon and return the response.

        Args:
            command: Command string to send

        Returns:
            Response string from daemon

        Raises:
            NotConnectedError: If not connected to daemon
            InvalidChannelError: If channel number is out of range
            InvalidGPIOError: If GPIO pin number is invalid
            ChannelNotConfiguredError: If channel has not been setup
            PulseOutOfRangeError: If pulse value is out of range
            InvalidRangeError: If range validation fails
            PiServoDError: If communication fails or daemon returns unknown error
        """
        if self._socket is None:
            raise NotConnectedError("Not connected to daemon. Call connect() first.")

        try:
            self._socket.sendall(f"{command}\n".encode())
            response = self._socket.recv(self.BUFFER_SIZE).decode().strip()

            if response.startswith("ERROR"):
                self._raise_error(response)

            return response

        except socket.timeout:
            raise PiServoDError("Command timeout - daemon not responding")

        except Exception as e:
            raise PiServoDError(f"Communication error: {e}")

    def _raise_error(self, error_response: str) -> None:
        """
        Parse error response and raise appropriate exception.

        Args:
            error_response: Error message from daemon

        Raises:
            InvalidChannelError: If channel number is invalid
            InvalidGPIOError: If GPIO pin is invalid
            ChannelNotConfiguredError: If channel not configured
            PulseOutOfRangeError: If pulse value out of range
            InvalidRangeError: If range validation fails
            PiServoDError: For any other error
        """
        error_msg = error_response[6:].strip()  # Remove "ERROR " prefix

        if "Invalid channel" in error_msg:
            raise InvalidChannelError(error_msg)
        elif "Invalid GPIO" in error_msg:
            raise InvalidGPIOError(error_msg)
        elif "not configured" in error_msg:
            raise ChannelNotConfiguredError(error_msg)
        elif "out of range" in error_msg:
            raise PulseOutOfRangeError(error_msg)
        elif "min must be less than max" in error_msg:
            raise InvalidRangeError(error_msg)
        else:
            raise PiServoDError(error_msg)

    def __enter__(self) -> "PiServoD":
        """
        Context manager entry - establish connection.

        Returns:
            Self for use in with statement

        Raises:
            PiServoDError: If connection fails
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - close connection"""
        self.disconnect()
