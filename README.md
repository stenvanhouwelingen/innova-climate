# ESPHome Innova Fancoil Integration (M7/PU)

This repository contains an ESPHome configuration and a custom C++ component to integrate **Innova fancoils** using **PU / on-board control** or **M7** series boards with Home Assistant via Modbus RTU (RS-485) using an **M5Stack Atom Lite** or **M5Stack NanoC6** and an **M5Stack RS485 Unit**.

The integration runs all climate control logic locally on the ESP32/ESP32-C6. It exposes a native Home Assistant `climate` entity, a local browser-based web panel, diagnostic sensors, and configuration entities.

---

## Supported Fancoil Models & Board Topologies

> [!NOTE]  
> **Tested & Verified**: This integration has been physically tested and verified on the **Innova OSMO Series** and **Innova AirLeaf Series** fancoils.
> 
> If you have successfully tested this integration on a different fancoil model, please let us know in the [Device Compatibility Category](https://github.com/stenvanhouwelingen/innova-climate/discussions/categories/device-compatibility) so we can update the list of verified hardware!

This integration is fully compatible with all fancoil models equipped with **Innova Electronics' M7 or PU control boards** (firmware default ID `1190` or compatible). The repository supports both main Modbus register families using ESPHome packages:

### 1. Board Family n273025d (Default/Newer)
* **Compatible Board Numbers**: `ECA789`, `PUB-30`, `EEB749`, `ECA844`, `ECA044`
* **Applicable Products**: Innova OSMO, AirLeaf, FÄRNA, and newer Filomuro versions.

### 2. Board Family n273025c (Older/Bridge Retrofits)
* **Compatible Board Numbers**: `INN-FR-B32` (Modbus bridge retrofit accessory card), `ECA644`, `ECA647`, `EDA649`, `EDB649`, `ESE645`, `ESE648`
* **Applicable Products**: Innova Filoterra, and older built-in / Slim Fit versions of AirLeaf and Filomuro.

### 3. Supported UI & Touchpads
* **On-Board Touchscreens**: ECA844II / EWA844II (Wi-Fi), ECA044II / EWA044II (Wi-Fi)
* **M7 Remote Wall Panels**: EEB749II (Standard) / EFB749II (Wi-Fi) / EGB749II (Bluetooth)
* **Smart Touch Panels**: EEA649II / EEB649II / EFA649II / EFB649II

---

## Hardware Requirements

1. **Innova-compatible Fancoil** (with PU on-board control or M7 wall control firmware).
2. **ESPHome Controller**: An ESP32 microcontroller (pre-configured for the **M5Stack Atom Lite** or the **M5Stack NanoC6**). In theory, any ESPHome-supported microcontroller board (ESP32/ESP8266) capable of Modbus RTU serial communication can be used.
3. **RS-485 Transceiver**: The **M5Stack RS485 Unit** (with automatic TX/RX direction switching built-in), or any standard RS-485 transceiver (such as MAX485).
4. **Wiring & Hookup Wires** to connect the transceiver to the fancoil's Modbus terminals.

---

## Wiring and Connections

### 1. ESP32 to RS-485 Converter (M5Stack Grove Port)
* Connect the M5Stack RS485 Unit to your ESP32's **Grove port** (Port A):
  * **M5Stack Atom Lite**:
    * **TX Pin (GPIO 26)** $\rightarrow$ RS485 Unit TX (Yellow Wire)
    * **RX Pin (GPIO 32)** $\rightarrow$ RS485 Unit RX (White Wire)
  * **M5Stack NanoC6**:
    * **TX Pin (GPIO 2)** $\rightarrow$ RS485 Unit TX (Yellow Wire)
    * **RX Pin (GPIO 1)** $\rightarrow$ RS485 Unit RX (White Wire)
  * **Power / GND**:
    * **5V Power** $\rightarrow$ RS485 Unit 5V (Red Wire)
    * **GND** $\rightarrow$ RS485 Unit GND (Black Wire)

> [!NOTE]  
> The M5Stack RS485 Unit has built-in hardware automatic flow control. There is **no need** to configure an RTS or `de_pin` in ESPHome.

### 2. RS-485 Converter to Innova Fancoil Board
Connect the screw terminals of the RS485 Unit to the fancoil's Modbus port:
1. **A** (Converter) $\rightarrow$ **B** (Fancoil Modbus B)
2. **B** (Converter) $\rightarrow$ **A** (Fancoil Modbus A)
3. **GND** (Converter) $\rightarrow$ **GND** (Fancoil Modbus GND / Shield)

> [!WARNING]  
> **Reversed A/B Pins / Swapped Connections**: The RS-485 transmission lines must be crossed (`A` to `B` and `B` to `A`) for communication to function correctly, as pin labels on many transceivers/controllers are reversed relative to standard conventions.
> **Ground Shielding**: Connecting the common Ground (`GND`) terminal between the converter and the fancoil board is critical to prevent ground loops and communication noise.

---

## Modbus Protocol Specifications

* **Physical Layer**: RS-485
* **Baud Rate**: `9600`
* **Data Bits**: `8`
* **Parity**: `None`
* **Stop Bits**: `1`
* **Default Slave Address**: `1`
* **Crucial Timing Restriction**: The Innova board only supports a maximum of **3 registers** in a single Modbus read request. Reading 4 or more registers in a single request causes communication timeouts. This is prevented in the ESPHome configuration by using `force_new_range: true` to split register reads.

---

## Modbus Register Map (PU Board)

The following registers are mapped and queried in this configuration:

| Register Address (Dec) | Type | Acronym | Description | Unit / Scale | Access |
|:---:|:---:|:---:|:---|:---:|:---:|
| **0** | Holding | `T_AIR` | Current Room Air Temperature | $0.1\ ^\circ\text{C}$ | R |
| **1** | Holding | `T_WATER_2` | Water Temperature T2 (Inlet/Return Water) | $0.1\ ^\circ\text{C}$ | R |
| **2** | Holding | `T_WATER_4` | Water Temperature T3 (Coil/Supply Water) | $0.1\ ^\circ\text{C}$ | R |
| **20** | Holding | `RH` | Relative Humidity | $\%$ | R |
| **150** | Holding | `Status` | Unit Status Bitmask (Heating/Cooling active, standby, fan stops) | Bitmask | R |
| **151** | Holding | `Alarms` | Unit Alarms Bitmask (Sensor faults, motor failure, clean filter) | Bitmask | R |
| **198** | Holding | `Release` | Firmware Release Version | $0.1$ | R |
| **199** | Holding | `ID` | Firmware Identifier (PU Default is `1190`) | - | R |
| **302** | Holding | `SPL_W` | WEB Minimum Setpoint Limit | $1\ ^\circ\text{C}$ | R/W |
| **303** | Holding | `SPH_W` | WEB Maximum Setpoint Limit | $1\ ^\circ\text{C}$ | R/W |
| **305** | Holding | `SP` | Target Air Temperature Setpoint | $0.1\ ^\circ\text{C}$ | R/W |
| **457** | Holding | `FSW` | Flap Swing (Motorized Louvers) | - | R/W |
| **530** | Holding | `OS1` | Room Temperature Calibration Offset | $0.1\ ^\circ\text{C}$ | R/W |
| **553** | Holding | `PRG` | Program register: Fan Mode, Keypad Lock, Power Switch | Bitmask | R/W |
| **556** | Holding | `MAN` | Season Selection: Auto (0), Heating (1), Cooling (2) | - | R/W |
| **557** | Holding | `WEB` | Webserver Lockout Flags | Bitmask | R/W |

### Detailed Bitmasks in Register `553` (Program)
* **Bits [2-0] (Mode)**: `000` (0) = Auto, `001` (1) = Night/Silent, `010` (2) = Max/High
* **Bit 3 (Lock)**: Keypad lock (`1` = locked, `0` = unlocked)
* **Bit 4 (Stby)**: Standby state (`1` = standby/off, `0` = on)

---

## Installation and Setup

### Quick Start (ESPHome Web Dashboard)
If you are using the ESPHome Dashboard (via the Home Assistant add-on or standalone), you can deploy this integration instantly without downloading any local files:
1. Create a new device in your ESPHome Dashboard.
2. Open the device's configuration editor, delete all default code, and copy-paste the entire content of [esphome-innova.yaml](esphome-innova.yaml) directly into the editor.
3. Configure your secrets in your `secrets.yaml` file (see the configuration template below).
4. Click **Install**. ESPHome will automatically pull the custom `innova_climate` component from GitHub, compile the firmware, and flash it to your ESP32 device!

---

### Method A: Remote GitHub Import (Alternative)
If you are creating your own configuration from scratch, you can import this component by adding the following `external_components` block to your YAML:
```yaml
external_components:
  - source:
      type: git
      url: https://github.com/stenvanhouwelingen/innova-climate
      ref: 2026.6.25
```

---

### Method B: Local Installation (Manual Download)
If you prefer to host and edit the component files locally on your ESPHome machine:

1. Clone or download this repository, and copy the `components` folder into your ESPHome configuration directory:
   ```text
   your-esphome-folder/
   ├── esphome-innova.yaml
   ├── secrets.yaml
   └── components/
       └── innova_climate/
           ├── __init__.py
           ├── climate.py
           └── innova_climate.h
   ```

2. Open your `esphome-innova.yaml`, and change the `external_components` block to point to your local components directory instead of the GitHub repository:
   ```yaml
   external_components:
     - source:
         type: local
         path: components
   ```

---

### 2. Configure `secrets.yaml`
Create a `secrets.yaml` file containing your Wi-Fi credentials and security keys:
```yaml
wifi_ssid: "Your_WiFi_SSID"
wifi_password: "Your_WiFi_Password"

# Security keys for ESPHome best practices
api_key: "your_base64_api_key_here"
ota_password: "your_ota_password_here"
fallback_ap_password: "your_fallback_password_here"
```

### 3. Compile and Upload
Ensure the ESP32 is connected to your machine or is available on the network for OTA updates, and run:
```bash
esphome run esphome-innova.yaml
```

---

## Home Assistant Integration

Once the device is flashed and connected to Wi-Fi, it will be automatically discovered by Home Assistant's native **ESPHome integration**:

1. In Home Assistant, navigate to **Settings** $\rightarrow$ **Devices & Services**.
2. Under the discovered integrations, locate **Innova Bedroom** (or your designated room name) and click **Configure**.
3. Confirm the configuration. If prompted, input the API encryption key (configured as `api_key` in your `secrets.yaml`).
4. The following entities will become available:
   * **Climate Entity**: `climate.innova_bedroom_thermostat` (provides Mode, Setpoint, and Fan Speed controls).
   * **Sensors**: Water Temperatures ($T_2, T_3$), Relative Humidity, diagnostics (Uptime, Wi-Fi, Firmware).
   * **Diagnostic Text Sensors**: Fully decoded, human-readable status description and alarm code reporting.
   * **Configuration Numbers**: Temp Calibration Offset, Min Water Limit Heating, Max Water Limit Cooling.
   * **Configuration Switches**: Local Keypad Lock.

---

## Local Web Control Panel

The local ESP32 runs a web server. If Home Assistant is ever down, you can control the unit directly from any device on your Wi-Fi network:

1. Open your browser and navigate to `http://innova-<room_name>.local/` (or your device's IP address).
2. The page displays real-time readings, current setpoint, and allows adjusting the thermostat mode, setpoint, and fan speed.
3. You can also view logs and update firmware (OTA) directly through this local portal.

---

## Troubleshooting & Customization

* **Device Times Out / No Data**: Ensure you have physically crossed the RS-485 `A` and `B` wires.
* **Firmware Mismatch**: This configuration is verified on the **PU (on-board control)** boards with firmware ID `1190`. If your unit has a wall panel and registers different responses, check if it uses the **M7** register set.
* **Humidity Setpoint (Register 312)**: Some newer units do not support Register 312. If you see Modbus Exception code `2` (Illegal Data Address), this register has been omitted in this configuration to preserve loop speed.

---

## Liability Disclosure

**Disclaimer**: This integration is an independent open-source project and is not affiliated with, authorized, maintained, sponsored, or endorsed by Innova S.r.l. or any of its affiliates or partners.

Modbus communication involves reading and writing directly to the fancoil controller's registers. While this configuration is designed to be safe and complies with official documentation, writing invalid configurations or registers can potentially impact your fancoil's operation. Use this software entirely **at your own risk**. The authors and contributors assume no liability and are not responsible for any damage to your hardware, property, or heating/cooling systems caused by the use of this integration.
