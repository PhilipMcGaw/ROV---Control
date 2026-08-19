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

## Browser-assisted time synchronisation

The active shared profile may define browser-assisted system-clock synchronisation for an RPi without an RTC. The standard subjects are:

```text
<namespace>.cockpit.command.system.time-sync
<namespace>.control.status.system.time-sync
```

Cockpit publishes the command only after an authenticated `driver` or `admin` browser session begins and then every 60 seconds. It is a JSON message with UTC Unix milliseconds:

```json
{
  "value": 1767225600000,
  "units": "ms",
  "timestamp": "2026-01-01T00:00:00Z",
  "profile": "rov",
  "source": "cockpit-browser"
}
```

Control loads this configuration at boot from `/etc/robot/profile.json`. It accepts only the exact configured command subject, active profile, `ms` unit, and a UTC date between 2024 and 2100. The first correction may be large because an RPi without an RTC can start near 1970. Control makes no adjustment inside the configured threshold (default `0.5 s`) and publishes an `adjusted` or `within-tolerance` JSON status. It never requires that status as an acknowledgement for command or safety behaviour.

Only Control calls Linux `time.clock_settime`; the service requires the narrowly scoped `CAP_SYS_TIME` capability in `configs/python.service`. This feature is not a replacement for NTP when a trusted network time service exists.
