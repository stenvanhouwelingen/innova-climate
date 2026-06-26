# Innova Fancoil Modbus Register Map Reference

This document provides a comprehensive overview of the Modbus registers, bitmasks, and connection guidelines for both Innova control board families: **`n273025d`** (modern on-board/wall controllers) and **`n273025c`** (older control touchscreens and bridge retrofits).

---

## Modbus Register Families & Board Directory

Innova fancoil systems belong to one of two firmware/register families. The physical board model determines which register mapping is active:

### 1. Modern Board Family (`n273025d` / `n421259a`)
* **Typical Fancoils**: OSMO Series, FÄRNA Series, newer AirLeaf SL/SLI/RSI/SLSI, newer Filomuro Slim Fit & SWI recessed.
* **Compatible Control PCBs**:
  * `ECA789` (On-board main PCB on newer Filomuro units)
  * `PUB-30` (On-board main PCB on newer AirLeaf, OSMO, FÄRNA units)
  * `ESE845`, `ESE845II`, `ESE846II` (Modulating receivers)
  * `ESE745II`, `ESE746II` (M7 modulating receivers)
  * `ESE645II` (Legacy modulating receivers)
  * `ESE790` (Slim Fit specialized modulating board)
* **Compatible User Interfaces**:
  * On-board Touchscreens: `ECA844II`, `EWA844II`, `ECA044II`, `EWA044II`
  * Remote Wall Panels: `EEB749II` (Standard), `EFB749II` (Wi-Fi), `EGB749II` (Bluetooth)
* **ESPHome Package**: [packages/innova_n273025d.yaml](packages/innova_n273025d.yaml)

### 2. Legacy / Retrofit Bridge Family (`n273025c`)
* **Typical Fancoils**: Filoterra trench floor terminals, older AirLeaf, older Filomuro Slim Fit / built-in.
* **Compatible Control PCBs / Accessories**:
  * `INN-FR-B32` (Modbus RTU retrofit bridge accessory card)
  * `eESE645` / `ESE648` (Modulating receivers used in combination with bridge)
* **Compatible User Interfaces**:
  * On-board Touchscreens: `ECA644`, `ECA647`
  * Remote Wall Panels: `EDA649`, `EDB649`, `EEA649II` / `EEB649II` / `EFA649II` / `EFB649II`
* **ESPHome Package**: [packages/innova_n273025c.yaml](packages/innova_n273025c.yaml)

---

## Connection Parameters

These parameters apply to both families when establishing communication:

* **Serial Protocol**: Modbus RTU
* **Baud Rate**: 9600
* **Data Bits**: 8
* **Parity**: None
* **Stop Bits**: 1
* **Default Slave Address**: `1`
* **Timing Restriction**: Minimum silent interval between Modbus commands must be at least **150ms** (recommend polling interval of `10s` and write command throttle of `200ms`).
* **Length Restriction**: The fancoil controller only supports reading a maximum of **3 registers** per single request. Reading 4 or more registers in a single request will result in timeout errors. (Avoided in ESPHome by using `force_new_range: true` to segment queries).

---

## PART 1: Modern `n273025d` / `n421259a` Register Map

### Standard Registers

