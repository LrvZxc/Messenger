@echo off
cd /d "%~dp0"

start cmd /k python mserver.py
start cmd /k python mclient.py
start cmd /k python mclient.py