# ROV control service

`src/rov_control/main.py` is the hardware-facing Python service. It reads MQTT demands, drives servo and H-bridge outputs, samples analogue channels, and forwards serial-board data to MQTT.

Run locally on macOS/Linux with:

```bash
./run.sh
```

The service is run as the `rov_control` package and expects the project `.venv`, a local MQTT broker, and target hardware. Windows/macOS development should use mock or disconnected hardware; GPIO, I2C, SPI, PWM, and serial behaviour is Raspberry Pi/Linux-specific.

Do not run this service against connected propulsion hardware without following `docs/testing.md`. The control service must remain independent from Cockpit so a web or database failure cannot directly stop or destabilise the hardware loop.