| Reg. | Acronym | Description | Unit / Scale | R/W | Default | Range / Values |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **0** | `T_AIR` | T1 Room Air Temperature | $0.1\ ^\circ\text{C}$ | R | - | - |
| **1** | `T_WATER_2` | T2 Water Inlet (Return) Temperature | $0.1\ ^\circ\text{C}$ | R | - | - |
| **2** | `T_WATER_4` | T3 Water Coil (Supply) Temperature | $0.1\ ^\circ\text{C}$ | R | - | - |
| **20** | `RH` | Relative Humidity | $\%$ | R | - | 0 to 100 (if sensor present) |
| **150** | `Status` | Operating status bitmask | - | R | - | See status table below |
| **151** | `Alarms` | System alarm code bitmask | - | R | - | See alarms table below |
| **198** | `Release` | Firmware release version | $0.1$ | R | - | e.g. `15` = v1.5 |
| **199** | `ID` | Firmware identifier | - | R | `1190` | `1190` = PU on-board control |
| **302** | `SPL_W` | WEB Minimum setpoint limit | $1\ ^\circ\text{C}$ | R/W | 20 | 5 to SPH_W |
| **303** | `SPH_W` | WEB Maximum setpoint limit | $1\ ^\circ\text{C}$ | R/W | 24 | SPL_W to 40 |
| **305** | `SP` | Target Air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | 200 | 50 ($5.0\ ^\circ\text{C}$) to 400 ($40.0\ ^\circ\text{C}$) |
| **457** | `FSW` | Flap swing (motorized louvers) | - | R/W | 1 | `0` = Swing OFF, `1` = Swing ON |
| **530** | `OS1` | Ambient sensor T1 calibration offset | $0.1\ ^\circ\text{C}$ | R/W | 0 | -12 to 12 ($-1.2\ ^\circ\text{C}$ to $+1.2\ ^\circ\text{C}$) |
| **550** | `ADR` | Modbus slave address | - | R/W | 1 | 1 to 255 |
| **553** | `PRG` | Program register (fan mode, power) | - | R/W | - | See program table below |
| **556** | `MAN` | Season selection (Auto/Heat/Cool) | - | R/W | 0 | `0` = Auto, `1` = Heating, `2` = Cooling |
| **557** | `WEB` | Flag for webserver lockouts | - | R/W | 0 | See webserver table below |
| **574** | `TY` | Unit Type configuration | - | R/W | 0 | `0` = RP, `1` = PE, `2` = PN, `3` = PS, `4` = R1 |

### Register Bitmasks (`n273025d`)

#### Register `553` (Program Control)
* **Bits [2-0] (Ventilation Mode)**:
  * `000` (0) = Auto
  * `001` (1) = Night / Silent
  * `010` (2) = Maximum Speed
* **Bit 3 (Lock)**: Keypad lock (`1` = locked, `0` = unlocked)
* **Bit 4 (Stby)**: Standby state (`1` = standby/OFF, `0` = active/ON)

#### Register `150` (Operating Status)
* **Bit 0**: Cooling loop active
* **Bit 1**: Heating loop active
* **Bit 2**: Stopped: coil water temperature too high for cooling
* **Bit 3**: Stopped: coil water temperature too low for heating
* **Bit 4**: Stopped: inadequate main water T2 temperature
* **Bit 5**: Stopped: inadequate coil water T3 temperature
* **Bit 6**: Stopped: inadequate water temperature trend
* **Bit 7**: Antifreeze protection active
* **Bit 8**: At least one alarm active (corresponds to Register 151)
* **Bit 10**: Standby active (unit is OFF)
* **Bit 11**: Master communication timeout (Remote Mode safety watchdog)
* **Bit 12**: Missing T2 (H2) main water temperature probe
* **Bit 13**: Missing T3 (H4) coil water temperature probe

#### Register `151` (Alarms)
* **Bit 0**: Serial Modbus timeout error
* **Bit 1**: T1 Room Air Probe fault
* **Bit 2**: T3 Water Coil Probe fault
* **Bit 3**: Stop for inadequate water temperature
* **Bit 4**: T2 Main Water Probe fault
* **Bit 5**: Secondary temperature loop out of range
* **Bit 6**: Electric auxiliary heater over-temperature trip
* **Bit 7**: Fan motor feedback signal failure
* **Bit 8**: Dry Contact IN1 open (window contact / condensate overflow)
* **Bit 9**: Primary water loop temperature out of range
* **Bit 10**: Filter cleaning maintenance timer expired
* **Bit 11**: Hard T2 thermal lockout
* **Bit 12**: Hard T3 thermal lockout

