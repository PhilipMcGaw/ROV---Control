# NATS contract

NATS Core is the service-to-service transport for Cockpit, Control, Datalogger, and HiL/SiL. The default local endpoint is `nats://127.0.0.1:4222`.

Subjects are namespaced by service and function. Units and scaling are SI, and robot-specific hardware mappings belong in the robot profile and Control service rather than in Cockpit.

This document records the transport boundary; individual service repositories define the subjects they implement.
