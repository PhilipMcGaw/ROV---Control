# ROV Control — Master Context

## Purpose

The enforceable documentation policy is `docs/documentation-policy.md`, with contributor guidance in `CONTRIBUTING.md`, current status in `docs/status.md`, and checks in `tests/test_documentation.py` and `tests/documentation_change_policy.py` using `tests/documentation_change_policy.json`.

This repository contains the Raspberry Pi/SBC hardware control service for the ROV. It is intentionally separate from Cockpit so a web, media, authentication, or database problem cannot directly stop or destabilise the hardware loop.

## Runtime boundary

On Linux, clone this repository as `~/ROV - Control` beside the other ROV repositories. On macOS, use a user-selected workspace beneath the home directory, for example `~/Projects/ROV/ROV - Control`. This is a documented convention only; scripts must derive paths from their own location so the repository remains movable.

`src/rov_control/main.py` connects to the local Mosquitto MQTT broker, consumes actuator demands, drives servo and H-bridge outputs, samples analogue channels, and bridges serial-board messages to MQTT.

```text
MQTT broker
   ├─ demands → rov_control → GPIO / I2C / SPI / PWM / serial hardware
   └─ telemetry ← rov_control ← sensors and attached boards
```

Cockpit and future services communicate with this repository through the MQTT contract. Do not add web-server responsibilities or browser-specific code here.

## Important interfaces

- NATS Core server: `nats://127.0.0.1:4222` by default, configured with `NATS_URL`.
- Serial board protocol: newline-delimited `<ADLER16_TOPIC_ID>:<PAYLOAD>` records.
- Servo demands use topics such as `output/servos/camera/demand`.
- H-bridge demands use `output/hbridge/left/demand` and `output/hbridge/right/demand`.
- Sensor and system telemetry is published under the documented `sensor/*`, `power/*`, and `system/*` topic families.

The authoritative topic and unit references are in `docs/mqtt.md`, the parent ROV project, and `dbc.xlsx`. Check live firmware and board code before changing a topic.

## Hardware and safety

- This service targets Linux/Raspberry Pi hardware and cannot be fully validated on Windows or macOS.
- Test with propulsion disabled, disconnected, or mechanically restrained.
- Validate command ranges and units before writing outputs.
- Motor neutral, command timeout, emergency-stop, and safe startup behaviour must not depend on Cockpit.
- Keep physical power isolation available during every hardware test.
- Use stable `/dev/serial/by-id/` paths where possible.

## Repository layout

- `src/rov_control/` — live Python package.
- `configs/` — service configuration.
- `docs/` — control-service contracts, deployment, hardware, and testing guidance.
- `tests/legacy/` — historical experiments, not an automated acceptance suite.
- `scripts/` — Windows portable WinPython installation and startup scripts.

## Development

Install the repository requirements into a project environment, then run:

```bash
PYTHONPATH=src python -m rov_control.main
```

On the deployed Raspberry Pi, use the service launcher and systemd configuration in `run.sh` and `configs/python.service`. The service requires NATS Core to be available before it starts driving outputs.

On Windows, use `scripts/1_install_dependencies.bat` followed by `scripts/2_start_app.bat`. These require a local or mapped drive, install portable Python without administrator rights, and do not use `uv`. Hardware imports still require a compatible Linux/Raspberry Pi environment.

## Documentation rule
The shared robot-profile requirements are defined in the Cockpit repository's `docs/robot-profile-requirements.md` and apply to this Controller. The Controller loads the same robot profile as Cockpit, owns the robot namespace and physical actuator mappings, and remains authoritative for motor mixing, direction, limits, timeouts, neutral behaviour, and emergency stop. It must not rely on Cockpit for propulsion safety.

Control exchanges logical demands, hardware status, and telemetry with the co-installed Cockpit and Datalogger services through NATS Core. Datalogger failure must not block or destabilise the control loop.

Control must validate the shared profile during boot before enabling hardware outputs. If validation fails, the service must remain in a safe non-driving state and report the cause.

Robot profiles currently originate in the Cockpit repository under `configs/profiles/`. Control consumes the deployed active profile and must not maintain an independently edited mapping copy.

The shared runtime profile is initially `/etc/robot/profile.json` on the robot Raspberry Pi and is loaded during boot.

Control also owns the robot networking deployment configuration. Control may deploy the Raspberry Pi's approved network configuration and is responsible at runtime for network-link status, NATS connectivity, reconnect behaviour, and safe handling of command-link loss. Cockpit and Datalogger must not be required to configure or maintain the robot network.

For the current deployment model, Wi-Fi SSIDs and passwords, NATS credentials, service tokens, API keys, and other robot deployment secrets may be stored in a local Control secrets file within the repository workspace, provided that the file is listed in `.gitignore` and is never committed. Committed configuration shall contain only non-secret structure, defaults, and an example secrets template. The deployment must verify that credential files have restrictive permissions.

Update this file and the relevant `docs/` page whenever NATS subjects, payloads, units, hardware mappings, service paths, safety behaviour, dependencies, or test procedures change. Every change must include a consistency check of this file; if it is not a true reflection of current behaviour, correct it in the same change. Keep the control repository documentation aligned with the parent ROV integration project. Documentation must remain current, use formal British English, and be written for readers with an engineering degree or equivalent technical experience.

Where SI units are used, place a space between the numerical value and the unit symbol, for example `5 m`, `12 V`, and `20 °C`. Use the degree symbol `°` by preference for angles.

The verbose portable scripting standard applies equally to Windows batch/PowerShell scripts and POSIX shell scripts on macOS, Linux, and Raspberry Pi.
The Control service publishes `sensor/camera/main/pitch` whenever the camera servo demand is applied. The value is the commanded servo angle relative to the 90° home position, with `0°` representing straight ahead. This is command-derived rather than physical feedback and requires bench validation.
