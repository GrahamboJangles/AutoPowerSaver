import ctypes.wintypes
import sys
import os
import subprocess
import time

import ctypes
from ctypes.wintypes import WORD, DWORD, LONG, WCHAR, SHORT

POWER_SAVER_SCHEME = "e0c9d4c7-ac96-4ba8-9a87-57290851629c"  
HIGH_PERFORMANCE_SCHEME = "05d26255-5cd8-41c0-b290-d1d472bca0f9"
GPU_HWID = "PCI\VEN_10DE&DEV_25A0&SUBSYS_143E1025&REV_A1"
LOOP_TIME = 5

# Constants
ENUM_CURRENT_SETTINGS = -1
CDS_UPDATEREGISTRY = 0x01
CDS_TEST = 0x02
DISP_CHANGE_SUCCESSFUL = 0
DISP_CHANGE_RESTART = 1

# DEVMODE structure
class DEVMODE(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", WCHAR * 32),
        ("dmSpecVersion", WORD),
        ("dmDriverVersion", WORD),
        ("dmSize", WORD),
        ("dmDriverExtra", WORD),
        ("dmFields", DWORD),
        ("dmOrientation", SHORT),
        ("dmPaperSize", SHORT),
        ("dmPaperLength", SHORT),
        ("dmPaperWidth", SHORT),
        ("dmScale", SHORT),
        ("dmCopies", SHORT),
        ("dmDefaultSource", SHORT),
        ("dmPrintQuality", SHORT),
        ("dmColor", SHORT),
        ("dmDuplex", SHORT),
        ("dmYResolution", SHORT),
        ("dmTTOption", SHORT),
        ("dmCollate", SHORT),
        ("dmFormName", WCHAR * 32),
        ("dmLogPixels", WORD),
        ("dmBitsPerPel", DWORD),
        ("dmPelsWidth", DWORD),
        ("dmPelsHeight", DWORD),
        ("dmDisplayFlags", DWORD),
        ("dmDisplayFrequency", DWORD),
        ("dmICMMethod", DWORD),
        ("dmICMIntent", DWORD),
        ("dmMediaType", DWORD),
        ("dmDitherType", DWORD),
        ("dmReserved1", DWORD),
        ("dmReserved2", DWORD),
        ("dmPanningWidth", DWORD),
        ("dmPanningHeight", DWORD),
    ]

def elevate():
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Define necessary power status constants and structures
class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ('ACLineStatus', ctypes.c_byte),
        ('BatteryFlag', ctypes.c_byte),
        ('BatteryLifePercent', ctypes.c_byte),
        ('SystemStatusFlag', ctypes.c_byte),
        ('BatteryLifeTime', ctypes.c_ulong),
        ('BatteryFullLifeTime', ctypes.c_ulong),
    ]

GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
GetSystemPowerStatus.argtypes = [ctypes.POINTER(SYSTEM_POWER_STATUS)]
GetSystemPowerStatus.restype = ctypes.wintypes.BOOL

def get_ac_status():
    status = SYSTEM_POWER_STATUS()
    if not GetSystemPowerStatus(ctypes.pointer(status)):
        raise ctypes.WinError()
    return status.ACLineStatus

def change_refresh_rate(refresh_rate):
    # Get current settings
    devmode = DEVMODE()
    ctypes.windll.user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(devmode))

    # Change the refresh rate
    devmode.dmDisplayFrequency = refresh_rate

    # Test if the changes are valid
    if ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(devmode), CDS_TEST) == -1:
        print("Failed to apply display settings")
        return False

    # Apply the changes
    result = ctypes.windll.user32.ChangeDisplaySettingsW(ctypes.byref(devmode), CDS_UPDATEREGISTRY)

    if result == DISP_CHANGE_SUCCESSFUL:
        return True
    elif result == DISP_CHANGE_RESTART:
        print("You need to reboot for the changes to take effect.")
        return False
    else:
        print("Failed to apply display settings")
        return False

def disable_gpu_and_reduce_refresh_rate():
    print("Disabling GPU...")
    os.system(f'devcon disable "{GPU_HWID}"')
    change_refresh_rate(60)
    print("Switching to Power Saver Scheme")
    os.system(f'powercfg /setactive {POWER_SAVER_SCHEME}')

def enable_gpu_and_increase_refresh_rate():
    print("Enabling GPU...")
    os.system(f'devcon enable "{GPU_HWID}"')
    change_refresh_rate(144)
    print("Switching to High Performance Scheme")
    os.system(f'powercfg /setactive {HIGH_PERFORMANCE_SCHEME}')

def main_loop():
    # Initialize to the opposite of the current status, to trigger an
    # immediate switch to the correct power scheme
    last_ac_status = 1 - get_ac_status()

    while True:
        ac_status = get_ac_status()
        if ac_status != last_ac_status:
            if ac_status == 1:  # AC power
                print("AC power connected, enabling high performance mode.")
                enable_gpu_and_increase_refresh_rate()
            else:  # Battery power
                print("Running on battery, enabling power saving mode.")
                disable_gpu_and_reduce_refresh_rate()
            last_ac_status = ac_status
        time.sleep(LOOP_TIME)  # Wait for a while before checking again

if __name__ == '__main__':
    if not is_admin():
        elevate()
        sys.exit()

    main_loop()
