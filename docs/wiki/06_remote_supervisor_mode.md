# Chapter 6: Remote Supervisor Mode (Injecting External Temperatures)

Innova PU series controllers support an official **Remote Supervisor Mode**. In this mode, the fancoil bypasses its local thermostat logic and acts as a pure actuator governed by an external master (such as ESPHome, Home Assistant, or a KNX gateway).

---

## 1. Why Use Remote Mode?

* **No Physical $T_1$ Sensor Required**: If the fancoil is installed without a wall panel and without an onboard NTC probe, ambient temperature can be streamed digitally over Modbus.
* **External Thermostats**: Allows using high-precision wall sensors (e.g. KNX, Zigbee, BLE thermometers, or Home Assistant averaged temperature sensors) placed away from the fancoil.

---

## 2. Remote Mode Modbus Registers

To activate and control the unit in Remote Mode, use the following registers:

| Register | Acronym | Description | Unit / Scale | R/W | Values / Bitmask |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **`100`** | `REM_MODE` | Remote work mode & control flags | - | R/W | See Bitmask Table below |
| **`101`** | `REM_SET` | Remote air temperature setpoint | $0.1\ ^\circ\text{C}$ | R/W | `50` to `400` ($5.0^\circ\text{C}$ to $40.0^\circ\text{C}$) |
| **`102`** | `REM_TA` | **Remote ambient air temperature** | $0.1\ ^\circ\text{C}$ | R/W | Target ambient temp (e.g. `215` for $21.5^\circ\text{C}$) |
| **`552`** | `CFG` | Configuration register | - | R/W | `Bit 1 (REM)` = 1 enables remote mode |

---

## 3. Register `100` Bitmask Breakdown

```
 Bit 15: TMP (0=Remote probe, 1=On-board probe)
 │
 │  Bits 14-13: Season (00=Auto, 01=Heat, 10=Cool)
 │  │
 │  │   Bit 12: CP (Contact switch)
 │  │   │
 │  │   │        Bit 7: Stby (0=On, 1=Standby)
 │  │   │        │
 │  │   │        │     Bit 4: REM (1=Remote mode enabled)
 │  │   │        │     │
 │  │   │        │     │  Bits 2-0: PRG (000=Auto, 001=Night, 010=Max)
 │  │   │        │     │  │
┌▼──▼───▼────────▼─────▼──▼──┐
│15│14 13│12│11 8│7│6 5│4│3│2 1 0│
└────────────────────────────┘
```

* **Bit 4 (`REM`)**: Set to `1` to activate Remote Mode operation.
* **Bit 7 (`Stby`)**: Set to `0` to turn the fancoil ON; set to `1` for Standby/Power OFF.
* **Bits [2-0] (`PRG`)**: Fan speed mode (`000` = Auto, `001` = Night/Silent, `010` = Max).
* **Bits [14-13] (`Season`)**: Mode selection (`00` = Auto changeover, `01` = Heating, `10` = Cooling).
* **Bit 15 (`TMP`)**: **Sensor source selection** (`0` = Use remote `REM_TA` register 102, `1` = Use physical on-board $T_1$ probe).

---

## 4. Safety Watchdog Protocol

To prevent runaway heating or cooling if the external automation server crashes:

1. Enabling Remote Mode activates a **300-second (5-minute) safety watchdog timer** inside the PU microcontroller.
2. The master controller (ESPHome) must periodically write to Registers `100`, `101`, or `102` at least once every 5 minutes.
3. **If the Watchdog Expires**:
   * The fancoil automatically initiates a safe shutdown (closes water valves, turns off fan motor).
   * Sets **Status Register 150 Bit 11 (`Master comm timeout`)** and **Alarm Register 151 Bit 0 (`Communication error`)**.
4. **Recommended Broadcast Frequency**: Transmit updates every **30 to 120 seconds**.
