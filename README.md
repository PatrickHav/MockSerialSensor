# Mock Serial Sensor

A small mock Modbus RTU sensor for testing an IoT gateway over an RS-485 serial connection. It uses [PyModbus](https://pymodbus.readthedocs.io/en/v3.16.1/) to behave like a single Modbus slave device and continuously updates simulated sensor values.

## What It Does

- Runs a Modbus RTU server on a serial device such as `/dev/ttyUSB0`.
- Responds as one configurable Modbus slave, with slave ID `1` by default.
- Publishes deterministic, changing temperature and humidity values.
- Uses `9600 8N1` serial settings by default.
- Supports standard PyModbus serial-server options through command-line arguments.

The server responds to gateway requests; it does not transmit unsolicited Modbus messages.

## Register Map

Holding registers use zero-based Modbus addresses:

| Address | Value | Encoding | Typical range |
| --- | --- | --- | --- |
| `0` | Temperature | Degrees Celsius multiplied by 10 | `200` to `240` |
| `1` | Relative humidity | Percent multiplied by 10 | `400` to `560` |
| `2`-`9` | Reserved | `0` | `0` |

For example, a register value of `225` represents `22.5 °C`, and `500` represents `50.0%` relative humidity.

## Requirements

- Python 3.10 or newer.
- An RS-485 serial adapter connected to the host, or a virtual serial-port pair for software-only testing.
- The gateway and mock sensor must use matching serial settings.

The Python dependencies are listed in [requirements.txt](requirements.txt).

## Running

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

A nix flake is also defined inside of the repository 

Start the mock sensor with the default settings:

```bash
python main.py --port /dev/ttyUSB0
```

A complete example with explicit settings:

```bash
python main.py \
  --port /dev/ttyUSB0 \
  --slave-id 1 \
  --baudrate 9600 \
  --bytesize 8 \
  --parity N \
  --stopbits 1
```

Press `Ctrl+C` to stop the server.

## Command-Line Options

| Option | Default | Description |
| --- | --- | --- |
| `--port` | `/dev/ttyUSB0` | Serial device path |
| `--slave-id` | `1` | Modbus slave ID, from `1` to `247` |
| `--baudrate` | `9600` | Serial baud rate |
| `--bytesize` | `8` | Number of data bits: `5`, `6`, `7`, or `8` |
| `--parity` | `N` | Parity: `N`, `E`, or `O` |
| `--stopbits` | `1` | Stop bits: `1`, `1.5`, or `2` |

See all options with:

```bash
python main.py --help
```

## Gateway Configuration

Configure the gateway to use:

- Protocol: Modbus RTU
- Serial port: the port connected to the mock sensor
- Slave/device ID: the value passed to `--slave-id`
- Baud rate, data bits, parity, and stop bits: the values passed to the matching options
- Function code: Read Holding Registers (`0x03`)
- Starting address: `0`
- Quantity: `2` or more registers

The mock sensor uses a real serial port. For testing without physical RS-485 hardware, connect the gateway and the mock process through a virtual null-modem serial-port pair, then pass one endpoint to each application.

## Development Checks

Compile the Python source without starting the serial server:

```bash
python -m py_compile main.py
```
