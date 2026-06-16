# Contributing to Innova Climate ESPHome Integration

Thank you for your interest in contributing to this project! Community contributions help make this integration more robust and feature-rich for everyone.

Please take a moment to review these guidelines before getting started.

---

## 💬 Discussions vs. Issues

- **Use Discussions** for general questions, setup/wiring assistance, sharing configurations, and open-ended design discussions.
- **Use Issues** only for reporting confirmed bugs or requesting specific feature enhancements with clear implementation details.

---

## 🐛 Reporting Bugs

Before opening an issue, please:
1. Search the existing issues and discussions to see if the problem has already been reported.
2. If not, open a new issue using the **Bug Report** template.
3. Provide as much detail as possible, including your fancoil model, ESP32 hardware setup, and relevant ESPHome log output (with log level set to `DEBUG`).

---

## 💡 Suggesting Features

We welcome ideas for new features! To request a feature:
1. Open an issue using the **Feature Request** template.
2. If the feature involves new Modbus registers or fancoil commands, please include documentation, register maps, or reference links if you have them.

---

## 🛠️ Development & Pull Requests

### 1. Repository Structure
- `esphome-innova.yaml`: Main configuration entry point for ESPHome.
- `components/innova_climate/`: Custom C++ climate component.
  - `climate.py`: ESPHome code generator and configuration definition.
  - `innova_climate.h`: Core C++ logic handling state representation and Modbus reads/writes.

### 2. PR Guidelines
When submitting a Pull Request, please follow these guidelines:
- **Branch naming**: Use descriptive branch names (e.g., `feature/humidity-setpoint` or `fix/temp-parsing`).
- **Code Style**: Ensure your C++ and Python code is clean, readable, and properly formatted. Keep all existing comments/docstrings intact unless they are being updated.
- **Testing**: Since this project interacts with physical HVAC hardware, we require all code changes to be tested on physical fancoil units before merging to prevent heating/cooling control issues. Please describe your hardware setup and test results in the PR.
- **Single Commit History**: We keep a clean, single-commit or linear git history. Keep your commits focused and descriptive.