#### Register `557` (Webserver Lockout Flags)
* **Bit 0**: Led WEB OFF (Force panel network status indicator off)
* **Bit 1**: Forced OFF (Lock fancoil in standby; local power toggles disabled)
* **Bit 2**: Disables mode change (Lock seasonal select button)
* **Bit 3**: Disables standby toggle (Prevent power toggles from panel)
* **Bit 4**: Inhibits extremes (Prevent selecting 5°C and 40°C setpoint limits)
* **Bit 5**: Enables setpoint restriction (Restricts range to [SPL_W, SPH_W])
* **Bit 6**: Disables all keys (Keypad completely locked)
* **Bit 7**: Webserver bypassed for 1 hour (Read-only; indicates manual bypass)
* **Bit 8**: Seasonal key disabled (Disable seasonal select button only)

---

## PART 2: Legacy / Retrofit `n273025c` Register Map

### Standard Registers

| Reg. | Acronym | Description | Unit / Scale | R/W | Default | Range / Values |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **0** | `T_AIR` | T1 Room Air Temperature | $0.1\ ^\circ\text{C}$ | R | - | - |
| **1** | `T_WATER_2` | T2 Water Inlet (Return) Temperature | $0.1\ ^\circ\text{C}$ | R | - | - |
| **2** | `T_WATER_4` | T3 Water Coil (Supply) Temperature | $0.1\ ^\circ\text{C}$ | R | - | - |
| **20** | `RH` | Relative Humidity | $\%$ | R | - | 0 to 100 (if sensor present) |
| **104** | `Status` | Operating status bitmask | - | R | - | See status table below |
| **105** | `Alarms` | System alarm code bitmask | - | R | - | See alarms table below |
| **200** | `ADR` | Modbus slave address | - | R/W | 1 | 1 to 255 |
| **201** | `PRG` | Program register (fan mode, power) | - | R/W | - | See program table below |
| **231** | `SP` | Target Air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | 200 | 160 ($16.0\ ^\circ\text{C}$) to 300 ($30.0\ ^\circ\text{C}$) |
| **233** | `MAN` | Season selection (Auto/Heat/Cool) | - | R/W | 0 | `0` = Auto, `3` = Heating, `5` = Cooling |
| **242** | `OS1` | Ambient sensor T1 calibration offset | $0.1\ ^\circ\text{C}$ | R/W | 0 | -12 to 12 ($-1.2\ ^\circ\text{C}$ to $+1.2\ ^\circ\text{C}$) |
| **245** | `SPL_W` | WEB Minimum setpoint limit | $0.1\ ^\circ\text{C}$ | R/W | 200 | 50 to SPH_W |
| **246** | `SPH_W` | WEB Maximum setpoint limit | $0.1\ ^\circ\text{C}$ | R/W | 240 | SPL_W to 400 |
| **247** | `WEB` | Flag for webserver lockouts | - | R/W | 0 | See webserver table below |

### Register Bitmasks (`n273025c`)

#### Register `201` (Program Control)
* **Bits [2-0] (Ventilation Mode)**:
  * `000` (0) = Auto
  * `001` (1) = Silent Speed
  * `010` (2) = Night Speed
  * `011` (3) = Maximum Speed
* **Bit 4 (Lock)**: Keypad lock (`1` = locked, `0` = unlocked)
* **Bit 7 (Stby)**: Standby state (`1` = standby/OFF, `0` = active/ON)

#### Register `104` (Operating Status)
* **Bit 0**: Cooling loop active
* **Bit 1**: Heating loop active
* **Bit 2**: Stopped: inadequate main water T2 temperature
* **Bit 3**: Stopped: coil water temperature too low for heating
* **Bit 4**: Stopped: coil water temperature too high for cooling (or safety delay)
* **Bit 5**: Antifreeze protection active
* **Bit 6**: At least one alarm active (corresponds to Register 105)
* **Bit 8**: Standby active (unit is OFF)
* **Bit 10**: Master communication timeout (Remote Mode safety watchdog)
* **Bit 11**: Missing T2 (H2) main water temperature probe
* **Bit 12**: Missing T3 (H4) coil water temperature probe

