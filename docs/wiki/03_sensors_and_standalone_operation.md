# Chapter 3: Sensors & Standalone Operation

Innova fancoil controllers monitor up to three temperature sensors and an optional relative humidity probe to manage thermal regulation and safety interlocks.

---

## 1. Sensor Specifications & Electrical Characteristics

All temperature sensor inputs on Innova controller boards are designed for standard **$10\text{ k}\Omega\text{ NTC}$ thermistors**:

| Sensor Port | Modbus Register | Acronym | Typical Location | Function |
| :---: | :---: | :--- | :--- | :--- |
| **`T1` / `AIR`** | **`0`** | `T_AIR` | Air intake grille / wall panel | Measures ambient room air temperature for the PI control loop. |
| **`T2` / `H2`** | **`1`** | `T_WATER_2` | Supply / inlet copper pipe | Water safety interlock (anti-cold/warm draft) & season changeover. |
| **`T3` / `H4`** | **`2`** | `T_WATER_4` | Internal heat-exchanger coil | Internal coil temperature safety and frost protection. |
| **`RH`** | **`20`** | `RH` | Intake air path (optional) | Relative humidity measurement (scaled by $0.1\%$). |

* **Electrical Characteristics**: $10\text{ k}\Omega \pm 1\%$ at $25^\circ\text{C}$, standard Beta coefficient $B_{25/85} \approx 3950\text{ K}$.

---

## 2. $T_1$ Ambient Air Sensor & Standalone Wiring

### Where is the Sensor Physically Mounted?
* On standard exposed fancoils (such as the **AirLeaf SL**, **>OSMO<**, and **FÄRNA**), the physical $T_1$ probe is clipped directly into the **lower suction / air intake grille** (behind the air filter) and wired into the `AIR` / `T1` terminal block on the PCB.
* On bare in-wall / built-in fancoil units (e.g., **Filomuro SWI 400**, **AirLeaf SLI**), Innova ships the fancoil without a physical room temperature probe pre-attached.
* If an optional remote wall-mounted thermostat panel is installed on the room wall, the system can be configured to read temperature from the wall plate instead.

### What is "Standalone" Operation?
> **Definition**: **Standalone Operation** means running the fancoil directly from an ESP32 (ESPHome) via Modbus RTU **without purchasing or mounting any Innova touch control panel** (such as the on-board display or the Smart Touch wall panel).

### Wiring $T_1$ in a Standalone Setup
If your unit did not come with a probe or was previously driven by a wall screen:
1. Connect any standard **$10\text{ k}\Omega\text{ NTC}$ temperature probe** (two wires) into the screw terminals marked **`T1`** (or **`AIR`**) on the main PCB.
2. Clip the sensor bead in the air intake path beneath the air filter.

> [!WARNING]
> If nothing is connected to the $T_1$ terminals, the PCB detects an open circuit ($-30^\circ\text{C}$), sets **Alarm Register 151 Bit 1 (`T1 Air Temp Sensor Fault`)**, and immediately halts all fan and valve operations.

---

## 3. $T_2$ Inlet Water Sensor Mechanics

The inlet water sensor ($T_2$ / $H_2$) measures the incoming supply water from the heat pump and acts as an automatic safety gatekeeper:

```
                           [ INLET WATER SENSOR (T2) ]
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
     [ HEATING MODE ]                                          [ COOLING MODE ]
    T2 ≥ 30°C  ──► FAN UNLOCKED                                T2 ≤ 20°C  ──► FAN UNLOCKED
    T2 < 30°C  ──► FAN BLOCKED (Cold Draft Safety)             T2 > 20°C  ──► FAN BLOCKED (Warm Draft Safety)
```

* **Cold-Draft Prevention (Heating)**: Prevents the fan from blowing unheated air into the room before the hot water loop has reached temperature.
* **Warm-Draft Prevention (Cooling)**: In cooling mode, delays fan start until chilled water has chilled the coil to prevent blowing warm, humid room air.

---

## 4. $T_3$ Internal Coil Water Sensor

The $T_3$ ($H_4$) sensor is embedded in direct physical contact with the copper U-bends of the internal heat exchanger coil:
* **Coil Water Adequacy**: Verifies that the internal coil is actively heating ($> 30^\circ\text{C}$) or cooling ($< 20^\circ\text{C}$). If temperature is inadequate, the controller pauses the fan (Status Register 150, Bit 5).
* **Trend Monitoring**: Checks if the temperature trend is stable (Status Register 150, Bit 6). If water flow stops (e.g. pump failure), the coil rapidly normalizes to room temperature and the fancoil pauses.
* **Antifreeze / Frost Protection**: If air or coil temperature drops below **$5.0^\circ\text{C}$**, the controller forces the water valve open and sets Status Register 150 Bit 7 (`Antifreeze active`) to circulate water and prevent frozen/burst copper pipes.

---

## 5. Relative Humidity Sensor (Register 20)

* Available on select fancoil models with factory-installed hygrometric sensors.
* Read as an unsigned word where the raw value represents tenths of a percent ($550 = 55.0\%$).
* Used in high-end installations for dew point calculation to prevent pipe sweat during active cooling.
