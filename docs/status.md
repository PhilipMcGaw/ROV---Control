# ROV Control current status

## Architecture

The Control service is a separate Linux/Raspberry Pi Python process. It drives hardware and exchanges the NATS Core contract with other ROV services. It must remain independent of the Cockpit web process.

## Implemented behaviour

- Python control-service entry point under `src/rov_control/main.py`.
- NATS-based command and telemetry boundary as described in the NATS documentation and the master context.
- Profile-driven browser-assisted clock synchronisation: Control validates the NATS message against the active profile and can call Linux `time.clock_settime` when its systemd service has `CAP_SYS_TIME`.
- Hardware-oriented configuration and deployment scripts are present in `configs/` and `scripts/`.

## Automated-test verification

The documentation currency audit is implemented in `tests/test_documentation.py` and runs without application dependencies. `tests/test_time_synchronisation.py` verifies profile-subject and message validation without hardware. The historical files under `tests/legacy/` are not an automated acceptance suite.

## Bench-tested and Production-validated status

The repository does not currently record physical propulsion, GPIO, serial-board, sensor, clock-synchronisation, or production deployment validation. These statuses require explicit evidence and must not be inferred from source-code presence.

## Planned or unverified

- Full automated control-loop and hardware-abstraction test coverage.
- Bench validation of command limits, neutral, timeout, emergency-stop, and camera-pitch feedback.
- Production validation on the intended Raspberry Pi and attached hardware.
- Raspberry Pi bench validation of browser-assisted time synchronisation and the deployed `CAP_SYS_TIME` service capability.

## Important references

- `MASTER_CONTEXT.md`
- `docs/documentation-policy.md`
- `docs/nats.md`
- `docs/hardware.md`
- `docs/testing.md`
- `src/rov_control/main.py`
- `src/rov_control/time_sync.py`
- `configs/python.service`
- `scripts/1_install_dependencies.bat`
- `scripts/2_start_app.bat`
