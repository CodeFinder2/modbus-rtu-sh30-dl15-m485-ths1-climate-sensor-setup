import time
from pymodbus.client import ModbusSerialClient

SERIAL_PORT = "/dev/ttyUSB0"
BAUDRATE = 9600
SENSOR_IDS = [1, 2] # [1, 2, 3, 4, 5]  # Deine konfigurierten IDs

client = ModbusSerialClient(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=0.5
)

if not client.connect():
    print(f"Konnte {SERIAL_PORT} nicht öffnen.")
    exit(1)

print("Starte Bus-Abfrage aller Sensoren...\n")

try:
    while True:
        output = []
        for sensor_id in SENSOR_IDS:
            res = client.read_holding_registers(address=0, count=2, device_id=sensor_id)
            
            if not res.isError():
                temp_raw = res.registers[0]
                humi_raw = res.registers[1]
                
                if temp_raw > 0x7FFF:
                    temp_raw -= 0x10000
                
                temp = temp_raw / 10.0
                humi = humi_raw / 10.0
                output.append(f"Sensor {sensor_id}: {temp:5.1f}°C | {humi:5.1f}%")
            else:
                output.append(f"Sensor {sensor_id}: keine Antwort")
        
        print(" | ".join(output))
        time.sleep(2)

except KeyboardInterrupt:
    print("\nBeendet.")
finally:
    client.close()
