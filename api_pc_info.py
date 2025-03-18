# API для отдачи информации о PC
# pip install psutil wmi
# http://localhost:5000/system_info  - посмотреть информацию PC
from flask import Flask, jsonify
import psutil
import platform
import subprocess
import os

app = Flask(__name__)


def get_cpu_info():
    try:
        cpu_info = {
            "model": platform.processor(),
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
            "max_freq": psutil.cpu_freq().max if hasattr(psutil, "cpu_freq") else None,
        }
        return cpu_info
    except Exception as e:
        return {"error": str(e)}


def get_disk_info():
    try:
        disk = psutil.disk_usage('/')
        disk_info = {
            "total": disk.total,
            "free": disk.free,
            "used": disk.used,
        }

        # Получение названия диска (работает на Linux/Windows)
        if platform.system() == "Linux":
            result = subprocess.check_output(["lsblk", "-o", "MODEL", "-n", "-d"]).decode().strip()
            disk_info["model"] = result if result else "Unknown"
        elif platform.system() == "Windows":
            import wmi
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                disk_info["model"] = disk.Model
                break
        else:
            disk_info["model"] = "Unsupported OS"

        return disk_info
    except Exception as e:
        return {"error": str(e)}


def get_ram_info():
    try:
        ram = psutil.virtual_memory()
        ram_info = {
            "total": ram.total,
            "available": ram.available,
            "used": ram.used,
        }

        # Получение названия и частоты (требует прав администратора на Linux)
        if platform.system() == "Linux":
            try:
                output = subprocess.check_output(["dmidecode", "--type", "memory"]).decode()
                manufacturer = [line.split(":")[1].strip() for line in output.splitlines() if
                                "Manufacturer:" in line][0]
                speed = \
                [line.split(":")[1].strip() for line in output.splitlines() if "Speed:" in line][0]
                ram_info.update({"manufacturer": manufacturer, "speed": speed})
            except:
                ram_info.update({"manufacturer": "Unknown", "speed": "Unknown"})
        elif platform.system() == "Windows":
            import wmi
            c = wmi.WMI()
            for mem in c.Win32_PhysicalMemory():
                ram_info["manufacturer"] = mem.Manufacturer
                ram_info["speed"] = mem.Speed
                break
        else:
            ram_info.update({"manufacturer": "Unsupported OS", "speed": None})

        return ram_info
    except Exception as e:
        return {"error": str(e)}


@app.route('/system_info', methods=['GET'])
def system_info():
    data = {
        "cpu": get_cpu_info(),
        "disk": get_disk_info(),
        "ram": get_ram_info(),
    }

    # Добавляем температуру CPU (работает не на всех системах)
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            data["cpu"]["temperature"] = temps['coretemp'][0].current
    except AttributeError:
        pass

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)