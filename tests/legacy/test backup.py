import logging
import os
import threading
import time
from datetime import datetime
from typing import Final

import ifaddr
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
import serial
from paho.mqtt.enums import CallbackAPIVersion, MQTTProtocolVersion

millis = lambda: int(round(time.time() * 1000))

logger = logging.getLogger(__name__)

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


mqtt_data = {}
mqtt_lock = threading.Lock()


def on_connect(client, userdata, flags, reason_code, properties):
    logger.info(f"Connected to MQTT broker with result code {reason_code}")
    client.subscribe("#")


def on_message(client, userdata, message):
    with mqtt_lock:
        mqtt_data[message.topic] = message.payload.decode()


mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def main() -> None:
    try:
        mqtt_client.connect("localhost")
        mqtt_client.loop_start()
        logger.info("MQTT client started")
    except Exception as error:
        logger.info(f"Failed to connect to MQTT broker: {error}")

    lastdata = "foo"
    lastsystem_uptime = "foo"
    lastsystem_time = "foo"
    lastsystem_date = "foo"

    lights_left_laststate = "foo"
    lights_left_lasttime = 0
    lights_right_laststate = "foo"
    lights_right_lasttime = 0
    lights_aux1_laststate = "foo"
    lights_aux1_lasttime = 0
    lights_aux2_laststate = "foo"
    lights_aux2_lasttime = 0
    lights_laser_laststate = "foo"
    lights_laser_lasttime = 0
    lights_toggle_laststate = "foo"
    lights_toggle_lasttime = 0

    # Open the serial port
    logger.info("Opening Serial Ports")

    # serial1 = serial.Serial('/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0', 115200, timeout=1)
    serial2 = serial.Serial(
        "/dev/serial/by-id/usb-Arduino_LLC_Arduino_Leonardo-if00", 115200, timeout=1
    )
    serial3 = serial.Serial(
        "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75433313739351C03152-if00",
        115200,
        timeout=1,
    )

    time.sleep(2)  # Wait for connection
    logger.info("I assume it worked… need to see what happens if it fails…")

    try:
        while True:
            #    if serial1.in_waiting > 0:
            #        data = serial1.readline().decode('utf-8').strip()

            if serial2.in_waiting > 0:
                data = serial2.readline().decode("utf-8").strip()

            if serial3.in_waiting > 0:
                data = serial3.readline().decode("utf-8").strip()

            if data != lastdata:
                lastdata = data
                topic = data.split(":")[0]
                message = data.split(":")[1]
                publish.single(f"{topic}", f"{message}", hostname="localhost")
                logger.info(f"Posting {topic}:{message} to MQTT")

            system_uptime = mqtt_data.get("system/uptime", "N/A")
            system_time = mqtt_data.get("system/time", "N/A")
            system_date = mqtt_data.get("system/date", "N/A")

            lights_left = mqtt_data.get("output/lights/left/demand", "N/A")
            lights_right = mqtt_data.get("output/lights/right/demand", "N/A")
            lights_aux1 = mqtt_data.get("output/lights/aux1/demand", "N/A")
            lights_aux2 = mqtt_data.get("output/lights/aux2/demand", "N/A")

            lights_laser = mqtt_data.get("output/lights/laser/demand", "N/A")
            lights_nav = mqtt_data.get("output/lights/nav/demand", "N/A")
            lights_strobe = mqtt_data.get("output/lights/strobe/demand", "N/A")
            lights_strobe_frequency = mqtt_data.get(
                "output/lights/strobe/frequency", "N/A"
            )
            lights_toggle = mqtt_data.get("output/lights/toggle", "N/A")

            if system_uptime != lastsystem_uptime:
                lastsystem_uptime = system_uptime
                logger.info(f"Getting system/uptime:{system_uptime} from MQTT")
            if system_time != lastsystem_time:
                lastsystem_time = system_time
                logger.info(f"Getting system/time:{system_time} from MQTT")
            if system_date != lastsystem_date:
                lastsystem_date = system_date
                logger.info(f"Getting system/date:{system_date} from MQTT")

            if lights_left != lights_left_laststate or millis() >= lights_left_lasttime:
                lights_left_laststate = lights_left
                lights_left_lasttime = millis() + 5000
                #        serial1.write(b"output/lights/left/demand:{lights_left}\\n")
                serial2.write(b"output/lights/left/demand:{lights_left}\\n")
                serial3.write(b"output/lights/left/demand:{lights_left}\\n")
                logger.info(
                    f"Getting output/lights/left/demand:{lights_left} from MQTT"
                )

            if (
                lights_right != lights_right_laststate
                or millis() >= lights_right_lasttime
            ):
                lights_right_laststate = lights_right
                lights_right_lasttime = millis() + 5000
                #        serial1.write(b"output/lights/right/demand:{lights_right}\\n")
                serial2.write(b"output/lights/right/demand:{lights_right}\\n")
                serial3.write(b"output/lights/right/demand:{lights_right}\\n")
                logger.info(
                    f"Getting output/lights/right/demand:{lights_right} from MQTT"
                )

            if lights_aux1 != lights_aux1_laststate or millis() >= lights_aux1_lasttime:
                lights_aux1_laststate = lights_aux1
                lights_aux1_lasttime = millis() + 5000
                #        serial1.write(b"output/lights/aux1/demand:{lights_aux1}\\n")
                serial2.write(b"output/lights/aux1/demand:{lights_aux1}\\n")
                serial3.write(b"output/lights/aux1/demand:{lights_aux1}\\n")
                logger.info(
                    f"Getting output/lights/aux1/demand:{lights_aux1} from MQTT"
                )

            if lights_aux2 != lights_aux2_laststate or millis() >= lights_aux2_lasttime:
                lights_aux2_laststate = lights_aux2
                lights_aux2_lasttime = millis() + 5000
                #        serial1.write(b"output/lights/aux2/demand:{lights_aux2}\\n")
                serial2.write(b"output/lights/aux2/demand:{lights_aux2}\\n")
                serial3.write(b"output/lights/aux2/demand:{lights_aux2}\\n")
                logger.info(
                    f"Getting output/lights/aux2/demand:{lights_aux2} from MQTT"
                )

            if (
                lights_laser != lights_laser_laststate
                or millis() >= lights_laser_lasttime
            ):
                lights_laser_laststate = lights_laser
                lights_laser_lasttime = millis() + 5000
                #        serial1.write(b"output/lights/laser/demand:{lights_laser}\\n")
                serial2.write(b"output/lights/laser/demand:{lights_laser}\\n")
                serial3.write(b"output/lights/laser/demand:{lights_laser}\\n")
                logger.info(
                    f"Getting output/lights/laser/demand:{lights_laser} from MQTT"
                )

            if (
                lights_toggle != lights_toggle_laststate
                or millis() >= lights_toggle_lasttime
            ):
                lights_toggle_laststate = lights_toggle
                lights_toggle_lasttime = millis() + 5000
                #        serial1.write(b"output/lights/toggle/demand:{lights_test}\\n")
                serial2.write(b"output/lights/toggle/demand:{lights_test}\\n")
                serial3.write(b"output/lights/toggle/demand:{lights_test}\\n")
                logger.info(
                    f"Getting output/lights/toggle/demand:{lights_toggle} from MQTT"
                )

    except KeyboardInterrupt:
        logger.info("Closing Serial Ports")
        # serial1.close()
        serial2.close()
        serial3.close()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("Exitited due to Keyboard Interuption")


if __name__ == "__main__":
    main()
