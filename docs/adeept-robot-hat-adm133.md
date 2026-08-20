# Adeept Robot HAT ADM133 topic map

## Status and scope

The Adeept Robot HAT ADM133 is planned as a shared Control hardware adapter
for K9 and PiWars. This document defines the logical NATS contract before the
driver is implemented. It is not evidence of a working board, wiring map, or
safe motor operation.

The manufacturer's current Robot HAT V3.3 material lists four DC-motor
drivers, 16 PCA9685 servo outputs, six analogue-to-digital converter (ADC)
inputs, a three-channel line sensor port, ultrasonic and MPU6050 ports, light
tracking, infrared receiver, RGB/WS2812 lighting, a buzzer, UART, and I2C.
See the [official product specification](https://www.adeept.com/adeept-robot-hat-v30-for-raspberry-pi_p0429.html)
and [official tutorial and code archive](https://www.adeept.com/learn/detail-84.html).
The exact revision fitted to a robot must be confirmed before deployment.

## Boundary

Cockpit publishes and presents only logical profile topics. Control validates
them, applies its safe state, limits, calibration, mixing, and channel mapping,
then drives the ADM133. No client may publish any of the following:

- raw GPIO writes;
- raw I2C or UART transfers;
- PCA9685 channel numbers or pulse widths;
- DC motor-channel demands;
- direct battery-charger or power-control demands.

The active profile binds a board function to named entries in its `commands`
and `telemetry` objects. The subject itself appears only in that canonical
entry, preventing a second, conflicting topic definition.

```json
{
  "hardware": {
    "adapters": [{
      "id": "main-hat",
      "driver": "adeept-robot-hat-adm133",
      "model": "ADM133",
      "validation_status": "planned-unverified",
      "bindings": {
        "dc-motor-drive": { "commands": ["drive.throttle", "drive.steering"] },
        "adc-battery": { "telemetry": ["battery_percentage", "battery_voltage"] }
      }
    }]
  }
}
```

Control must reject an incomplete, unknown, stale, or unsafe command. The
adapter must leave motor outputs neutral until Control has completed profile
validation and entered an explicitly safe enabled state.

## Logical topic map

`<namespace>` is the active profile namespace, for example `k9` or `piwars`.
The exact logical keys that are enabled for a robot are profile configuration;
unneeded capabilities are not exposed merely because the HAT has a connector.

| ADM133 function | Profile binding and resolved topic | Value contract and Control responsibility |
| --- | --- | --- |
| Up to four DC-motor drivers | `drive.throttle`, `drive.steering` → `<namespace>.command.drive.throttle`, `<namespace>.command.drive.steering` | `-100–100 %` logical demands. Control performs drive mixing, direction, ramping, channel assignment, neutral, timeout, and emergency-stop behaviour. |
| PCA9685 servo outputs | Robot-specific actuator commands, such as K9 `head.pan`, `head.tilt` → `<namespace>.command.animatronics.head.pan`, `<namespace>.command.animatronics.head.tilt` | Degrees relative to the configured logical home. Control applies servo calibration and physical limits, and may publish an explicitly documented commanded-position telemetry value. |
| ADC battery measurement | `battery_voltage`, `battery_percentage` → `<namespace>.telemetry.power.battery.voltage`, `<namespace>.telemetry.power.battery.percentage` | Voltage is `V`; state of charge is `0–100 %`. Control owns ADC scaling, calibration, filtering, and battery safety thresholds. |
| Other ADC inputs | A configured logical sensor, for example `analogue.<id>.voltage` → `<namespace>.telemetry.sensors.analogue.<id>.voltage` | `V` after Control calibration. Raw ADC counts are diagnostic-only and, if published, use `count` with a documented ADC resolution. |
| Three-channel line sensor | PiWars `line_left`, `line_centre`, `line_right` → `<namespace>.telemetry.sensors.line.left`, `.centre`, `.right` | Boolean or `0`/`1` detection values. The profile must document the active polarity before enabling autonomous behaviour. |
| Ultrasonic range sensor | `distance_front` → `<namespace>.telemetry.sensors.distance.front` | Metres. Control validates timeout and out-of-range readings; it must not report an invalid reading as a valid obstacle distance. |
| MPU6050 accelerometer/gyroscope port | Optional `attitude.roll`, `attitude.pitch` → `<namespace>.telemetry.navigation.attitude.roll`, `.pitch` | Degrees after sensor fusion and installation calibration. The MPU6050 has no magnetometer, so this board function alone must not publish a heading. |
| Light-tracking sensor | Optional `light_tracking_detected` → `<namespace>.telemetry.sensors.light-tracking.detected` | Boolean detection value with configured polarity. Its electrical interface and polarity must be confirmed before activation. |
| Infrared receiver | Optional `ir_code` → `<namespace>.telemetry.inputs.ir.code` | A profile-approved, explicitly documented code encoding. No receiver code is defined until the receiver and library are selected. |
| RGB LED ports and WS2812 outputs | Optional `indicator.<id>.set` → `<namespace>.command.indicator.<id>.set` | A JSON colour/effect request defined by the profile. Control limits brightness, pattern rate, and output count; it does not accept a raw GPIO/PWM demand. |
| Buzzer | Optional `buzzer.pattern` → `<namespace>.command.notification.buzzer.pattern` | A profile-approved named pattern. It is a short notification device, not K9's sound-file speaker; `sound.play` remains a separate audio contract. |
| UART and I2C expansion ports | No raw bus topic | A dedicated Control driver for each attached device defines its own semantic command and telemetry topics. |
| Battery charger and power input | No control topic | They are electrical safety functions, not remotely commandable interfaces. Power-state monitoring may be exposed only through validated telemetry. |

Control may publish the adapter's health on
`<namespace>.control.status.hardware.adeept-robot-hat`. The status object must
identify the active profile and report safe initialisation, missing hardware,
and communication/configuration faults without exposing a direct actuation
path.

## Initial profile bindings

The current shared profiles validate only the functions selected for their
robots:

- K9: DC drive, head pan/tilt servos, and battery measurement.
- PiWars: DC drive, battery measurement, all three line-sensor channels, and
  front ultrasonic range.

These bindings are configuration contracts, not an ADM133 driver
implementation. No channel allocations have been recorded and no electrical,
motor, servo, sensor, or power behaviour is bench-tested.

## Required bring-up evidence

Before changing the status, record the board revision, Raspberry Pi model and
operating system, wiring/channel map, power source and fusing, calibration,
input polarity, software revision, and test results. Begin with motors
disconnected or mechanically made safe. Test one output and one sensor class at
a time, verify neutral and timeout behaviour, then test the physical emergency
stop before a robot is operated.
