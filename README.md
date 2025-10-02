# piservod-python

Python bindings for [piservod](https://github.com/stylesuxx/piservod) - a software PWM daemon for controlling servos on Raspberry Pi.

> **NOTE:** Requires piservod to be installed and running on the system!

## Installation

Install via pip:

```bash
pip install piservod
```

## Prerequisites

First, install and start the piservod daemon:

```bash
# Clone and build piservod
git clone https://github.com/stylesuxx/piservod.git
cd piservod
make
sudo make install

# Start the daemon
sudo piservod
```

## Usage

### Basic Example

```python
from piservod import Servo

# Connect to daemon (shared connection for all servos)
Servo.connect()

# Create and control a servo
servo = Servo(channel=0, gpio=5)
servo.enable()
servo.set_pulse(1500)  # Center position
servo.disable()

# Disconnect when done
Servo.disconnect()
```

### Multiple Servos

```python
from piservod import Servo

Servo.connect()

# Create multiple servos sharing the same connection
servo1 = Servo(channel=0, gpio=5)
servo2 = Servo(channel=1, gpio=6)
servo3 = Servo(channel=2, gpio=7)

# Control them independently
servo1.enable()
servo2.enable()
servo3.enable()

servo1.set_pulse(1000)
servo2.set_pulse(1500)
servo3.set_pulse(2000)

Servo.disconnect()
```

### Using Context Managers

```python
from piservod import Servo

Servo.connect()

# Servo automatically enabled on enter, disabled on exit
with Servo(channel=0, gpio=17) as servo:
    servo.set_pulse(1500)
    servo.center()  # Move to center position

Servo.disconnect()
```

### Custom Pulse Ranges

```python
from piservod import Servo

Servo.connect()

# Some servos use different pulse ranges
servo = Servo(channel=0, gpio=17, min_pulse=600, max_pulse=2400)
servo.enable()
servo.center()  # Uses the custom range

Servo.disconnect()
```

### Low-Level API

For more control, use the `PiServoD` class directly:

```python
from piservod import PiServoD

daemon = PiServoD()
daemon.connect()

# Setup channel
daemon.setup(channel=0, gpio=5)
daemon.set_range(channel=0, min_pulse=1000, max_pulse=2000)

# Control servo
daemon.enable(channel=0)
daemon.set_pulse(channel=0, pulse=1500)

# Query state
pulse = daemon.get_pulse(channel=0)
state = daemon.get_state(channel=0)
print(f"Current pulse: {pulse}μs")
print(f"Enabled: {state['enabled']}")

daemon.disconnect()
```

### Error Handling

```python
from piservod import Servo, PiServoDError, PulseOutOfRangeError

try:
    Servo.connect()
    servo = Servo(channel=0, gpio=5)
    servo.enable()
    servo.set_pulse(3000)  # Out of range

except PulseOutOfRangeError as e:
    print(f"Pulse out of range: {e}")
except PiServoDError as e:
    print(f"Error: {e}")
finally:
    Servo.disconnect()
```

## API Reference

### Servo Class

#### Class Methods
- `connect(socket_path='/tmp/piservod.sock', timeout=1.0)` - Connect to daemon
- `disconnect()` - Disconnect from daemon
- `is_connected()` - Check connection status

#### Instance Methods
- `enable()` - Enable PWM output
- `disable()` - Disable PWM output
- `set_pulse(pulse)` - Set pulse width in microseconds
- `set_range(min_pulse, max_pulse)` - Set pulse range
- `get_pulse()` - Get current pulse width
- `get_range()` - Get pulse range as tuple
- `get_state()` - Get servo state (gpio, enabled)
- `is_enabled()` - Check if servo is enabled
- `center()` - Move to center position

### PiServoD Class

Lower-level daemon interface with the same methods as Servo, but requires explicit channel parameter:

- `connect()` / `disconnect()` / `is_connected()`
- `setup(channel, gpio)` - Setup a channel
- `enable(channel)` / `disable(channel)`
- `set_pulse(channel, pulse)` / `get_pulse(channel)`
- `set_range(channel, min_pulse, max_pulse)` / `get_range(channel)`
- `get_state(channel)`

### Exception Types

- `PiServoDError` - Base exception
- `NotConnectedError` - Not connected to daemon
- `InvalidChannelError` - Invalid channel number (0-7)
- `InvalidGPIOError` - Invalid GPIO pin
- `ChannelNotConfiguredError` - Channel not setup
- `PulseOutOfRangeError` - Pulse value out of range
- `InvalidRangeError` - Invalid range values

## Development

### Setup
Clone, setup venv and install dev dependencies:

```bash
git clone https://github.com/stylesuxx/piservod-python.git
cd piservod-python
python -m venv ./.venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Releases

Pushing a new tag will create a new release on PyPI:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Links

- [piservod daemon](https://github.com/stylesuxx/piservod)
- [Issue tracker](https://github.com/stylesuxx/piservod-python/issues)
