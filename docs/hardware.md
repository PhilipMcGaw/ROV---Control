# Hardware interfaces

The main pin and bus reference is [Pins.md](../Pins.md). The KiCad projects under `KiCAD/` are the authoritative source for board-level connectivity.

## Interfaces in use

- UART serial links to navigation and attached controllers.
- I2C for sensors, analogue input, PWM output, and EEPROM devices.
- SPI for selected IMU and magnetometer devices.
- GPIO for status, leak detection, and control signals.
- PWM through PCA9685 or board-specific outputs.

## RS485 microcontroller links

Control owns communication with RS485-attached microcontrollers. Cockpit must not open serial devices or implement RS485 framing. Control shall translate validated NATS commands into the microcontroller protocol and publish validated microcontroller telemetry back to namespaced NATS subjects.

The implementation must document the selected electrical interface and transceiver, UART device, baud rate, parity, stop bits, bus termination and biasing, node addressing, frame format, payload encoding, CRC or checksum, half-duplex direction control, response timeout, retry policy, startup discovery, and behaviour when a node becomes unavailable. Until these details are confirmed against the hardware, the RS485 interface is planned and must not be described as bench-tested or production-ready.

The bus design should avoid multiple transmitters speaking at once. Control remains the bus coordinator unless the selected protocol explicitly provides another arbitration method. A lost or malformed RS485 response must not bypass Control safety limits or prevent the hardware loop from entering its safe state.

## Hardware safety

- Disconnect or inhibit thrusters before software changes are tested.
- Start actuator demands at zero and verify that command direction is correct.
- Test lights, servos, and H-bridges unloaded before wet testing.
- Verify battery voltage, current limits, fusing, polarity, and leak detection independently.
- Never rely on a browser control timeout as the only motor safety mechanism.

## Command and actuator boundary

Cockpit maps human inputs to namespaced logical robot commands such as `drive.forward` or ROV motion axes. Control is responsible for converting those logical commands into physical actuator demands. Direction, inversion, motor mixing, channel assignment, limits, ramps, neutral output, command timeouts, and emergency-stop handling must remain in Control and its robot-specific configuration. Hardware wiring must never be encoded in Cockpit input mappings.

Example:

```text
Cockpit: left-stick-y → drive.forward = 0.7
Control: drive.forward = 0.7 → left motor = 0.7, right motor = 0.7
```

The second mapping is illustrative only; actual values and signs must come from the active robot hardware configuration and must be verified with propulsion disabled.

## Hardware-dependent paths

Historical code uses Raspberry Pi device paths such as `/dev/serial/by-id/...`. These are machine-specific and should be discovered and documented on the deployed Pi rather than copied blindly from an old test script.
