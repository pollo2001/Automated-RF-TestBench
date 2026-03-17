# **Automated-RF-TestBench**
**NDA-compliant educational release** of the framework designed for modern Smart PLL synthesizers. This project provides a cross-compatible, Python-based GUI for serial control and automated hardware-in-the-loop (HIL) testing, replacing legacy LabVIEW test benches. Significant portions have been redacted or sanitized to comply with NDA and educational guidelines.

---

### Overview
This project demonstrates the **core architecture** of a real-time GUI used to automate frequency/power sweeps by synchronizing MCU-controlled PLL synthesizers over UART with legacy GPIB test equipment. 
The GUI layer runs asynchronously, handling command queues, serial communications, and data logging, while strictly respecting the embedded hardware's internal timing and RF loop constraints.

This framework was developed with reliability and timing practices aligned with high-performance RF systems.

---

### Tech Stack & Requirements
- **Python 3.12+**
- **`pyvisa`**: Industry-standard library used for SCPI/IEEE-488 communication to decouple and control the GPIB test equipment.
- **`pyserial`**: Handles the non-blocking UART communication with the embedded target MCU.
- **`customtkinter`**: Provides the modern, asynchronous GUI framework.

---

### Framework Highlights
- **Serial Communication:** Auto-detects, safely connects/disconnects, and utilizes non-blocking TX/RX for generic target MCUs.
- **GPIB Instrument Decoupling:** Abstracts SCPI/VISA commands into a dedicated controller class, equipped with anti-spam traffic delays for vintage test equipment.
- **Hardware Protection:** Implements hardcoded input clamping on loop pacing to physically prevent UART-to-SPI buffer overflows that cause watchdog resets on embedded targets.
- **Zero-Polling Crash Detection:** To avoid interrupting the MCU with status polls during a high-speed sweep, the software calculates the derivative (Delta) of the incoming GPIB power readings. Instantaneous drops (>30 dB) trigger an automatic system halt, successfully detecting MCU reboots with zero I/O overhead.
- **Smart Channel Routing:** Automatically calculates reverse-algebra and prescaler divider routing to achieve target output frequencies before taking measurements.

---

### Structure
```text
Smart_PLL_Interface/
│
├── src/
│   ├── gui_main.py         # GUI frontend – controls, sweep engine, and routing logic
│   ├── GPIB_controller.py  # Backend – GPIB instrument I/O and serial abstractions
│   └── run_sweep.bat       # Boot-strap Launcher
├── README.md               # Documentation
└── LICENSE                 # MIT (educational use)
```
---

# SSG_POWER_SWEEP v1.0 - Maintenance & Deployment Guide

### 1. The Launcher Strategy (.bat vs .exe)
While a compiled .exe offers a single-file look, 'run_sweep.bat' 
provides a more robust deployment for lab environments. It 
functions as a "Bootstrap Launcher":
- It silently verifies/installs dependencies (PyVISA, etc.) on 
  the host bench before execution.
- It eliminates "Module Not Found" errors caused by PyInstaller 
  hidden-import conflicts with legacy NI-VISA backends.
- It provides a transparent console for real-time debugging if 
  a hardware connection fails.

### 2. Deployment to Test Benches
To add this tool to a new bench:
1. Navigate to this network folder from the bench PC.
2. Right-click 'run_sweep.bat' -> Send to -> Desktop (shortcut).
3. Change Icon: Right-click Shortcut -> Properties -> Change Icon 
   -> Browse to 'thum.ico' in this network folder.

### 3. Data Integrity & Overwrite Protection
- The script generates .csv results in this root folder.
- CRITICAL: Filenames are derived from the 'Serial Number' field. 
  Always update the SN or Identifier before a new sweep to 
  avoid overwriting previous test data.

### 4. Hardware Handoff
- If the sweep logic or SCPI commands need updating, edit 
'gui_main.py' directly. All benches will pull the update 
automatically on the next launch.

---

### Purpose
Educational reference for engineers or students learning:
- GUI ↔ MCU synchronization
- Serial communication and threading
- Real-time embedded control abstractions

---

### Disclaimer
This release is a sanitized, independent derivative created for demonstration and educational use only. The core architecture and system flow were inspired by hardware-in-the-loop (HIL) automation challenges I solved at Z-Communications, Inc.

To fully comply with NDA and IP guidelines, all proprietary firmware commands, exact timing constraints, hardware identifiers, and confidential company data have been strictly generalized or removed. Over 50% of the code is redacted to adhere to complaince. This repository serves solely to showcase high-level embedded hardware control and UI decoupling.

### Dev
Genaro Salazar Ruiz
