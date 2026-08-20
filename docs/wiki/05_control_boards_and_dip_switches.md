# Chapter 5: Control Boards & DIP Switch Configurations

Innova fancoil units utilize several generations of onboard electronic control boards. Setting the physical DIP switches correctly before applying power is required to enable Modbus RTU communication.

---

## 1. Board Family Identification
Innova fancoils use three primary electronic board families depending on the model and generation:

| Board Family | Board Part Numbers | Typical Units | Key Identification |
| :--- | :--- | :--- | :--- |
| **PU / PUB-30 Series** | `PUB-30`, `ECA789`, `EEB749`, `ECA844`, `ECA044` | AirLeaf (exposed), >OSMO<, FÄRNA, Ducto | 4 DIP switches + Jumper. Firmware ID `1190`. |
| **Smart Touch / ES690 Series** | `ES690II`, `ESE690II`, `ES690` | Filomuro SWI 400 (in-wall), Smart Touch wall controls | **6 DIP switches**. No ASCII jumper. |
| **Bridge / Retrofit Series** | `INN-FR-B32`, `ESE645`, `ESE648`, `EDA649`, `EDB649`, `ECA644`, `ECA647` | Filoterra (in-floor), older Filomuro Slim Fit, older AirLeaf built-in | 4 DIP switches + ASCII/RTU Jumper. Programmable `LLO` register 218. |

---

## 2. RS-485 Modbus Wiring & Terminal Pinouts

The RS-485 Modbus serial connection is made on the terminal block labeled **`+ A B -`** (or **`+ A B GND`**) on the main board:

```
     INNOVA PCB SERIAL TERMINAL BLOCK               ESPHome / RS-485 CONVERTER
    ┌─────────────────────────────────┐             ┌─────────────────────────┐
    │  [+]  Aux 5V/12V Power (Opt.)   │────────────►│ VCC (Optional)          │
    │  [A]  RS-485 Non-inverting (D+) │────────────►│ A (D+)                  │
    │  [B]  RS-485 Inverting (D-)     │────────────►│ B (D-)                  │
    │  [-]  Signal Ground (GND)       │────────────►│ GND (Common Ground)     │
    └─────────────────────────────────┘             └─────────────────────────┘
```

### Cabling Best Practices:
* **Cable Type**: Use shielded twisted-pair cable (STP), such as Belden 9841, LiYCY $2 \times 0.35\text{ mm}^2$, or standard Cat5e/Cat6 (using one twisted pair for A/B and one wire for GND).
* **The #1 Gotcha: A/B Line Polarity**:
  * If ESPHome reports continuous Modbus timeouts (`Modbus checksum error` or `No response from slave 1`), **swap the `A` and `B` wires**. Different transceiver manufacturers occasionally label $D+$ as B and $D-$ as A.
* **120 Ω Bus Termination**:
  * For short runs ($< 20\text{ meters}$), termination resistors are usually unnecessary.
  * For long bus runs ($> 50\text{ meters}$) with multiple daisy-chained fancoils, add a $120\ \Omega\ (1/4\text{W})$ resistor across `A` and `B` at the farthest end of the line.

---

## 3. DIP Switch Configuration for Modbus RTU

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
