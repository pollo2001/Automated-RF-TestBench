@echo off 
title "Launching AUTO RF Test Bench..."
echo checking Python dependencies...
pip install pyvisa pyvisa-py pyserial customtkinter --quiet
echo Starting GUI...
python main_gui.py
pause
