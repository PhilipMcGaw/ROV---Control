# NATS contract

NATS Core is the service-to-service transport for Cockpit, Control, Datalogger, and HiL/SiL. The default local endpoint is `nats://127.0.0.1:4222`.

Subjects are namespaced by service and function. Units and scaling are SI, and robot-specific hardware mappings belong in the robot profile and Control service rather than in Cockpit.

## Subject and payload convention

NATS does not impose an application payload format. The framework uses dot-separated hierarchical subjects:

```text
<robot-namespace>.<service>.<message-type>.<function>
```

Examples:

```text
rov.control.command.drive
rov.control.telemetry.motor
rov.cockpit.status.connection
rov.datalogger.status.health
```

Structured commands, telemetry, and status messages use JSON payloads. A normal structured payload contains the value, SI units where applicable, timestamp, and profile identity:

```json
{
  "value": 0.7,
  "units": "1",
  "timestamp": "2026-08-18T12:00:00Z",
  "profile": "rov"
}
```

NATS payloads remain arbitrary bytes at the transport level. Binary payloads may be used for specialised data, such as camera or compressed sensor data, but the subject must document the encoding explicitly. Cockpit may present subjects using slash-separated dashboard keys internally; that presentation does not change the NATS subject contract.

This document records the transport boundary; individual service repositories define the subjects they implement.

## Logical command example

Cockpit publishes a semantic command rather than a motor demand:

```json
{
  "command": "drive.forward",
  "value": 0.7,
  "profile": "rov",
  "units": "1"
}
```

Control validates the namespace, profile, range, freshness, and safety state, then applies the robot-specific motor or thruster mixer. Cockpit must not publish physical motor-channel commands as a substitute for the Control mapping.
