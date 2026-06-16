# Innova Fancoil Modbus Register Map Reference

This document provides a comprehensive overview of the Modbus registers and bitmasks for the **Innova M7** (Wall Control) and **PU** (On-board Power Unit) fancoil controllers, transcribed directly from the manufacturer's Modbus Quick Reference and system architecture documentation.

---

## Connection Parameters

* **Serial protocol**: Modbus RTU (Default) or Modbus ASCII (Configured via dip-switch option B)
* **Baud rate**: 9600
* **Data bits**: 8 (RTU) or 7 (ASCII)
* **Parity**: None (RTU) or Even (ASCII)
* **Stop bits**: 1
* **Default Slave Address**: `1`
* **Timing restriction**: Minimum silent interval between Modbus commands is **150ms**. Polling faster than this can saturate the serial buffer, leading to missed frames.
* **Length restriction**: The fancoil controller only supports reading a maximum of **3 registers** per single request. Asking for 4 or more registers in a single request will result in timeout errors.

---

## 1. M7 (Wall Control) Register Map

This register map applies to fancoil models configured with the **M7** wall controller (Firmware Release 1.5 and up).

### Registers

| Reg. | Acronym | Description | Unit | R/W | Default | Min | Max |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **0** | `T_AIR` | T1 Room Air Temperature | $0.1\ ^\circ\text{C}$ | R | - | - | - |
| **20** | `RH` | Relative Humidity | $\%$ | R | - | - | - |
| **150** | `Status` | Unit status (see below) | - | R | - | - | - |
| **151** | `Alarms` | Unit alarms (see below) | - | R | - | - | - |
| **198** | `Release` | Firmware release | $0.1$ | R | - | - | - |
| **199** | `ID` | Firmware identifier (`1190` = PU) | - | R | 1190 | - | - |
| **305** | `SP` | Air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | 200 ($20\ ^\circ\text{C}$) | 50 | 400 |
| **312** | `SP_RH` | Relative humidity setpoint | $\%$ | R/W | 50 | 20 | 90 |
| **550** | `ADR` | Modbus slave address | - | R/W | 1 | 1 | 255 |
| **553** | `PRG` | Program register (see below) | - | R/W | - | - | - |
| **556** | `MAN` | Season selection: Auto (0), Heat (1), Cool (2) | - | R/W | Auto | - | - |
| **574** | `TY` | Unit type: RP=0, PE=1, PN=2, PS=3, R1=4 | - | R/W | RP | - | - |

### Register Bitmasks (M7)

#### Register `553` (Program)
* **Bits [2-0] (Mode)**: `000` (0) = Auto, `001` (1) = Night/Silent, `010` (2) = Max
* **Bit 3 (Lock)**: Keypad lock (`1` = locked, `0` = unlocked)
* **Bit 4 (Stby)**: Standby state (`1` = standby/off, `0` = on)

#### Register `150` (Status)
* **Bit 0**: At least one alarm present
* **Bit 2**: Control in standby
* **Bit 3**: Communication error

#### Register `151` (Alarms)
* **Bit 0**: Communication error

---

## 2. PU (On-Board Control) Register Map

This register map applies to fancoil models configured with the **PU** on-board controller (Firmware Release 1.5 and up). This requires the on-board dip-switch **F** to be set to **ON** at power-on.

### Registers

| Reg. | Acronym | Description | Unit | R/W | Default | Min | Max |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **0** | `T_AIR` | T1 Room Air Temperature | $0.1\ ^\circ\text{C}$ | R | - | - | - |
| **1** | `T_WATER_2` | T2 Water Inlet (Return) Temperature | $0.1\ ^\circ\text{C}$ | R | - | - | - |
| **2** | `T_WATER_4` | T3 Water Coil (Supply) Temperature | $0.1\ ^\circ\text{C}$ | R | - | - | - |
| **150** | `Status` | Unit status (see below) | - | R | - | - | - |
| **151** | `Alarms` | Unit alarms (see below) | - | R | - | - | - |
| **198** | `Release` | Firmware release | $0.1$ | R | - | - | - |
| **199** | `ID` | Firmware identifier (`1190` = PU) | - | R | 1190 | - | - |
| **305** | `SP` | Air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | 200 ($20\ ^\circ\text{C}$) | 50 | 400 |
| **550** | `ADR` | Modbus slave address | - | R/W | 1 | 1 | 255 |
| **553** | `PRG` | Program register (see below) | - | R/W | - | - | - |
| **556** | `MAN` | Season selection: Auto (0), Heat (1), Cool (2) | - | R/W | Auto | - | - |

