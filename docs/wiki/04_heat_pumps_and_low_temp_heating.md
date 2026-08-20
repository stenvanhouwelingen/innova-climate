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

For users who want to keep live water temperature monitoring in Home Assistant while enabling heating at $26^\circ\text{C}$:

1. Solder or clip a standard **$47\text{ k}\Omega$ metal film resistor** in parallel across the two leads of the $10\text{ k}\Omega\text{ NTC}$ $T_2$ water sensor.
2. **Result**:
   * Placing $47\text{ k}\Omega$ in parallel with the thermistor lowers the effective resistance seen by the analog-to-digital converter.
   * This artificially shifts the temperature reading up by approximately **$+3.5^\circ\text{C}\ \text{to}\ +4.5^\circ\text{C}$**.
   * When actual water temperature is **$26.5^\circ\text{C}$**, the PCB reads **$30.5^\circ\text{C}$**, clearing the 30 °C gate and allowing heating to commence.
   * Safety limits remain functional (just with a shifted baseline).

---

## 3. Board Architecture Differences

* **PU / PUB-30 / M7 Series (`n273025d`)**:
  * The 30 °C threshold is hardcoded in firmware and cannot be adjusted over Modbus registers. Use Method 1 or Method 2.
* **Bridge / Legacy Series (`n273025c` / INN-FR-B32 / ESE645)**:
  * Has a software-programmable register: **Register `218` (`LLO` - Minimum Water Temp for Heating)**.
  * You can adjust this register via Modbus down to **$20.0^\circ\text{C}$ or $0.0^\circ\text{C}$** directly in Home Assistant without touching hardware.
