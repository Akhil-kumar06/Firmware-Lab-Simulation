# FirmwareLab — Milestone 1

A hardware-free embedded control portfolio project. Portable C11 implements a temperature controller; Python provides the desktop dashboard and test automation. All temperatures, sensors and fan outputs are simulated.

**This milestone does not use FreeRTOS, concurrent tasks, hardware interrupts or a real watchdog.** It is the tested control-logic foundation for the next milestone. Do not describe it as STM32 hardware or RTOS experience yet. Simulation time is explicit and is not a measurement of real-time performance.

## Start on Windows (recommended: Ubuntu in WSL2)

If WSL is not installed, run `wsl --install` in an Administrator PowerShell, restart if requested, then open Ubuntu and finish its user setup. GUI execution needs working WSLg (normally Windows 11); otherwise use the command-line demo or run Python/Tk and GCC natively.

In Ubuntu:

```bash
sudo apt update
sudo apt install build-essential python3 python3-tk unzip
```

Extract this ZIP, then open a terminal in the extracted `FirmwareLab` directory. In WSL, Windows files are accessible under `/mnt/c/Users/YOUR_NAME/Downloads/`.

```bash
python3 build.py
python3 dashboard.py
```

No pip packages, cloud services, account, or hardware required. On Linux use the same commands; on macOS install the command-line developer tools and a Python distribution with Tk, then run them. Native Windows needs GCC or Clang on PATH and Python with Tk; use `python build.py` and `python dashboard.py`. Only Linux GCC execution has been validated in the supplied build.

## First demonstration

1. Start the dashboard: RUNNING, approximately 30 C.
2. Click Disconnect sensor: FAULT, SENSOR_INVALID, fan 100%.
3. Click Normal / recover: recovery requires 10 healthy samples below 65 C.
4. Click Freeze samples: SENSOR_STALE after the sample age exceeds 500 ms.
5. Click Normal, then Increase heat: WARNING at 65 C, OVERTEMP at 80 C.
6. Click Normal: the simulated plant cools; recovery waits until it is below 65 C, then counts 10 good samples.

The plot shows the latest 240 readings. One request advances 100 ms of simulated time; GUI scheduling is deliberately not treated as a real-time guarantee. A sensor read failure commands full cooling in this model even when disabled. This is an educational policy, not a validated safety design.

## Command-line demo / record data

```bash
python3 demo.py > telemetry.jsonl
```

This sends normal operation, disconnection, recovery, stale samples, heating and cooldown to the compiled C executable. Each output line is JSON. No GUI needed.

## Architecture

`dashboard.py` sends commands -> `src/main.c` advances plant and sample models -> `src/controller.c` evaluates state and fan command -> JSON telemetry returns to dashboard.

The controller has no OS dependencies, allocation, file I/O or global mutable state. It can be tested separately and later called by an RTOS control task. Sensor invalidity takes priority over staleness, which takes priority over overtemperature. Fault recovery is debounced; warning uses hysteresis. Temperature is a float in degrees C, fan output is 0..1, timestamps are milliseconds.

## Files to study in order

1. `src/controller.h`: interface and state definitions.
2. `src/controller.c`: control policy, fault priority, recovery and hysteresis.
3. `tests/test_controller.c`: boundaries and failure cases.
4. `src/main.c`: model and line-oriented host transport.
5. `dashboard.py`: subprocess transport and visualization.
6. `tests/test_integration.py`: end-to-end scenario tests.

## Your first coding exercises

- Change warning thresholds to 60 C / 55 C. Update the tests and explanation.
- Add a FAN_STUCK fault using commanded versus simulated actual fan speed.
- Add a fault counter without counting every tick as a new incident.
- Export state transitions with timestamps to a separate event log.

Make one small Git commit per change and explain your reasoning. Understand and modify the starter before presenting it in interviews. It is appropriate to describe this as an AI-assisted personal project with your tested contributions identified.

## Next milestone: real FreeRTOS host integration

Use an official supported host port and pin a kernel version. Separate sensor, control, telemetry and health tasks; pass timestamped readings through bounded queues. Define ownership, priorities and overflow policy. Add task heartbeat fault injection and measure recovery in simulated ticks. No stub RTOS API is included here. Then port to a supported emulated MCU or physical board if desired.

## Verification and limits

`python3 build.py` compiles with strict warnings, runs controller checks, then five integration tests. The long-run test advances one **simulated** hour rapidly, not one hour of physical runtime. Tests cover disconnect recovery, stale samples, overtemperature, normal long-run behaviour and clean quit. The desktop GUI requires local Tk/display support and was not visually tested in the headless build environment. No hardware behaviour or real-time scheduling is established by these tests.

The thermal model is intentionally simple, sensor noise is omitted, and the CLI is a trusted local test interface. Out-of-range plant values are treated as invalid sensor readings. It is not intended to control real machinery.
