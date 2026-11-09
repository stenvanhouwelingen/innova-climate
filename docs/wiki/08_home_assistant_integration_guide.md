# Chapter 8: Home Assistant Integration Guide

This guide explains how to install, configure, and operate the **Innova Fancoil Climate Control** integration in Home Assistant using the modern **Serial Proxy / Modbus TCP Bridge** architecture.

---

## 1. Architecture: Why ESPHome Serial / TCP Bridge?

Instead of compiling and uploading heavy C++ code to individual microcontrollers:
1. **The Microcontroller (M5Stack Atom Lite / NanoC6 / etc.)** runs a lightweight, generic ESPHome Serial / TCP Stream Server on port `8899`.
2. **Home Assistant** handles all Innova Modbus register decoding, climate state machines, thermostat presets, and diagnostic sensors.
3. **Microcontroller compilation overhead is eliminated**: You update your fancoil integration via Home Assistant Marketplace with a single click, completely avoiding ESPHome C++ compile overhead, firmware re-flashing, and ESPHome `modbus_controller` polling deprecations (such as `skip_updates`).

---

## 2. Hardware Wiring

### M5Stack RS485 Unit Hookup
1. Connect the **M5Stack RS485 Unit** to your microcontroller's **Grove Port**:
   * **M5Stack Atom Lite**: TX=26, RX=32, 5V, GND
   * **M5Stack NanoC6**: TX=2, RX=1, 5V, GND
2. Wire the RS-485 transceiver screw terminals to the Innova fancoil board:
   * **A** (Transceiver) $\rightarrow$ **B** (Fancoil Modbus B)
   * **B** (Transceiver) $\rightarrow$ **A** (Fancoil Modbus A)
   * **GND** (Transceiver) $\rightarrow$ **GND** (Fancoil Modbus Shield / GND)

> [!IMPORTANT]
> The RS-485 transmission lines must be crossed (`A` to `B` and `B` to `A`) for communication to function properly.

---

## 3. Flash the ESPHome Firmware

1. Open `examples/m5nanoc6-serial-proxy.yaml` (or `m5atom-serial-proxy.yaml`).
2. Flash the firmware onto your M5Stack device via USB or OTA:
   ```bash
   esphome run examples/m5nanoc6-serial-proxy.yaml
   ```
3. Once powered, Home Assistant will automatically discover the ESPHome device.

---

## 4. Install the Home Assistant Integration

> [!NOTE]
> **Marketplace vs HACS**:
> Starting in **Home Assistant 2026.11**, HACS is natively integrated directly into Home Assistant Core as the **Marketplace** (accessible via **Settings > Marketplace**). Both workflows use the same underlying repository catalog and are supported.

### Option A: Via Home Assistant Marketplace (Recommended for HA 2026.11+)