### Register Bitmasks (PU)

#### Register `553` (Program)
* **Bits [2-0] (Mode)**: `000` (0) = Auto, `001` (1) = Night/Silent, `010` (2) = Max
* **Bit 3 (Lock)**: Keypad lock (`1` = locked, `0` = unlocked)
* **Bit 4 (Stby)**: Standby state (`1` = standby/off, `0` = on)

#### Register `150` (Status)
* **Bit 0**: Cooling active
* **Bit 1**: Heating active
* **Bit 2**: Water fan stop in cooling (setpoint met)
* **Bit 3**: Water fan stop in heating (setpoint met)
* **Bit 4**: Fan stopped due to inadequate Inlet (T2) water temperature
* **Bit 5**: Fan stopped due to inadequate Coil (T3) water temperature
* **Bit 6**: Stopped due to inadequate water temperature trend
* **Bit 7**: Antifreeze active
* **Bit 8**: At least one alarm active
* **Bit 10**: Standby active
* **Bit 11**: Master communication timeout (only when in remote mode)
* **Bit 12**: Missing H2 (T2) probe (only on selected units)
* **Bit 13**: Missing H4 (T3) probe (only on selected units)

#### Register `151` (Alarms & System Interlocks)
When a fault is detected in this register, the PU board sets the corresponding error bit and activates physical safety interlock actions to protect the unit:

| Bit Index | Modbus Fault Flag | Associated Node | System Interlock & Safety Actions |
|:---:|:---|:---|:---|
| **0** | Serial Timeout Error | RS-485 Modbus Bus | Sets Register 150 Bit 11. If the timeout exceeds 300 seconds in Remote Mode, the fan is stopped and hydronic valves are closed. |
| **1** | T1 Sensor Fault | Ambient Air Probe | Disables local temperature-based operations; the fan is locked off unless running in fan-only mode. |
| **2** | T3 Sensor Fault | Secondary Water Coil | Disables 4-pipe automatic seasonal changeover and auxiliary heating controls. |
| **3** | Inadequate Water Temp | Primary Hydraulic Flow | Triggers thermal fan lock (Reg 150 Bit 2/3). Stops fan to prevent cold draft (heating) or warm draft (cooling). |
| **4** | T2 Sensor Fault | Main Water Coil Probe | Disables standard 2-pipe temperature checks. The system relies on manual override selections to run. |
| **5** | Secondary Temp Out of Range | Secondary Water Loop | Disables the secondary control valve, isolating the secondary coil from water flow. |
| **6** | High Temp Limit | Auxiliary Electric Heater | Disconnects the power relay to the electric heating element to prevent thermal damage. |
| **7** | Motor Drive Failure | EC Centrifugal Fan | Shuts down the valve actuators and sets a global diagnostic alarm to prevent internal heat build-up. |
| **8** | Safety Input Open | Dry Contact Input IN1 | Immediately disables the fan and closes all valves. Typically used for window contacts or condensate overflow sensors. |
| **9** | Main Coil Temp Out of Range | Primary Water Loop | Closes the main valve and stops the fan until the water temperature returns to the proper range. |
| **10** | Filter Maintenance Warning | Return Air Grille | Triggers a visual warning on local panels. Operation continues normally while the timer awaits a manual reset. |
| **11** | Hard T2 Thermal Lockout | Primary Hydronic Loop | Disables all heating/cooling functions. Requires manual intervention or a reset command to restore operation. |
| **12** | Hard T3 Thermal Lockout | Secondary Hydronic Loop | Locks out secondary coil operations until the diagnostic state is cleared. |

---

## 3. Remote Mode & Safety Watchdog Protocols (PU Board Only)

In Remote Mode, the fancoil ignores its local thermostat algorithms and is instead driven entirely by a supervisor or smart home master (such as ESPHome). This allows sending external room temperatures and setting remote targets.

### Remote Mode Registers

| Reg. | Acronym | Description | Unit | R/W | Default | Min | Max |
|:---:|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **100** | `REM_MODE` | Remote work mode register (see below) | - | R/W | - | - | - |
| **101** | `REM_SET` | Remote air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | - | 50 | 400 |
| **102** | `REM_TA` | Remote air temperature value | $0.1\ ^\circ\text{C}$ | R/W | - | - | - |
| **552** | `CFG` | Configuration register (see below) | - | R/W | - | - | - |

### Bitmasks

#### Register `100` (Remote Mode)
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
