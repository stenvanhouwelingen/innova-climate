# Chapter 4: Heat Pumps & Low-Temperature Heating ($< 30^\circ\text{C}$ Water)

Modern residential heat pumps frequently operate on weather-dependent heating curves (low-temperature radiant / underfloor water loops), supplying water between **$25^\circ\text{C}$ and $29^\circ\text{C}$** during mild winter days.

---

## 1. The 30 °C Interlock Conflict

By factory default, the Innova controller firmware enforces a hard safety gate:

| Water Temperature ($T_2$) | Controller Action | Status Code |
| :--- | :--- | :--- |
| **$T_2 \ge 30.0^\circ\text{C}$** | Fan runs normally based on room temperature error ($\Delta T$). | Status `Normal` |
| **$T_2 < 30.0^\circ\text{C}$** | Fan motor is completely locked at **`0 RPM`** (even if room is cold). | Status Register 150 Bit 4: *"Fan stop for inadequate T2 temp"* |

In high-efficiency heat pump systems, supply water may intentionally stay at $26^\circ\text{C} - 28^\circ\text{C}$ for days, causing the fancoil to refuse to heat.

---

## 2. Solutions for Low-Temperature Operation

There are two verified ways to enable low-temperature heating on Innova fancoils:

```
                            [ LOW-TEMP WATER SOLUTIONS ]
                                         │
            ┌────────────────────────────┴────────────────────────────┐
            ▼                                                         ▼
  [ METHOD 1: PROBE DISCONNECT ]                             [ METHOD 2: 47kΩ RESISTOR MOD ]
  • Official Innova hardware bypass                          • Community hardware mod
  • Completely removes 30°C check                            • Preserves sensor reading with +4°C shift
  • Disconnect T2 sensor before boot                         • Solder 47kΩ in parallel with T2 NTC
```

---

### Method 1: Disconnecting the $T_2$ Water Sensor (Official Innova Bypass)

Innova designed the controller firmware to recognize when a unit is installed without water probes:

1. Power off the fancoil completely.
2. Unplug the **$T_2$ (Inlet Water)** temperature probe from the PCB.
3. Wait at least **1 minute**, then power on the fancoil.
4. **Result**:
   * The controller detects that the probe was absent at startup and sets **Status Register 150 Bit 12 (`Missing T2 probe`)**.
   * The firmware **permanently disables the 30 °C heating interlock**.
   * The fan will now spin and heat the room at whatever supply water temperature is circulating.

> [!NOTE]
> In our ESPHome package, disconnected probes are automatically filtered (`- lambda: if (x <= -30.0) return NAN;`), so Home Assistant cleanly marks the sensor as `Unavailable` without generating false alarms.

---

### Method 2: The 47 kΩ Parallel Resistor Hack (Community Mod)

Some community members have experimented with soldering or clipping a standard **$47\text{ k}\Omega$ resistor** in parallel across the leads of the $10\text{ k}\Omega\text{ NTC}$ $T_2$ water sensor to artificially lower the resistance seen by the analog-to-digital converter, shifting the reading up by $\approx +4^\circ\text{C}$.

> [!CAUTION]
> **Major Drawbacks & Why Method 1 is Recommended Instead**:
> 1. **Breaks Cooling Mode**: Shifting the temperature reading $+4^\circ\text{C}$ means that during summer, when chilled water is at $18^\circ\text{C}$, the PCB reads $22^\circ\text{C}$. Because $22^\circ\text{C} > 20^\circ\text{C}$, the fancoil thinks the water is too warm and **blocks the fan in cooling mode**!
> 2. **Inaccurate Sensor Values**: The water temperature reported to Home Assistant is distorted and non-linear across the curve.
> 
> **Conclusion**: **Method 1 (Disconnecting $T_2$) is the cleanest and recommended approach** for heating and cooling systems.

---

## 3. Board Architecture Differences

* **PU / PUB-30 / M7 Series (`n273025d`)**:
  * The 30 °C threshold is hardcoded in firmware and cannot be adjusted over Modbus registers. Use Method 1 or Method 2.
* **Bridge / Legacy Series (`n273025c` / INN-FR-B32 / ESE645)**:
  * Has a software-programmable register: **Register `218` (`LLO` - Minimum Water Temp for Heating)**.
  * You can adjust this register via Modbus down to **$20.0^\circ\text{C}$ or $0.0^\circ\text{C}$** directly in Home Assistant without touching hardware.
