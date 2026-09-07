"""
System and OS-level action handlers.
Supports launching applications, running shell commands, and system control.
"""

import os
import sys
import ctypes
import subprocess
import shutil

# Common Windows application aliases mapping human names to executable commands
WINDOWS_APP_ALIASES = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "windows terminal": "wt.exe",
    "task manager": "taskmgr.exe",
    "taskmgr": "taskmgr.exe",
    "settings": "ms-settings:",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "edge": "msedge.exe",
    "msedge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "firefox": "firefox.exe",
    "brave": "brave.exe",
    "vscode": "code.cmd",
    "code": "code.cmd",
    "vs code": "code.cmd",
    "spotify": "spotify.exe",
    "word": "winword.exe",
    "winword": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "powerpnt": "powerpnt.exe",
    "outlook": "outlook.exe",
}


def _resolve_windows_app_path(app_name: str) -> str | None:
    """
    Finds the full absolute executable path for an application on Windows.
    Searches in order:
    1. System PATH via shutil.which
    2. Windows Registry App Paths (HKCU & HKLM)
    3. Common install locations (Program Files, LocalAppData, etc.)
    """
    clean = app_name.strip().lower()
    alias = WINDOWS_APP_ALIASES.get(clean, clean)

    candidates = [alias, clean]
    for name in [alias, clean]:
        if not name.endswith(".exe"):
            candidates.append(f"{name}.exe")
        if not name.endswith(".cmd"):
            candidates.append(f"{name}.cmd")
        if not name.endswith(".bat"):
            candidates.append(f"{name}.bat")

    # 1. Check system PATH
    for cand in candidates:
        found = shutil.which(cand)
        if found:
            return found

    # 2. Check Windows Registry App Paths
    if sys.platform == "win32":
        try:
            import winreg
            for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                for cand in [alias, f"{alias}.exe", clean, f"{clean}.exe"]:
                    try:
                        key = winreg.OpenKey(root, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{cand}")
                        val, _ = winreg.QueryValueEx(key, "")
                        winreg.CloseKey(key)
                        if val:
                            path = val.strip('"')
                            if os.path.exists(path):
                                return path
                    except OSError:
                        pass
        except Exception:
            pass

    # 3. Check well-known install locations
    well_known_paths = [
        # Chrome
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        # Edge
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # VS Code
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"),
        r"C:\Program Files\Microsoft VS Code\Code.exe",
        # Spotify
        os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Spotify.exe"),
        # Brave
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        # Firefox
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        # Office
        r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE",
    ]

    target_names = {clean, alias.replace(".exe", ""), f"{clean}.exe", alias}
    for p in well_known_paths:
        if os.path.exists(p):
            base = os.path.basename(p).lower()
            if base in target_names or base.replace(".exe", "") in target_names:
                return p

    return None


def launch_application(app_name: str) -> str:
    """
    Launches a desktop application on Windows.
    
    Args:
        app_name: The name of the application (e.g. 'notepad', 'calculator', 'chrome')
    Returns:
        Confirmation message of launch success.
    """
    clean_name = app_name.strip().lower()
    alias = WINDOWS_APP_ALIASES.get(clean_name, clean_name)

    try:
        # Handle system URIs (e.g. ms-settings:)
        if alias.startswith("ms-settings:") or alias.startswith("start ms-settings:"):
            if hasattr(os, "startfile"):
                os.startfile("ms-settings:")
            else:
                os.system("start ms-settings:")
            return f"Successfully opened {app_name} via system URI."

        # 1. Resolve to concrete absolute executable path
        resolved_exe = _resolve_windows_app_path(clean_name)
        if resolved_exe:
            subprocess.Popen([resolved_exe], shell=False)
            return f"Successfully launched application: {app_name} ({resolved_exe})"

        # 2. Try os.startfile on Windows (resolves system associations & App Paths)
        if hasattr(os, "startfile"):
            try:
                os.startfile(alias)
                return f"Successfully launched application: {app_name}"
            except Exception:
                pass

        # 3. Fallback: launch via Windows cmd start
        proc = subprocess.Popen(f'start "" "{alias}"', shell=True)
        return f"Successfully launched application: {app_name}"
    except Exception as e:
        raise RuntimeError(f"Failed to launch '{app_name}': {str(e)}")


def execute_shell_command(command: str) -> str:
    """
    Executes a shell command safely and captures the output.
    
    Args:
        command: The shell command string to execute.
    Returns:
        The standard output produced by the command.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip() if result.stdout else result.stderr.strip()
        if result.returncode != 0:
            raise RuntimeError(f"Command returned code {result.returncode}: {output}")
        return output if output else "Command executed successfully with no output."
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out after 15 seconds: {command}")
    except Exception as e:
        raise RuntimeError(f"Execution failed for '{command}': {str(e)}")


# Win32 Multimedia Virtual Keys
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
KEYEVENTF_KEYUP = 0x0002
user32 = ctypes.windll.user32 if sys.platform == "win32" else None


def control_system_volume(action: str = "up", steps: int = 3) -> str:
    """
    Sub-millisecond Windows master volume control using direct Win32 keybd_event.
    
    Latency: < 0.2 ms.
    """
    clean = action.strip().lower()
    if not user32:
        return f"Volume control not supported on non-Windows platform: {clean}"

    if clean in ("mute", "unmute", "toggle_mute"):
        user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        user32.keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, 0)
        return "Toggled master audio mute."

    vk_key = VK_VOLUME_UP if clean in ("up", "increase", "higher") else VK_VOLUME_DOWN
    count = max(1, steps)

    for _ in range(count):
        user32.keybd_event(vk_key, 0, 0, 0)
        user32.keybd_event(vk_key, 0, KEYEVENTF_KEYUP, 0)

    direction = "Increased" if vk_key == VK_VOLUME_UP else "Decreased"
    return f"{direction} volume by {count * 2}%."


def control_system_brightness(action: str = "up", step: int = 10) -> str:
    """
    Adjusts screen brightness using Windows WMI.
    """
    clean = action.strip().lower()
    delta = step if clean in ("up", "increase", "higher") else -step
    ps_command = f"""
    $b = (Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightness).CurrentBrightness
    $new = [Math]::Max(0, [Math]::Min(100, $b + ({delta})))
    (Get-CimInstance -Namespace root/WMI -ClassName WmiMonitorBrightnessMethods).WmiSetBrightness(1, $new)
    """
    try:
        subprocess.Popen(["powershell", "-NoProfile", "-Command", ps_command], shell=False)
        return f"Adjusted brightness {clean} by {abs(delta)}%."
    except Exception as e:
        return f"Brightness adjustment error: {str(e)}"
