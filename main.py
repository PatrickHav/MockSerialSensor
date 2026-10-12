"""Mock Modbus RTU sensor for testing an RS-485 IoT gateway."""

from __future__ import annotations

import argparse
import logging
import math
import time
from argparse import Namespace

from pymodbus import FramerType, ModbusDeviceIdentification
from pymodbus.simulator import DataType, SimData, SimDevice
from pymodbus.server import StartSerialServer

REGISTER_COUNT = 10


async def update_sensor_values(
    _function_code: int,
    _start_address: int,
    _address: int,
    _count: int,
    registers: list[int],
    _set_values: list[int] | list[bool] | None,
) -> None:
    """Refresh simulated readings before a gateway reads the registers."""
    elapsed = time.monotonic() % (2 * math.pi * 100)
    temperature = round(22.0 + 2.0 * math.sin(elapsed / 10.0), 1)
    humidity = round(48.0 + 8.0 * math.sin(elapsed / 14.0), 1)
    registers[0] = int(temperature * 10)
    registers[1] = int(humidity * 10)


def build_device(slave_id: int, identity: ModbusDeviceIdentification) -> SimDevice:
    """Create a single-slave datastore with holding registers at address 0."""
    return SimDevice(
        id=slave_id,
        simdata=SimData(
            address=0,
            count=REGISTER_COUNT,
            values=0,
            datatype=DataType.REGISTERS,
        ),
        action=update_sensor_values,
        identity=identity,
    )


def parse_args() -> Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial device path")
    parser.add_argument("--slave-id", type=int, default=1, help="Modbus slave ID")
    parser.add_argument("--baudrate", type=int, default=9600)
    parser.add_argument("--bytesize", type=int, choices=(5, 6, 7, 8), default=8)
    parser.add_argument("--parity", choices=("N", "E", "O"), default="N")
    parser.add_argument("--stopbits", type=float, choices=(1, 1.5, 2), default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 1 <= args.slave_id <= 247:
        raise ValueError("--slave-id must be between 1 and 247")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "MockSerialSensor",
            "ProductCode": "MSS-01",
            "ProductName": "Mock RS-485 Sensor",
            "MajorMinorRevision": "1.0",
        }
    )
    device = build_device(args.slave_id, identity)
    logging.info(
        "Starting Modbus RTU sensor on %s (slave=%s, %s baud, %s%s%s)",
        args.port,
        args.slave_id,
        args.baudrate,
        args.bytesize,
        args.parity,
        args.stopbits,
    )
    logging.info("Holding register 0 = temperature x10 C; register 1 = humidity x10 %%")
    StartSerialServer(
        device,
        framer=FramerType.RTU,
        port=args.port,
        baudrate=args.baudrate,
        bytesize=args.bytesize,
        parity=args.parity,
        stopbits=args.stopbits,
        identity=identity,
    )


if __name__ == "__main__":
    main()
