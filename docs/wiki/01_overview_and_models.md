# Chapter 1: Overview & Model Variants

Innova fancoils (hydronic fan coil units) are slim, DC inverter-driven convective and radiant terminals designed to heat and cool using water from a heat pump or boiler system.

---

## 1. Product Lineup & Hardware Variants

| Model Series | Installation Type | Chassis Depth | Key Characteristics |
| :--- | :--- | :---: | :--- |
| **Airleaf SL** | Low-Wall / Floor Exposed | $13\text{ cm}$ | The flagship model. Extremely slim depth, modern radiator form-factor. Sizes: `200`, `400`, `600`, `800`, `1000`. |
| **Airleaf SLS** | Low-Wall Under-Sill | $13\text{ cm}$ | Low-height variant ($\approx 38\text{ cm}$ high vs $58\text{ cm}$ on SL). Engineered for low window sills and knee-walls. |
| **Airleaf RS** | Low-Wall Radiant Panel | $13\text{ cm}$ | Features integrated water micro-tubes bonded directly to the steel front panel. Warms the front face like a static radiator during winter. |
| **Airleaf SLI / SLSI** | Recessed In-Wall / Ceiling | $13\text{ cm}$ | Bare frameless chassis designed to be built into stud walls, false ceilings, or drywall niches with supply/return grilles. |
| **Filomuro (SW / SWI)** | High-Wall (Air-to-Water) | $12.8\text{ cm}$ | High-wall hydronic unit mimicking the look of a ductless mini-split. Includes motorized oscillating air louvers and integrated drain pan. |
| **>OSMO<** | Floor / Low-Wall | $13\text{ cm}$ | Next-generation aesthetic chassis with refined grilles, integrated display option, and updated M7 control electronics. |
| **Filoterra** | In-Floor Trench | Flush | Embedded inside floor trenches for full-height glass facades and sliding doors. |
| **Ducto / Ducto Multi**| Concealed Ducted | Compact | High static pressure ducted units for multi-room distribution or ducted ceiling supply. |

---

## 2. Airleaf RS: The Radiant Front Panel Mechanic

The **Airleaf RS** model incorporates a unique dual-mode heating system:

```
                  ┌──────────────────────────────────────────────┐
                  │          HOT WATER SUPPLY INLET (T2)         │
                  └──────────────────────┬───────────────────────┘
                                         │
              ┌──────────────────────────┴──────────────────────────┐
              ▼                                                     ▼
   [ FRONT RADIANT PANEL ]                                [ MAIN FINNED COIL ]
  Micro-channel copper tubes                             Cross-fin heat exchanger
  bonded to front sheet metal.                           forced convection via fan.
  (Static radiant heat, 0 RPM)                           (High kW dynamic output)
```

1. **Micro-Convective Heating**: At low thermal demand, hot water circulates through the front casing micro-channels, heating the room silently through natural radiation and convection **without spinning the fan**.
2. **Dynamic Boost**: When a larger temperature gap is detected, the DC inverter fan spins up to blow air across the primary finned coil, quickly bringing the room up to the target temperature.

---

## 3. High-Wall Filomuro Mechanics

The **Filomuro** is specifically designed for bedrooms and offices where floor and low-wall space is occupied:
* **Motorized Flap (Louver)**: Driven by an internal stepper motor (Register `457`). Flap opens automatically on startup and can cycle in continuous oscillation or fixed angles.
* **Condensate Management**: Due to high-wall positioning, condensate drainage occurs via gravity out the rear or through a dedicated mini-condensate pump recess.
