# Chapter 7: Modbus Register Deep Dive & Bitmasks

This reference contains the complete holding register map and bitmask decodings for Innova PU / M7 series fancoil units (`n273025d`).

---

## 1. Core Holding Registers Map

| Reg. | Acronym | Description | Unit / Scale | R/W | Range / Values |
|:---:|:---|:---|:---:|:---:|:---|
| **`0`** | `T_AIR` | Ambient Room Air Temperature ($T_1$) | $0.1\ ^\circ\text{C}$ | R | $-300$ to $+800$ ($-30.0^\circ\text{C}$ to $+80.0^\circ\text{C}$) |
| **`1`** | `T_WATER_2` | Inlet Water Supply Temperature ($T_2$) | $0.1\ ^\circ\text{C}$ | R | $-300$ to $+800$ |
| **`2`** | `T_WATER_4` | Internal Coil Water Temperature ($T_3$) | $0.1\ ^\circ\text{C}$ | R | $-300$ to $+800$ |
| **`20`** | `RH` | Relative Humidity | $0.1\ \%$ | R | `0` to `1000` ($0\%$ to $100\%$) |
| **`150`** | `STATUS` | Operating Status Bitmask | - | R | See Status Bitmask below |
| **`151`** | `ALARMS` | Diagnostic Faults Bitmask | - | R | See Alarms Bitmask below |
| **`198`** | `RELEASE` | Firmware Version | $0.1$ | R | e.g., `10` = Release 1.0 |
| **`199`** | `ID` | Firmware Identifier | - | R | `1190` = PU series |
| **`305`** | `SP` | Target Air Temperature Setpoint | $0.1\ ^\circ\text{C}$ | R/W | `50` to `400` ($5.0^\circ\text{C}$ to $40.0^\circ\text{C}$, default `200`) |
| **`312`** | `SP_RH` | Relative Humidity Setpoint | $1\ \%$ | R/W | `20` to `90` (default `50`) |
| **`457`** | `FSW` | Motorized Flap Swing Control | - | R/W | `0` = Fixed / Off, `1` = Oscillating Swing |
| **`530`** | `OS1` | Ambient Sensor $T_1$ Calibration Offset | $0.1\ ^\circ\text{C}$ | R/W | `-12` to `+12` ($-1.2^\circ\text{C}$ to $+1.2^\circ\text{C}$) |
| **`550`** | `ADR` | Modbus Slave Address | - | R/W | `1` to `255` (default `1`) |
| **`553`** | `PRG` | Program, Fan Speed & Power Control | - | R/W | See Program Bitmask below |
| **`556`** | `MAN` | Season Mode Selection | - | R/W | `0` = Auto (Heat/Cool), `1` = Heating, `2` = Cooling |
| **`557`** | `WEB` | Webserver & Keypad Lock Flags | - | R/W | See Web Flags Bitmask below |

---

## 2. Status Register `150` Bitmask

| Bit | Name | Meaning When `1` |
|:---:|:---|:---|
| **`0`** | `Cooling active` | Water valve is open and unit is actively cooling. |
| **`1`** | `Heating active` | Water valve is open and unit is actively heating. |
| **`2`** | `Water fan stop in cooling` | Fan stopped: inlet water is too warm ($> 20^\circ\text{C}$) for cooling. |
| **`3`** | `Water fan stop in heating` | Fan stopped: inlet water is too cold ($< 30^\circ\text{C}$) for heating. |
| **`4`** | `Fan stop: Inadequate T2` | Safety lock due to out-of-range inlet water temperature. |
| **`5`** | `Fan stop: Inadequate T3` | Safety lock due to out-of-range coil temperature. |
| **`6`** | `Stop: Inadequate trend` | Water temperature trend unstable or moving wrong direction. |
| **`7`** | `Antifreeze active` | Frost protection routine active (forced valve opening). |
| **`8`** | `Alarm active` | At least one diagnostic alarm in Register 151 is active. |
| **`10`** | `Standby active` | Fancoil is in Standby (power logically OFF). |
| **`11`** | `Master timeout` | Remote Mode watchdog timer expired (> 300 s without command). |
| **`12`** | `Missing T2 probe` | Inlet probe $T_2$ absent at boot (30 °C heating gate bypassed). |
| **`13`** | `Missing T3 probe` | Coil probe $T_3$ absent at boot. |

---

## 3. Alarm Register `151` Bitmask

| Bit | Alarm Name | Description & Cause |
|:---:|:---|:---|
| **`0`** | `Modbus Comm Error` | Serial bus communication interrupted or watchdog timeout. |
| **`1`** | `T1 Air Temp Sensor Fault` | Ambient room probe open or shorted. (Wire 10k NTC to $T_1$). |
| **`2`** | `T3 Coil Sensor Fault` | Internal coil probe open or shorted. |
| **`3`** | `Inadequate Water Temp` | Water temperature outside operable thermal limits. |
| **`4`** | `T2 Inlet Sensor Fault` | Inlet water probe open or shorted. |
| **`5`** | `Inadequate T3 Temp` | Coil temperature dropped during heating or rose in cooling. |
| **`6`** | `Electric Heater Over-temp`| Electric heating element thermal fuse tripped (if equipped). |
| **`7`** | `Fan Motor Failure` | BLDC motor tachometer feedback missing or rotor blocked. |
| **`8`** | `Window Contact Open (IN1)`| External window sensor or presence contact open. |
| **`9`** | `Inadequate T2 Temp` | Supply water out of range for current command. |
| **`10`** | `Air Filter Needs Cleaning`| Fan motor operating hours exceeded maintenance interval. |
| **`11`** | `Lock: Inadequate T2 Temp` | Persistent low water temperature condition locked unit. |
| **`12`** | `Lock: Inadequate T3 Temp` | Persistent coil water temperature condition locked unit. |

---

## 4. Program Register `553` Bitmask

* **Bits [2-0] (Mode)**: `000` = Auto (PI modulated), `001` = Night / Silent, `010` = Max / Boost.
* **Bit 3 (Lock)**: `1` = Physical keypad locked, `0` = Keypad unlocked.
* **Bit 4 (Stby)**: `1` = Standby / Power OFF, `0` = Power ON / Active.

---

## 5. Web Control & Lock Register `557` Bitmask

| Bit | Hex Mask | Function When `1` |
|:---:|:---:|:---|
| **`0`** | `0x0001` | **LED Off**: Turns off front status LEDs / display lighting. |
| **`1`** | `0x0002` | **Force Off**: Forces fancoil off regardless of local controls. |
| **`2`** | `0x0004` | **Disable Mode Change**: Locks out local heating/cooling switching. |
| **`3`** | `0x0008` | **Disable Power Control**: Disables physical power on/off button. |
| **`4`** | `0x0010` | **Inhibit Extremes**: Prevents setting setpoints below 18°C or above 28°C. |
| **`5`** | `0x0020` | **Enable Setpoint Restriction**: Restricts setpoints to `[SPL_W, SPH_W]`. |
| **`6`** | `0x0040` | **Disable All Keys**: Complete physical keypad lockout. |
| **`7`** | `0x0080` | **Webserver Bypassed**: Read-only flag; indicates local manual override. |
| **`8`** | `0x0100` | **Disable Seasonal Key**: Disables season selection button only. |
