# Changelog

All notable changes to the **Innova Fancoil Climate Control** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-11-09

### ✨ Added
* **Water Temperature $T_2$ Threshold Controls (#6)**:
  * Added **Minimum Water Temperature Heating ($L_{LO}$)** (`Register 510` on `n273025d` / `Register 218` on `n273025c`, $20.0\ ^\circ\text{C} \text{ to } 50.0\ ^\circ\text{C}$) and **Maximum Water Temperature Cooling ($L_{HI}$)** (`Register 511` / `Register 219`, $5.0\ ^\circ\text{C} \text{ to } 25.0\ ^\circ\text{C}$) across the Home Assistant integration (`number` entities), `innova-modbus` library, and standalone ESPHome YAML packages.
* **Filomuro Multi-Position Flap Control (`Register 457`)**:
  * Added `InnovaFlapMode` (`auto` -> `0`, `position_1` -> `1`, `position_2` -> `2`, `position_3` -> `3`, `swing` -> `7`).
  * Added dedicated **Flap Position** (`select`) entity and multi-position `swing_modes` on the **Thermostat** (`climate`) entity so Filomuro and Airleaf dampers can be opened fully (`Position 3`), held at intermediate angles (`Position 1` / `Position 2`), returned to `Auto`, or set to `Oscillating Swing` (`7`).
* **Display LED & Setpoint Range Controls (`n273025d`)**:
  * Added **Turn Off Display LED** (`switch`, Program Register `553` Bit 11) for bedroom stealth mode.
  * Added **Web Minimum Setpoint ($SP_{L,W}$)** (`Register 453`) and **Web Maximum Setpoint ($SP_{H,W}$)** (`Register 454`) configuration `number` entities.
* **Home Assistant 2026.11 Marketplace & Quality Scale Updates**:
  * Updated `hacs.json` (`homeassistant: "2025.1.0"`), added `"loggers"` to `manifest.json` for 1-click UI debug logging, redacted network host/IP in `diagnostics.py`, and updated documentation for the Home Assistant Marketplace transition.

### 🐛 Fixed & Optimized
* **Fixed Filomuro Halfway-Opening Flap Bug**: Previously, toggling Flap Swing ON wrote `1` (`Position 1` = fixed 45° / halfway open on Filomuro) instead of `7` (`Oscillating Swing`).
* **Fixed Operational Status, Fan Status & `HVACAction` Decoding**:
  * Parsed Program Register (`553` / `201`) before Status Register (`150` / `104`) so `power_on` is always synchronized before evaluating status bits.
  * Prioritized Water-Wait Fan-Stop status bits (`Bits 2–6` on modern, `Bits 2–4` on legacy) over active Cooling/Heating bits (`Bits 0–1`), accurately reporting `HVACAction.IDLE` and `"Fan Stopped (Water T2 too cold/warm...)"` when the unit is waiting on heat pump water temperature.
  * Reported `"Stopped (Target reached)"` for `fan_status_description` when the room setpoint is satisfied and `fan_rpm == 0`.
* **Eliminated Post-Write UI Bounce**: Added `async_notify_write(delay=2.0)` to `InnovaCoordinator` so optimistic state updates broadcast immediately while debouncing the hardware follow-up poll by 2.0 seconds until the PCB settles.
* **Fast / Slow Register Polling & Optional Register Fallback**: Split Modbus reads into fast telemetry batches (every poll) and slow configuration batches (every 6th poll or after writes), cutting RS485 traffic by ~43% and gracefully handling older firmware revisions that reject optional registers (`218–219`, `457`, `510–511`).
* **Legacy `n273025c` Decoding Parity**: Unified float rounding, disconnected probe detection (`<= -30.0 °C`), window contact polarity, and `web_*` supervisor flags between modern and legacy boards.

---

## [1.0.0] - 2026-08-31

### 🚀 Major Architectural Milestone: Native Home Assistant HACS Integration

This release introduces a native Home Assistant Custom Integration and a lightweight dual-mode ESPHome bridge architecture, eliminating heavy microcontroller C++ compilation while unlocking 1-click HACS updates.

### ✨ Added
* **Native Home Assistant Custom Integration (`custom_components/innova_climate/`)**:
  * Full climate thermostat entity supporting `Off`, `Heat`, `Cool`, `Auto` modes.
  * Real-time HVAC action state reporting (`heating`, `cooling`, `idle`, `off`).
  * Precise 0.5 °C temperature stepping (16.0 °C to 30.0 °C).
  * Fan modes (`Auto`, `Low / Night`, `High / Max`) and presets (`Sleep`, `Boost`, `None`).
  * Sensors: Room Temperature ($T_1$), Inlet Water Temperature ($T_2$), Coil Water Temperature ($T_3$), Relative Humidity ($RH$).
  * Dynamic diagnostic sensors: Operating status, fan speed status, alarm fault codes, and firmware version ($v1.9$).
  * Binary sensors: Problem alarm sensor, window contact ($IN1$), and temperature probe connectivity ($T_2$, $T_3$).
  * Controls: Remote Supervisor Mode switch, touch keypad lock switch, motorized flap swing switch, room temp calibration offset slider ($-1.2\ ^\circ\text{C}$ to $+1.2\ ^\circ\text{C}$), and manual refresh button.
  * Event entity: Dispatches Home Assistant bus events and automation triggers for alarms, fault clearances, and air filter maintenance.
* **Dual-Mode ESPHome Stream Server Bridge (`examples/`)**:
  * Pre-configured for **M5Stack NanoC6** (`m5nanoc6-serial-proxy.yaml`) and **M5Stack Atom Lite** (`m5atom-serial-proxy.yaml`).
  * Runs Modbus RTU-over-TCP stream server on **port 8899** alongside native ESPHome API serial proxy and Bluetooth BLE Proxy.
* **Standalone `innova-modbus` Python Device Library (`innova_modbus/`)**:
  * Async Python library with automated hardware board family detection (`n273025d` modern & `n273025c` legacy bridge).
  * Cross-version PyModbus compatibility supporting PyModbus 3.8 through 3.13+ (`device_id` / `slave` / `unit` keyword adaptation).
  * Comprehensive Pytest unit test suite with 100% test coverage.
* **Hardware-Aware Smart Sensor Filtering**:
  * Automatically filters out unconnected hardware probes on 2-pipe fancoil systems (such as unused $T_3$ coil probes returning $-51.0\ ^\circ\text{C}$ open circuit and uninstalled $RH$ humidity sensors).
* **Brand Assets & Translations**:
  * High-resolution icons and logos (`icon.png`, `icon@2x.png`) for Home Assistant and HACS.
  * Complete Material Design Icons mapping (`icons.json`).
  * 100% dual-language localization in **Dutch (`nl.json`)** and **English (`en.json`)**.
* **Centralized 8-Chapter Technical Wiki (`docs/wiki/`)**:
  * Complete documentation covering thermodynamics, continuous inverter BLDC regulation, low-temp heat pump operation ($< 30^\circ\text{C}$ water), Modbus register maps, and step-by-step setup guides.
* **Automated GitHub Actions CI**:
  * Official Home Assistant Hassfest validation, HACS action validation, Pytest matrix (Python 3.12 & 3.13), and ESPHome configuration tests.

### 🛡️ Backwards Compatibility
* Preserved legacy standalone ESPHome C++ components (`components/innova_climate/`) and packages (`packages/`) for users who wish to keep their existing on-device C++ setups without recompilation overhead.