#### Register `105` (Alarms)
* **Bit 0**: Modbus / bridge board communication timeout error
* **Bit 1**: T1 Room Air Probe fault
* **Bit 2**: H4 Water Sensor Fault (T3 Water Probe)
* **Bit 3**: Block for harmful water temperature
* **Bit 4**: H2 Water Sensor Fault (T2 Water Probe)
* **Bit 5**: Inadequate H4 coil temperature
* **Bit 6**: Electric auxiliary heater over-temperature trip
* **Bit 7**: Fan motor feedback signal failure
* **Bit 8**: Grid Contact Open (IN1 Switch)
* **Bit 9**: Inadequate H2 main loop temperature
* **Bit 10**: Filter cleaning maintenance timer expired
* **Bit 11**: Remote Probe communication error

#### Register `247` (Webserver Lockout Flags)
* **Bit 0**: Led WEB OFF (Force panel network status indicator off)
* **Bit 1**: Forced OFF (Lock fancoil in standby; local power toggles disabled)
* **Bit 2**: Disables mode change (Lock seasonal select button)
* **Bit 3**: Disables standby toggle (Prevent power toggles from panel)
* **Bit 4**: Inhibits extremes (Prevent selecting 5°C and 40°C setpoint limits)
* **Bit 5**: Enables setpoint restriction (Restricts range to [SPL_W, SPH_W])
* **Bit 6**: Disables all keys (Keypad completely locked)
* **Bit 7**: Webserver bypassed for 1 hour (Read-only; indicates manual bypass)
* **Bit 8**: Seasonal key disabled (Disable seasonal select button only)

---

## PART 3: Remote Mode & Safety Watchdog Protocols (PU Board Only, n273025d)

In Remote Mode, the fancoil ignores its local thermostat algorithms and is driven entirely by a supervisor or smart home master (such as ESPHome). This allows sending external room temperatures and setting remote targets.

### Remote Mode Registers

| Reg. | Acronym | Description | Unit / Scale | R/W | Default | Range / Values |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **100** | `REM_MODE` | Remote work mode register | - | R/W | - | See remote mode bitmask below |
| **101** | `REM_SET` | Remote air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | - | 50 to 400 |
| **102** | `REM_TA` | Remote air temperature value | $0.1\ ^\circ\text{C}$ | R/W | - | Transmitted ambient temperature |
| **552** | `CFG` | Configuration register | - | R/W | - | Bit 1 enables remote mode |

### Remote Mode Bitmasks

#### Register `100` (Remote Mode Control)
* **Bits [2-0] (PRG)**: `000` = Auto, `001` = Night/Silent, `010` = Max, `011` = Min
* **Bit 4 (REM)**: Remote mode toggle (`1` = Remote mode enabled, `0` = Disabled)
* **Bit 7 (Stby)**: Standby state (`1` = Standby/Off, `0` = On)
* **Bit 12 (CP)**: Contact switch status (`0` = Closed, `1` = Open)
* **Bits [14-13] (Season)**: `00` = Auto changeover, `01` = Heating, `10` = Cooling
* **Bit 15 (TMP)**: Temperature probe selection (`1` = Use on-board T1 sensor, `0` = Use remote `REM_TA` register)

#### Register `552` (CFG)
* **Bit 1 (REM)**: Remote mode configuration toggle (`1` = Enable remote mode operation, `0` = Use local thermostat logic)

### Safety Watchdog Protocol
To enable Remote Mode, the central controller must write a value of `1` to Bit 4 of Register 100 or Bit 1 of Register 552. Doing so activates a **300-second (5-minute) safety watchdog timer** on the PU board.

* While in Remote Mode, the supervisor must regularly transmit Modbus write commands to at least one of its remote-control registers (Registers 100, 101, or 102).
* **If the watchdog timer expires** (no updates received for > 300 seconds), the PU board initiates a safety shutdown: it closes all hydronic valves, turns off the fan motor, and sets the watchdog timeout flag (Register 150, Bit 11) and communication error flag (Register 151, Bit 0).
* **Recommended Update Interval**: The central controller should transmit periodic updates to the fancoil every **30 to 120 seconds** to ensure stable remote operations and prevent watchdog timeouts.
