# Chapter 2: Internal Workings & Control Physics

Innova fancoils utilize a Brushless DC (BLDC) motor coupled with electronic continuous modulation (ECM) to provide smooth, stepless airflow regulation.

---

## 1. Proportional-Integral (PI) Fan Speed Regulation

The onboard microcontroller does **not** switch between stepped AC fan speeds. Instead, it continuously samples the ambient air temperature and computes the instantaneous thermal error:

$$\Delta T = |T_{\text{ambient}} (T_1) - T_{\text{setpoint}}|$$

```
   FAN RPM
     ▲
1500 ┼───────────────────────────────┐ (High Speed / Quick Warmup)
     │                              /
     │                             / ◄── Continuous Inverter Modulation
 800 ┼                            /
     │                           /
 400 ┼──────────────────────────/ (Silent / Maintenance Speed)
   0 ┼──────────────┼───────────┼───────────► ΔT (°C)
     0            0.5°C        2.0°C+
```

### Factory Modbus Motor Limits

The exact rotational speeds are programmed into the controller firmware (and exposed on Modbus registers `210` to `215` on bridge units):

| Operating Mode | Register / Logic | Motor Speed (RPM) | Acoustic Level (ISO 7779) |
| :--- | :--- | :---: | :---: |
| **Night / Silent** | Register `210` (`Mvv5`) | **$400\text{ RPM}$** | **$< 18.8\text{ dB(A)}$** |
| **Auto Dynamic** | Register `213` (`Mvv2`) | **$400 - 1100\text{ RPM}$** | $19 - 30\text{ dB(A)}$ |
| **Max / Boost** | Register `214` (`Mvv1`) | **$1500\text{ RPM}$** | $38.4\text{ dB(A)}$ |
| **Performance Max** | Register `215` (`MvvP1`) | **$1700\text{ RPM}$** | $42.0\text{ dB(A)}$ |

1. **Large Error ($\Delta T \ge 2.0^\circ\text{C}$)**: Fan accelerates to high speed ($1100 - 1500\text{ RPM}$) to quickly bridge the temperature gap.
2. **Medium Error ($0.5^\circ\text{C} < \Delta T < 2.0^\circ\text{C}$)**: Fan speed modulates smoothly along the PI curve.
3. **Low Error ($\Delta T \le 0.5^\circ\text{C}$)**: Fan settles at minimum floor speed ($400\text{ RPM}$), producing whisper-quiet maintenance airflow.
4. **Target Satisfied ($\Delta T = 0$)**: The valve actuator (`Y1`) is de-energized and the motor executes a soft stop.

---

## 2. Thermodynamics: Water Temperature vs. Fan Speed

A common point of confusion is whether water temperature directly dictates fan speed:

> **Core Principle**: The fan speed controller **only** responds to the **air temperature error** ($\Delta T_{\text{air}}$). It does **not** dynamically change RPM based on water temperature.

### How Water Temperature Affects System Behavior:
* **Thermal Power Output Formula**:
  $$\dot{Q} = \dot{m} \cdot c_p \cdot (T_{\text{water, in}} - T_{\text{water, out}})$$
* **Hot Water ($45^\circ\text{C} - 50^\circ\text{C}$)**:
  * High thermal transfer rate ($\text{kW}$).
  * Room warms rapidly $\to$ $\Delta T_{\text{air}}$ collapses within minutes $\to$ Fan slows down to minimum speed quickly.
* **Low-Temperature Water ($26^\circ\text{C} - 32^\circ\text{C}$)**:
  * Low thermal transfer rate ($\text{kW}$).
  * Room warms slowly $\to$ $\Delta T_{\text{air}}$ remains high $\to$ Fan stays at higher RPM for longer trying to satisfy the room setpoint.

---

## 3. Auto Season Changeover (2-Pipe vs. 4-Pipe)

* **2-Pipe Installations**:
  * In `Auto` season mode (Register `556 = 0`), the board samples the inlet water sensor ($T_2$).
  * If $T_2 > 25^\circ\text{C} - 30^\circ\text{C}$ $\to$ Automatically enters **Heating mode**.
  * If $T_2 < 18^\circ\text{C} - 20^\circ\text{C}$ $\to$ Automatically enters **Cooling mode**.
* **4-Pipe Installations**:
  * Two separate hydraulic loops (`Y1` for cooling coil, `Y2` for heating coil). The controller switches between valves automatically based on room temperature demands.

---

## 4. De-Stratification (Anti-Stratification) Cycle

In heating mode, hot air naturally rises toward the ceiling (thermal stratification). When the fancoil is idle (setpoint reached, valve closed), the unit periodically initiates a slow, silent circulation pulse ($300\text{ RPM}$) to draw down warm ceiling air and prevent cold spots near the floor.
