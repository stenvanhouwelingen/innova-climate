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

### Where is the Sensor Normally Located?
* On units equipped with an official Innova wall thermostat panel (e.g. Smart Touch), the ambient temperature sensor is integrated inside the wall panel.
* On bare in-wall / built-in fancoil units (e.g., **Filomuro SWI 400**, **Airleaf SLI**), Innova ships the fancoil without a physical room temperature sensor attached.

### The Standalone Setup (Without Wall Panel)
If you operate the fancoil standalone using ESPHome without an official Innova wall thermostat:
1. Obtain any standard **$10\text{ k}\Omega\text{ NTC}$ temperature probe** (two wires).
2. Connect the two probe wires into the screw terminals marked **`T1`** (or **`AIR`**) on the main PCB.
3. Position the sensor tip in the return air path beneath the air filter.

> [!WARNING]
> If nothing is connected to the $T_1$ terminals, the PCB detects an open circuit ($-30^\circ\text{C}$), sets **Alarm Register 151 Bit 1 (`T1 Air Temp Sensor Fault`)**, and immediately shuts down the fancoil.

---

## 3. $T_2$ Inlet Water Sensor Mechanics

The inlet water sensor acts as a thermal gatekeeper:

```
                           [ INLET WATER SENSOR (T2) ]
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
     [ HEATING MODE ]                                          [ COOLING MODE ]
    T2 ≥ 30°C  ──► FAN UNLOCKED                                T2 ≤ 20°C  ──► FAN UNLOCKED
    T2 < 30°C  ──► FAN BLOCKED (Cold Draft Safety)             T2 > 20°C  ──► FAN BLOCKED (Warm Draft Safety)
```

* **Cold-Draft Prevention**: Prevents the fan from blowing unheated air into the room before the hot water loop has reached temperature.
* **Warm-Draft Prevention**: In cooling mode, delays fan start until chilled water has chilled the coil to prevent blowing warm, humid room air.

---

## 4. $T_3$ Internal Coil Sensor

* Placed in direct contact with the internal copper coil fins.
* Triggers **Alarm Register 151 Bit 5** if the internal coil temperature deviates significantly from expected thresholds during operation.
* Provides rapid frost protection in the event that water flow drops while cooling below freezing.

---

## 5. Relative Humidity Sensor (Register 20)

* Available on select fancoil models with factory-installed hygrometric sensors.
* Read as an unsigned word where the raw value represents tenths of a percent ($550 = 55.0\%$).
* Used in high-end installations for dew point calculation to prevent pipe sweat during active cooling.
