# innova-modbus

A backend-neutral, asynchronous Python library for controlling **Innova Fancoils** (OSMO, AirLeaf, FÄRNA, Filomuro, Filoterra) over Modbus RTU or Modbus TCP.

Built using [`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/) and following modern Home Assistant integration architecture.

## Supported Board Families

1. **`n273025d`** (Modern on-board and M7 wall controllers: ECA789, PUB-30, EEB749, ECA844, ECA044)
2. **`n273025c`** (Legacy touchscreen and Modbus bridge retrofits: INN-FR-B32, ECA644, EDA649)
