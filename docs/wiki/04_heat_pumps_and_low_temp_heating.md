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

There are three ways to enable low-temperature heating on Innova fancoils:

```
                            [ LOW-TEMP WATER SOLUTIONS ]
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
[ METHOD 0: MODBUS REGISTERS ] [ METHOD 1: PROBE DISCONNECT ]    [ METHOD 2: 47kΩ RESISTOR ]
• Software-based (RECOMMENDED) • Official Innova hardware bypass • Community hardware mod
• Adjust LLO down to 15-25°C   • Completely removes 30°C check   • Distorts reading (+4°C)
• Reg 510 (M7) / Reg 218 (Leg) • Disconnect T2 sensor before boot• Breaks cooling mode!
```

---

### Method 0: Adjusting Modbus Water Threshold Registers (Recommended)

Modern fancoils and bridge cards expose software-configurable water temperature limits over Modbus:

| Board Family | Minimum Water Temp for Heating (`LLO`) | Maximum Water Temp for Cooling (`LHI`) |
| :--- | :--- | :--- |
| **Modern PU / M7 / OSMO (`n273025d`)** *(Firmware 2.0+)* | **Register `510`** (Default: `300` = $30.0^\circ\text{C}$) | **Register `511`** (Default: `200` = $20.0^\circ\text{C}$) |
| **Bridge / Legacy Series (`n273025c`)** | **Register `218`** (Default: `300` = $30.0^\circ\text{C}$) | **Register `219`** (Default: `200` = $20.0^\circ\text{C}$) |

Both parameters are scaled at $0.1\ ^\circ\text{C}$ (e.g., write `250` for $25.0^\circ\text{C}$).

**How to use:**
1. In ESPHome or the Home Assistant custom integration, adjust the **"Minimum Water Temperature Heating (LLO)"** number slider down to your heat pump loop temperature (e.g., $22.0^\circ\text{C} - 25.0^\circ\text{C}$).
2. The fancoil will immediately accept water above this new threshold without locking the fan motor or displaying status faults.
3. Your $T_2$ water temperature sensor readings remain accurate and cooling mode remains completely functional.

---

### Method 1: Disconnecting the $T_2$ Water Sensor (Hardware Bypass Fallback)

For older PU / M7 units running legacy firmware (where Register 510 is not available):

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
> **Conclusion**: Whenever supported, **Method 0 (Modbus Registers 510/218)** is the optimal approach. If your board firmware does not respond to register 510, use **Method 1 (Disconnecting $T_2$)**. Avoid Method 2.

---

## 3. Board Architecture Differences

* **PU / PUB-30 / M7 Series (`n273025d`)**:
  * **Firmware 2.0+ (ID 1190 / EWA844II / OSMO / newer AirLeaf/Filomuro)**: Supports software adjustment via **Register `510` (`LLO`)** and **Register `511` (`LHI`)**.
  * **Older Firmware (e.g. 1.0 / 1.5)**: 30 °C threshold may not be configurable over Modbus; use Method 1 (probe disconnection).
* **Bridge / Legacy Series (`n273025c` / INN-FR-B32 / ESE645)**:
  * Supports software adjustment via **Register `218` (`LLO` - Minimum Water Temp for Heating)** and **Register `219` (`LHI` - Maximum Water Temp for Cooling)**.
  * You can adjust these registers via Modbus down to **$15.0^\circ\text{C} - 25.0^\circ\text{C}$** directly in ESPHome or Home Assistant without touching hardware.
