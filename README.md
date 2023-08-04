# AutoPowerSaver
This script runs in the background, detects if the laptop is charging or running on battery, and then automatically adjusts the power scheme, display refresh rate, and enables/disables the dedicated GPU.

# HOW TO RUN
Make sure to change these variables to the corresponding values for your system:

```python
POWER_SAVER_SCHEME = "e0c9d4c7-ac96-4ba8-9a87-57290851629c"  
HIGH_PERFORMANCE_SCHEME = "05d26255-5cd8-41c0-b290-d1d472bca0f9"
GPU_HWID = "PCI\VEN_10DE&DEV_25A0&SUBSYS_143E1025&REV_A1"
```

You can get these values using `cmd.exe powercfg /list` and the GPU_HWID you can find using Device Manager -> Properties -> Details -> then selecting the topmost value under the Hardware Ids values. You can also use [devcon.exe (which is a cmd interface for device manager from Microsoft)](https://github.com/Drawbackz/DevCon-Installer/releases)
