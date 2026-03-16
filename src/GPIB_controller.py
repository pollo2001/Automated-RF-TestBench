import pyvisa
import time

class GPIB_Instrument:
    """Generic GPIB wrapper for SCPI instruments, decoupled from the UI."""
    def __init__(self, address="GPIB0::13::INSTR"):
        self.rm = pyvisa.ResourceManager()
        self.address = address
        self.instrument = None

    def connect(self):
        try:
            self.instrument = self.rm.open_resource(self.address)
            self.instrument.timeout = 5000
            return True, self.instrument.query('*IDN?')
        except Exception as e:
            return False, str(e)

    def set_offset(self, offset_db: float):
        """Hardware-level offset injection with anti-spam pacing."""
        if not self.instrument: return False, "Not connected"
        
        # Generic SCPI commands
        cmd = "OSOF" if offset_db == 0 else f"OS {offset_db} EN"
        self.instrument.write(cmd)
        
        # Anti-spam pacing to protect vintage hardware parsers from UI thread spam
        time.sleep(0.15) 
        return True, "Offset Set"

    def get_reading(self, settling_time_ms=200):
        if not self.instrument: return None
        # Allow RF hardware to slew and settle before triggering measurement
        time.sleep(settling_time_ms / 1000.0) 
        try:
            return float(self.instrument.query('TR1').strip())
        except:
            return None
