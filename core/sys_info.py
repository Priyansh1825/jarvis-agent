import psutil
import platform
import socket
import datetime
import os

def get_system_diagnostics() -> dict:
    """Collects comprehensive real-time system and hardware health metrics."""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count(logical=True)
    
    # RAM
    ram = psutil.virtual_memory()
    ram_total_gb = round(ram.total / (1024 ** 3), 1)
    ram_used_gb = round(ram.used / (1024 ** 3), 1)
    ram_percent = ram.percent
    
    # Battery
    battery = psutil.sensors_battery()
    battery_info = {
        "present": battery is not None,
        "percent": battery.percent if battery else None,
        "power_plugged": battery.power_plugged if battery else None,
    }
    
    # Disk (System Drive)
    disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
    disk_free_gb = round(disk.free / (1024 ** 3), 1)
    disk_total_gb = round(disk.total / (1024 ** 3), 1)
    disk_percent = disk.percent
    
    # Network & Host
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"
        
    # Uptime
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = str(datetime.datetime.now() - boot_time).split('.')[0]
    
    return {
        "os": f"{platform.system()} {platform.release()}",
        "hostname": hostname,
        "local_ip": local_ip,
        "uptime": uptime,
        "cpu_usage_percent": cpu_percent,
        "cpu_threads": cpu_count,
        "ram_used_gb": ram_used_gb,
        "ram_total_gb": ram_total_gb,
        "ram_usage_percent": ram_percent,
        "disk_free_gb": disk_free_gb,
        "disk_total_gb": disk_total_gb,
        "disk_usage_percent": disk_percent,
        "battery": battery_info
    }

def format_system_report() -> str:
    """Formats system diagnostics into a concise string suitable for voice reporting."""
    stats = get_system_diagnostics()
    
    battery_str = "Desktop power (No battery detected)"
    if stats["battery"]["present"]:
        status = "charging" if stats["battery"]["power_plugged"] else "on battery power"
        battery_str = f"{stats['battery']['percent']}% ({status})"
        
    report = (
        f"System Status Report: "
        f"CPU is running at {stats['cpu_usage_percent']}%. "
        f"Memory utilization is at {stats['ram_usage_percent']}% ({stats['ram_used_gb']} GB of {stats['ram_total_gb']} GB used). "
        f"Storage free: {stats['disk_free_gb']} GB available on drive. "
        f"Power status: {battery_str}. "
        f"System uptime: {stats['uptime']}."
    )
    return report

if __name__ == "__main__":
    print(format_system_report())
