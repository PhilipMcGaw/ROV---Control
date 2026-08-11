# NATS subject contract

NATS Core is the internal shared data contract between the SBC, boards, Cockpit, and future services such as Datalogger. Payloads are generally strings, even when they represent numbers or booleans. NATS subjects use dots as separators; the legacy slash-separated names below map directly to dot-separated subjects. Cockpit connects to NATS server-side and forwards selected updates to browsers over `/ws/telemetry`; browsers do not connect directly to the server.

## Topic families

| Family | Legacy key / NATS subject | Direction |
|---|---|---|
| System | `system/uptime`, `system/time`, `system/network/...` | SBC → MQTT |
| Power | `power/battery/1/soc`, `power/battery/1/voltage` | Power board → SBC |
| AHRS | `sensor/ahrs/imu/heading`, `sensor/ahrs/imu/pitch` | AHRS → SBC |
| Water | `sensor/water/temperature`, `sensor/water/depth` | Sensor board → SBC |
| Motors | `output/motor/motor1/speed/demand` | SBC ↔ motor board |
| Lights | `out/left`, `out/right`, `out/laser` | SBC → light board |

The complete and historically accumulated table is in the root `README.md` and `dbc.xlsx`. Verify live code and board firmware before adding or renaming a topic.

## Serial bridge format

Board firmware communicates using newline-delimited records:

```text
<ADLER16_TOPIC_ID>:<PAYLOAD>\n
```

For example:

```text
05C0:127
```

The Adler-16 ID corresponds to the full lower-case legacy key. The transport adapter maps slash-separated board keys to dot-separated NATS subjects. Board firmware periodically repeats values and sends changed values immediately.

## Units and scaling

Some values use integer scaling to avoid floating-point transport. Confirm the topic table before displaying or commanding a value. Known examples include voltage, current, temperature, salinity, and depth values represented as a value divided by 10.

## Adding a topic

1. Define the topic, direction, payload type, unit, and frequency.
2. Add it to the relevant firmware topic table and calculate its Adler-16 ID.
3. Add the producer/consumer mapping in `Control/main.py` or the relevant board code.
4. Add Cockpit display/API mapping if it is operator-visible.
5. Update `README.md`, `dbc.xlsx`, and this document as appropriate.
6. Test with NATS publisher/subscriber tooling before connecting hardware.

## Service reliability

Keep the Control service and Cockpit as separate processes. Use NATS reconnect handling and explicit local safety state; NATS Core does not provide MQTT retained messages or QoS semantics. The Control service must enforce command ranges, timeouts, neutral output, and emergency-stop behaviour independently of Cockpit. Persistent recording belongs in Datalogger/SQLite, not JetStream.
