# Changelog

All notable changes to the **Innova Fancoil Climate Control** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
