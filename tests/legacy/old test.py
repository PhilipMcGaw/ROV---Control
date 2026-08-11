import logging
import os
import time
from datetime import datetime
from typing import Final

import ifaddr
import paho.mqtt.publish as publish
import serial
from paho.mqtt.enums import MQTTProtocolVersion


class SerialConnection:
    def __init__(self):
        self.ser = serial.Serial("/dev/ttyACM0", baudrate=115200)  # fake AHRS

    def read(self):
        self.ser.read()

    def __enter__(self):
        yield self

    def __exit__(self):
        self.ser.close()


logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    # logging.basicConfig(filename='myapp.log', level=logging.INFO)

    fast_loop: float = 0.0
    one_second_loop: float = 0.0
    slow_loop: float = 0.0
    _FAST_LOOP_TIME: Final[float] = 0.01  # 100 Hz
    _ONE_SECOND_LOOP_TIME: Final[int] = 1  # 1 Hz
    _SLOW_LOOP_TIME: Final[int] = 100  # 0.01 Hz

    while True:
        # https://pypi.org/project/paho-mqtt/#publish. - need to move from single to multiple (also should add username and password to MQTT broker)

        if time.monotonic() > fast_loop:
            is_this_working = time.monotonic()
            msgs = [
                {"topic": "output/motors/motor1/speed", "payload": "0"},
                ("output/motors/motor2/speed", f"{is_this_working}", 0, False),
                ("output/motors/motor3/speed", "0", 0, False),
                ("output/motors/motor4/speed", "0", 0, False),
                ("output/motors/motor5/speed", "0", 0, False),
                ("output/motors/motor6/speed", "0", 0, False),
                ("output/motors/motor7/speed", "0", 0, False),
                ("output/motors/motor8/speed", "0", 0, False),
                ("output/motors/motor9/speed", "0", 0, False),
                ("output/motors/motor10/speed", "0", 0, False),
                ("output/motors/motor11/speed", "0", 0, False),
                ("output/motors/motor12/speed", "0", 0, False),
            ]

            publish.multiple(
                msgs, hostname="localhost", protocol=MQTTProtocolVersion.MQTTv5
            )
            fast_loop = time.monotonic() + _FAST_LOOP_TIME

        if time.monotonic() > one_second_loop:
            logger.info(f" UPTIME: {uptime()}")
            msgs = [
                {
                    "topic": "system/time",
                    "payload": datetime.strftime(datetime.now(), "%H:%M:%S"),
                },
                ("system/date", time.strftime("%Y-%m-%d", time.gmtime())),
                ("system/uptime", uptime()),
                ("power/battery/1/soc", "10"),
                ("power/battery/1/voltage", "10.2", 0, False),
                ("power/battery/1/current", "5", 0, False),
                ("power/battery/1/temperature", "30", 0, False),
                ("sensor/water/temperature", "22", 0, False),
                ("sensor/water/salinity", "35", 0, False),
                ("sensor/water/depth", "550", 0, False),
                ("output/lights/left/demand", "100", 0, False),
                ("output/lights/right/demand", "25", 0, False),
                ("output/lights/aux1/demand", "0", 0, False),
                ("output/lights/aux2/demand", "0", 0, False),
                ("output/lights/laser/demand", "100", 0, False),
                ("output/lights/nav/demand", "100", 0, False),
                ("output/lights/strobe/demand", "0", 0, False),
                ("output/lights/toggle/demand", "100", 0, False),
            ]
            publish.multiple(
                msgs, hostname="localhost", protocol=MQTTProtocolVersion.MQTTv5
            )
            one_second_loop = time.monotonic() + _ONE_SECOND_LOOP_TIME

        if time.monotonic() > slow_loop:
            # all other stuff that doesn't change very often

            # IP Addresses
            adapters = ifaddr.get_adapters()
            messages: list[tuple[str, str]] = []
            for adapter in adapters:
                for i, ip in enumerate(adapter.ips, start=1):
                    messages.append(
                        (f"system/network/{adapter.nice_name}_{i}", f"{ip.ip}")
                    )

            publish.multiple(messages)

            slow_loop = time.monotonic() + _SLOW_LOOP_TIME


def uptime():
    with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
        min, sec = divmod(uptime_seconds, 60)
        hour, min = divmod(min, 60)
        day, hour = divmod(hour, 24)
    if day == 0:
        return "%02d:%02d:%02d" % (hour, min, sec)
    return "%dD %02d:%02d:%02d" % (day, hour, min, sec)


if __name__ == "__main__":
    main()
