import os
import subprocess
import ctypes
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from pathlib import Path

class SystemOps:
    """
    Tactical System Operations for Windows.
    Part of Milestone 1: Deep OS Integration.
    """
    
    @staticmethod
    def get_volume():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        return int(volume.GetMasterVolumeLevelScalar() * 100)

    @staticmethod
    def set_volume(level: int):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(level / 100, None)
        return f"Volume set to {level}%"

    @staticmethod
    def set_brightness(level: int):
        # Using PowerShell to set brightness
        cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        return f"Brightness set to {level}%"

    @staticmethod
    def list_services(filter_str: str = ""):
        cmd = "Get-Service"
        if filter_str:
            cmd += f" -Name '*{filter_str}*'"
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        return result.stdout

    @staticmethod
    def restart_service(service_name: str):
        cmd = f"Restart-Service -Name '{service_name}' -Force"
        result = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Service {service_name} restarted successfully."
        return f"Failed to restart {service_name}: {result.stderr}"

# Singleton helper
ops = SystemOps()
