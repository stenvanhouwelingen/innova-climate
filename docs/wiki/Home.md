# Innova Fancoil Technical Knowledge Base & Wiki

Welcome to the **Innova Fancoil Technical Knowledge Base**. This documentation contains an in-depth reference for the internal workings, physical control algorithms, sensor mechanics, and Modbus RTU integration across the entire Innova fancoil ecosystem (**Airleaf, Filomuro, >OSMO<, Filoterra, and Ducto**).

---

## 📚 Table of Contents

1. [**Chapter 1: Overview & Model Variants**](01_overview_and_models.md)
   * Product lineup breakdown: Airleaf SL, SLS (dwarf window sill), RS (radiant front panel), SLI (in-wall), Filomuro (high-wall), >OSMO<, Filoterra, Ducto.
   * Radiant panel mechanics and motorized flap louvers.

2. [**Chapter 2: Internal Workings & Control Physics**](02_internal_workings_and_physics.md)
   * Continuous Brushless DC (BLDC) inverter PI regulation.
   * Factory motor RPM ranges ($400 - 1500+\text{ RPM}$) and acoustic levels ($< 18.8\text{ dB(A)}$).
   * Thermodynamics: Why water temperature dictates thermal power (kW) rather than fan speed.
   * Auto season changeover and de-stratification cycles.

3. [**Chapter 3: Sensors & Standalone Operation**](03_sensors_and_standalone_operation.md)
   * Sensor electrical specs: $10\text{ k}\Omega\text{ NTC}$ thermistors ($B=3950$).
   * $T_1$ (Ambient Air), $T_2$ (Inlet Water), $T_3$ (Coil Temp), and $RH$ (Humidity).
   * Standalone setup without official wall panels (wiring 10k NTC to $T_1$).

4. [**Chapter 4: Heat Pumps & Low-Temperature Heating ($< 30^\circ\text{C}$ Water)**](04_heat_pumps_and_low_temp_heating.md)
   * The 30 °C water heating gate conflict with heat pump weather curves.
   * **Method 1**: Disconnecting the $T_2$ sensor (official Innova bypass).
   * **Method 2**: The $47\text{ k}\Omega$ parallel resistor hardware mod ($+4^\circ\text{C}$ shift).
   * Board differences: PU series (hardcoded) vs Legacy Bridge series (Register 218 `LLO`).

5. [**Chapter 5: Control Boards & DIP Switch Configurations**](05_control_boards_and_dip_switches.md)
   * Board identification: PUB-30, ES690II, INN-FR-B32.
   * Enabling Modbus RTU: Switch `F = ON` (PU) vs Switch `6 = ON` (ES690II).
   * Touch buzzer hardware silencing.

6. [**Chapter 6: Remote Supervisor Mode (Injecting External Temperatures)**](06_remote_supervisor_mode.md)
   * Purpose and operation for external thermostats (KNX, Zigbee, BLE).
   * Registers 100, 101, 102 (`REM_TA`) breakdown.
   * 5-minute (300 s) safety watchdog timer protocol.

7. [**Chapter 7: Modbus Register Deep Dive & Bitmasks**](07_modbus_register_deep_dive.md)
   * Complete register map (0 to 557).
   * Status Register 150 bitmask table.
   * Alarm Register 151 bitmask table.
   * Web control / lock Register 557 bitmask table.
