# ROV Control current status

## Architecture

The Control service is a separate Linux/Raspberry Pi Python process. It drives hardware and exchanges the NATS Core contract with other ROV services. It must remain independent of the Cockpit web process.

## Implemented behaviour

- Python control-service entry point under `src/rov_control/main.py`.
- NATS-based command and telemetry boundary as described in the NATS documentation and the master context.
- Hardware-oriented configuration and deployment scripts are present in `configs/` and `scripts/`.

## Automated-test verification

The documentation currency audit is implemented in `tests/test_documentation.py` and runs without application dependencies. The historical files under `tests/legacy/` are not an automated acceptance suite.

## Bench-tested and Production-validated status

The repository does not currently record physical propulsion, GPIO, serial-board, sensor, or production deployment validation. These statuses require explicit evidence and must not be inferred from source-code presence.

## Planned or unverified

- Full automated control-loop and hardware-abstraction test coverage.
- Bench validation of command limits, neutral, timeout, emergency-stop, and camera-pitch feedback.
- Production validation on the intended Raspberry Pi and attached hardware.

## Important references

- `MASTER_CONTEXT.md`
- `docs/documentation-policy.md`
- `docs/nats.md`
- `docs/hardware.md`
- `docs/testing.md`
- `src/rov_control/main.py`
- `configs/python.service`
- `scripts/1_install_dependencies.bat`
- `scripts/2_start_app.bat`
