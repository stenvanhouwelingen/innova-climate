# Innova Fancoil Climate Control for Home Assistant

[![Home Assistant Integration](https://img.shields.io/badge/Home%20Assistant-Integration-blue.svg)](docs/wiki/08_home_assistant_integration_guide.md)
[![HACS](https://img.shields.io/badge/HACS-Custom%20Integration-orange.svg)](custom_components/innova_climate)
[![Continuous Integration](https://github.com/stenvanhouwelingen/innova-climate/actions/workflows/ci.yaml/badge.svg)](https://github.com/stenvanhouwelingen/innova-climate/actions/workflows/ci.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Wiki](https://img.shields.io/badge/docs-Wiki-brightgreen.svg)](docs/wiki/Home.md)

Modern, native Home Assistant integration and lightweight serial proxy firmware for the complete **Innova Electronics Fancoil Ecosystem** (**OSMO, AirLeaf, Filomuro, Filoterra, and FÄRNA**).

<p align="center">
  <img src="custom_components/innova_climate/brand/icon@2x.png" width="160" alt="Innova Climate Logo">
</p>

> [!NOTE]  
> **Upgrading from the standalone ESPHome C++ Component?**  
> Your existing setups and configurations continue to work seamlessly! The legacy packages (`packages/`) and C++ components (`components/`) remain fully supported in this repository. We recommend migrating to the new **HACS Custom Integration** to benefit from 1-click updates, zero microcontroller compilation overhead, and automatic hardware probe filtering. See **[Chapter 8: Home Assistant Integration Guide](docs/wiki/08_home_assistant_integration_guide.md)** for a simple 2-minute migration guide.

---

## 🌟 Highlights & Features

* 🚀 **Native Home Assistant Integration (`innova_climate`)**: Direct UI configuration with auto-discovery, thermostat entity, diagnostic sensors, and calibration controls.
* ⚡ **Dual-Mode ESPHome Bridge (Port 8899)**: Lightweight ESPHome firmware for **M5Stack NanoC6** and **M5Stack Atom Lite** running Modbus RTU-over-TCP stream server + Bluetooth BLE Proxy.
* 🐍 **Standalone `innova-modbus` Python Library**: Async Python library built for PyModbus 3.8–3.13+ with automated register family detection (`n273025d` modern & `n273025c` legacy).
* 🌡️ **Smart Sensor Filtering**: Automatically hides unconnected hardware probes (e.g. T3 coil probe on 2-pipe systems or uninstalled relative humidity sensors).
* 🔧 **Calibration & Diagnostics**: Real-time water temperatures (T2 inlet), room temperature calibration slider (-1.2 to +1.2 °C), physical keypad locks, and supervisor mode.
* 📖 **Comprehensive Technical Wiki**: In-depth chapters on fancoil mechanics, sensor physics, heat pump low-temp heating curves, and Modbus register maps.

---

## 🗂️ Repository Structure

```text
├── custom_components/
│   └── innova_climate/       # Home Assistant Custom Component (HACS)
├── innova_modbus/            # Standalone Python device library & test suite
├── examples/                 # ESPHome Serial & TCP Stream Server configs (NanoC6 / Atom Lite)
├── docs/
│   └── wiki/                 # Complete 12-Chapter Technical Wiki & Integration Guide
└── hacs.json                 # HACS repository metadata
```

---

## 🚀 Quick Start Guide

### 1. Hardware Hookup (M5Stack Grove Port $\rightarrow$ Fancoil Modbus)

Connect the **M5Stack RS-485 Unit** to your microcontroller's **Grove Port**:
* **M5Stack Atom Lite**: TX = GPIO 26, RX = GPIO 32
* **M5Stack NanoC6**: TX = GPIO 2, RX = GPIO 1

Connect the RS-485 transceiver screw terminals to the fancoil PCB:
* **A** (Transceiver) $\rightarrow$ **B** (Fancoil Modbus B)
* **B** (Transceiver) $\rightarrow$ **A** (Fancoil Modbus A)
* **GND** (Transceiver) $\rightarrow$ **GND** (Fancoil Modbus Shield / GND)

> [!IMPORTANT]
> The RS-485 transmission lines must be crossed (`A` to `B` and `B` to `A`) for communication to function properly.

---

### 2. Flash the ESPHome Firmware

1. Create your `secrets.yaml` containing your Wi-Fi credentials (see `secrets.yaml.example`).
2. Flash your device via USB or OTA:
   * **For M5Stack NanoC6** (ESP32-C6):
     ```bash
     esphome run examples/m5nanoc6-serial-proxy.yaml
     ```
   * **For M5Stack Atom Lite** (ESP32):
     ```bash
     esphome run examples/m5atom-serial-proxy.yaml
     ```

---

### 3. Install in Home Assistant via HACS

1. In Home Assistant, open **HACS** $\rightarrow$ **Integrations** $\rightarrow$ **Custom repositories**.
2. Add `https://github.com/stenvanhouwelingen/innova-climate` with category **Integration**.
3. Click **Download**, then restart Home Assistant.
4. Go to **Settings** $\rightarrow$ **Devices & Services** $\rightarrow$ **Add Integration** $\rightarrow$ Search **Innova Fancoil Climate Control**.
5. Enter the IP address of your ESP32 device on port `8899` (default).

👉 For complete setup instructions, read **[Chapter 8: Home Assistant Integration Guide](docs/wiki/08_home_assistant_integration_guide.md)**.

---

## 📚 Technical Wiki & Documentation

Explore the **[Innova Fancoil Technical Knowledge Base](docs/wiki/Home.md)**:

1. [Chapter 1: Overview & Model Variants](docs/wiki/01_overview_and_models.md)
2. [Chapter 2: Internal Workings & Control Physics](docs/wiki/02_internal_workings_and_physics.md)
3. [Chapter 3: Sensors & Standalone Operation](docs/wiki/03_sensors_and_standalone_operation.md)
4. [Chapter 4: Heat Pumps & Low-Temperature Heating ($< 30^\circ\text{C}$ Water)](docs/wiki/04_heat_pumps_and_low_temp_heating.md)
5. [Chapter 5: Control Boards & DIP Switch Configurations](docs/wiki/05_control_boards_and_dip_switches.md)
6. [Chapter 6: Remote Supervisor Mode](docs/wiki/06_remote_supervisor_mode.md)
7. [Chapter 7: Modbus Register Deep Dive & Bitmasks](docs/wiki/07_modbus_register_deep_dive.md)
8. [Chapter 8: Home Assistant Integration Guide](docs/wiki/08_home_assistant_integration_guide.md)

---

## 🧪 Testing & Validation

Run the standalone unit test suite locally:
```bash
PYTHONPATH=innova_modbus/src pytest innova_modbus/tests -v
```

---

## 📄 License & Disclaimer

* **License**: Released under the [MIT License](LICENSE).
* **Disclaimer**: This integration is an independent open-source project and is not affiliated with, authorized, maintained, sponsored, or endorsed by Innova S.r.l.