[![Open your Home Assistant instance and open a repository in the Marketplace.](https://my.home-assistant.io/badges/marketplace_repository.svg)](https://my.home-assistant.io/redirect/marketplace_repository/?owner=stenvanhouwelingen&repository=innova-climate&category=integration)

1. Click the 1-click badge above, or navigate in Home Assistant to **Settings** $\rightarrow$ **Marketplace**.
2. Click the three dots (overflow menu) in the top-right $\rightarrow$ **Custom repositories**.
3. Enter `https://github.com/stenvanhouwelingen/innova-climate` with category **Integration**.
4. Click **Download**, then restart Home Assistant when prompted.

### Option B: Via HACS (For Home Assistant Versions Prior to 2026.11)
1. In Home Assistant, open **HACS** $\rightarrow$ **Integrations**.
2. Click the three dots in the upper right corner $\rightarrow$ **Custom repositories**.
3. Add `https://github.com/stenvanhouwelingen/innova-climate` with category **Integration**.
4. Click **Download**, then restart Home Assistant.

### Option C: Manual Installation
1. Copy the `custom_components/innova_climate` folder into your Home Assistant `/config/custom_components/` directory.
2. Restart Home Assistant.

---

## 5. Adding the Integration in Home Assistant

1. In Home Assistant, navigate to **Settings** $\rightarrow$ **Devices & Services** $\rightarrow$ **Add Integration**.
2. Search for **Innova Fancoil Climate Control**.
3. Choose your connection type:
   * **Modbus TCP / Network Bridge (Recommended)**:
     * **Host**: `192.168.1.80` (or your device hostname/IP)
     * **Port**: `8899` (default for ESPHome Stream Server)
     * **Slave ID**: `1`
     * **Board Family**: `Modern (OSMO, AirLeaf, FÄRNA, Filomuro M7/PU)` or `Legacy (Filoterra, INN-FR-B32)`
   * **Physical Serial Port**:
     * Select your USB RS-485 transceiver device from the drop-down.
     * Set Baud Rate to `9600`.
4. Click **Submit**. Your fancoil climate entity and all sensors will be created automatically!

---

## 6. Available Entities & Controls

### Climate Entity (`climate.innova_fancoil_thermostat`)
* **HVAC Modes**: `Off`, `Heat`, `Cool`, `Auto`
* **Fan Modes**: `Auto`, `Low` (Night/Silent), `High` (Max/Boost)
* **Preset Modes**: `Sleep` (Silent Mode), `Boost` (Max Speed), `None` (Auto)
* **Swing Modes (Modern / Filomuro)**: `Auto (Default)`, `Position 1 (45° / Halfway)`, `Position 2 (Horizontal)`, `Position 3 (Fully Open)`, `Oscillating Swing`
* **Target Temperature**: Adjustable in 0.5 °C increments (16.0 °C to 30.0 °C)
* **Current Temperature**: Real-time room air temperature from probe T1

### Sensors
* **Inlet Water Temperature (T2)**: Return water temperature (°C)
* **Coil Water Temperature (T3)**: Internal heat exchanger coil temperature (°C) (automatically hidden if not present)
* **Relative Humidity**: Room humidity percentage (if optional sensor is fitted)
* **Diagnostics / Status**: Real-time operating state and alarm fault strings (e.g., `Heating`, `Heating (Waiting for water)`, `Stopped (Target reached)`)
* **Firmware Version**: Readout of on-board Innova firmware version (e.g. `v1.9`)

### Binary Sensors
* **Alarm Status**: Problem binary sensor alerting when fancoil reports an error code.
* **Window Contact**: Reports if window/auxiliary contact (IN1) is open or closed.
* **Probe Connected (T2 / T3)**: Connectivity sensors for temperature probes.

### Switches, Numbers & Controls
* **Room Temperature Calibration Offset (`number`)**: Box control for T1 sensor offset (-1.2 °C to +1.2 °C).
* **Minimum Water Temperature Heating (`number`)**: Configurable $T_2$ water temperature threshold for heating (`LLO`, 10.0 °C to 50.0 °C; Register 510 on modern boards, Register 218 on legacy boards).
* **Maximum Water Temperature Cooling (`number`)**: Configurable $T_2$ water temperature threshold for cooling (`LHI`, 10.0 °C to 35.0 °C; Register 511 on modern boards, Register 219 on legacy boards).
* **Web Minimum / Maximum Setpoint Limits (`number`)**: Hardware setpoint bounds (`SPL_W` / `SPH_W`, disabled by default).
* **Remote Supervisor Mode (`switch`)**: Locks local buttons so Home Assistant has sole authority.
* **Keypad Lock (`switch`)**: Locks the physical on-board touch screen.
* **Turn Off Display LED (`switch`)**: Turns off the fancoil's bright onboard display LED at night.
* **Flap Position (`select`)**: Directly selects the motorized louver position (`Auto`, `Position 1`, `Position 2`, `Position 3`, `Oscillating Swing`) on Filomuro models.
* **Flap Swing (`switch`)**: Toggles motorized louver oscillation (disabled by default in favor of `Flap Position` and Thermostat `swing_modes`).
* **Manual Refresh (`button`)**: Force immediate poll from fancoil.
* **Alarm Events (`event`)**: Home Assistant event entity firing on alarm or filter maintenance alerts.
