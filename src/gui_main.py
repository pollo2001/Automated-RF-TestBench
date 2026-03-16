import customtkinter as ctk
import serial
import time
import csv
from rf_controller import GPIB_Instrument

class AutomatedTestBench(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HIL Automated Test Bench")
        
        self.ser = None
        self.bench = GPIB_Instrument("GPIB0::13::INSTR")
        self.is_sweeping = False
        self.prev_pwr = None # Tracking for Ghost Tripwire

        # --- [UI COMPONENT SETUP REDACTED FOR BREVITY] ---
        # Initialize CTk elements here (Buttons, Entries, Labels)
        # e.g., self.e_time = ctk.CTkEntry(...) 
        # -------------------------------------------------

    # ==========================================
    # SERIAL COMMUNICATION LAYER
    # ==========================================
    def toggle_connect(self):
        """Establishes non-blocking UART connection to target MCU."""
        if self.ser is None:
            try:
                # Target baud 115200, non-blocking timeout
                self.ser = serial.Serial("COM3", 115200, timeout=0.5)
                self.ser.setDTR(True); self.ser.setRTS(True)
                time.sleep(0.5)
                self.ser.reset_input_buffer()
                print("Target MCU Connected.")
            except Exception as e:
                print(f"Connection Error: {e}")
        else:
            self.ser.close(); self.ser = None

    def safe_serial_write(self, cmd_str: str):
        """Thread-safe UART writing with buffer clearing and basic pacing."""
        if not self.ser: return False
        self.ser.reset_input_buffer()
        self.ser.write(cmd_str.encode("ascii"))
        self.ser.flush()
        time.sleep(0.05) # Tiny I/O pacing
        return True

    # ==========================================
    # SWEEP ENGINE & HARDWARE PROTECTION
    # ==========================================
    def toggle_sweep(self):
        """Initializes the automated sweep and enforces hardware safety limits."""
        if not self.ser or self.is_sweeping: return
        
        # Pseudo-fetch user inputs from UI
        # swp_start, swp_stop, swp_step = ...
        self.swp_time = 500 # Default fallback
        
        # --- HARDWARE PROTECTION---
        # Prevents users from inputting <400ms. High-speed commands cause 
        # UART-to-SPI buffer overflows and watchdog resets on the target MCU.
        if self.swp_time < 400:
            self.swp_time = 400
            # self.e_time.insert(0, "400") # Force UI update feedback
        # ---------------------------------------------------

        self.is_sweeping = True
        self.prev_pwr = None # Reset tripwire for new run
        
        # Initialize CSV log...
        
        self.execute_sweep_move()

    def execute_sweep_move(self):
        """Commands MCU to move to the next frequency state."""
        if not self.is_sweeping: return
        
        # Check if sweep complete logic...
        
        # ... [Calculate next frequency and channel routing] ...
        target_mhz = 1000.0 # Pseudo-calculated target
        
        try:
            # Send generic UART command for target frequency
            self.safe_serial_write(f"CMD_SET_FREQ,{int(target_mhz * 10_000)}\r")
            
            # ... [Handle secondary channel routing/dividers if needed] ...
            
        except Exception as e:
            print("Hardware Error")
            self.is_sweeping = False
            return

        # Schedule the measurement after the hard-floored settle time
        self.after(self.swp_time, self.execute_sweep_measure)

    def execute_sweep_measure(self):
        """Reads instrument, runs tripwire logic, and logs data."""
        if not self.is_sweeping: return
        
        pwr = self.bench.get_reading()

        # ---DELTA CRASH DETECTOR---
        # A 0-polling method to detect MCU watchdog resets. 
        # By calculating the derivative of the GPIB power readings in RAM, 
        # we detect catastrophic hardware failures (>30dB instant drop)
        # without adding serial overhead to the target MCU.
        if pwr is not None and self.prev_pwr is not None:
            if (self.prev_pwr - pwr) > 30.0:
                print("CRASH HALT: >30dB Drop Detected. MCU likely rebooted.")
                self.is_sweeping = False
                return
        
        if pwr is not None:
            self.prev_pwr = pwr
        # ---------------------------------------------

        # ... [CSV Logging and UI live readout updates redacted] ...

        # Loop to next step
        self.execute_sweep_move()

if __name__ == "__main__":
    app = AutomatedTestBench()
    # app.mainloop() # Uncomment to run CustomTkinter loop
