# Chapter 5: Control Boards & DIP Switch Configurations

Innova fancoil units utilize several generations of onboard electronic control boards. Setting the physical DIP switches correctly before applying power is required to enable Modbus RTU communication.

---

## 1. Board Family Identification

| Board Model | Typical Units | DIP Switch Count | Modbus Activation Switch |
| :--- | :--- | :---: | :--- |
| **PUB-30 / PU Series** | AirLeaf (exposed), >OSMO<, FÄRNA, Ducto | 4 + Jumper | **DIP Switch `F = ON`** (or Switch 1) at power-on |
| **ES690II / Smart Touch** | Filomuro SWI 400 (in-wall), newer Smart Touch | 6 | **DIP Switch `6 = ON`** before power-on |
| **INN-FR-B32 / ESE645** | Filoterra, older Filomuro Slim Fit | 4 | ASCII/RTU Jumper |

---

## 2. DIP Switch Configuration for Modbus RTU

The board microcontroller samples the physical switch positions **only during bootloader initialization (at power-on)**. Any switch changes made while the board is powered will be ignored until mains power is cycled.

```
       PU / PUB-30 BOARD                     ES690II BOARD (6 SWITCHES)
    ┌─────────────────────┐                   ┌────────────────────────┐
    │  [ON]               │                   │  [ON]                  │
    │  ┌───┬───┬───┬───┐  │                   │  ┌───┬───┬───┬───┬───┬───┐│
    │  │ 1 │ 2 │ 3 │ F │  │                   │  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 ││
    │  └───┴───┴───┴───┘  │                   │  └───┴───┴───┴───┴───┴───┘│
    │               ▲     │                   │                       ▲│
    │          SWITCH F=ON│                   │             SWITCH 6=ON│
    └─────────────────────┘                   └────────────────────────┘
```

### Critical Rules:
1. **PU / PUB-30**: Ensure switch **`F`** (or the designated Modbus switch) is in the **`ON`** position.
2. **ES690II (New 6-Switch Boards)**: Ensure **DIP switch `6`** is set to **`ON`** before turning on power. If switch 6 is off, the RS-485 port will not respond to Modbus requests and will produce communication timeouts.
3. **Serial Parameters**: Modbus RTU, **`9600 baud, 8 Data bits, No Parity, 1 Stop bit (9600-8N1)`**, Default Slave Address **`1`**.

---

## 3. Silencing the Onboard Touchscreen Buzzer

On fancoils with on-board touch keypads (CB-Touch), button presses trigger a loud high-pitched piezoelectric beep that can disturb sleeping occupants in bedrooms:

* **Hardware Mod**: Place a small dab of silicone sealant, blue-tack, or insulating tape over the small round sound hole on top of the black piezo buzzer cylinder located on the PCB. This attenuates the volume by ~80% without damaging the electronics.
