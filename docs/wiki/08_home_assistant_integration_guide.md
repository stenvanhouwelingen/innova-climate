# Chapter 8: Home Assistant Integration Guide

This guide explains how to install, configure, and operate the **Innova Fancoil Climate Control** integration in Home Assistant using the modern **Serial Proxy / Modbus TCP Bridge** architecture.

---

## 1. Architecture: Why ESPHome Serial / TCP Bridge?

Instead of compiling and uploading heavy C++ code to individual microcontrollers:
1. **The Microcontroller (M5Stack Atom Lite / NanoC6 / etc.)** runs a lightweight, generic ESPHome Serial / TCP Stream Server on port `8899`.
2. **Home Assistant** handles all Innova Modbus register decoding, climate state machines, thermostat presets, and diagnostic sensors.
3. **Firmware updates are eliminated**: You update your fancoil integration via Home Assistant or HACS with a single click.

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

### Option A: Via HACS (Custom Repository)
1. In Home Assistant, open **HACS** $\rightarrow$ **Integrations**.
2. Click the three dots in the upper right corner $\rightarrow$ **Custom repositories**.
3. Add `https://github.com/stenvanhouwelingen/innova-climate` with category **Integration**.
4. Click **Download**, then restart Home Assistant.

### Option B: Manual Installation
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
* **Target Temperature**: Adjustable in 0.5 °C increments (16.0 °C to 30.0 °C)
* **Current Temperature**: Real-time room air temperature from probe T1

### Sensors
* **Inlet Water Temperature (T2)**: Return water temperature (°C)
* **Coil Water Temperature (T3)**: Internal heat exchanger coil temperature (°C) (automatically hidden if not present)
* **Relative Humidity**: Room humidity percentage (if optional sensor is fitted)
* **Diagnostics / Status**: Real-time operating state and alarm fault strings
* **Firmware Version**: Readout of on-board Innova firmware version (e.g. `v1.9`)

### Binary Sensors
* **Alarm Status**: Problem binary sensor alerting when fancoil reports an error code.
* **Window Contact**: Reports if window/auxiliary contact (IN1) is open or closed.
* **Probe Connected (T2 / T3)**: Connectivity sensors for temperature probes.

### Switches, Numbers & Controls
* **Room Temperature Calibration Offset (`number`)**: Slider for T1 sensor offset (-1.2 °C to +1.2 °C).
* **Remote Supervisor Mode (`switch`)**: Locks local buttons so Home Assistant has sole authority.
* **Keypad Lock (`switch`)**: Locks the physical on-board touch screen.
* **Flap Swing (`switch`)**: Toggles motorized louver oscillation (Filomuro models).
* **Manual Refresh (`button`)**: Force immediate poll from fancoil.
* **Alarm Events (`event`)**: Home Assistant event entity firing on alarm or filter maintenance alerts.
