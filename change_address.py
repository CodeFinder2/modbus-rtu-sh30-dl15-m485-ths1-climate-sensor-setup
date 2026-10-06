import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

SERIAL_PORT = "/dev/ttyUSB0"
CURRENT_ID = 1      # Aktuelle ID (oder 0 als Broadcast)
NEW_ID = 5          # Neue Ziel-ID
BAUDRATE = 9600
REG_ADDRESS = 0x0100  # Wir wissen nun: 0x0100 (256) ist das richtige Register!

client = ModbusSerialClient(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1
)

if not client.connect():
    print(f"Konnte {SERIAL_PORT} nicht öffnen.")
    exit(1)

print(f"Setze Sensor-ID von {CURRENT_ID} auf {NEW_ID}...")

try:
    # Schreibbefehl absenden
    client.write_register(address=REG_ADDRESS, value=NEW_ID, device_id=CURRENT_ID)
    print("Schreibbefehl ohne Ausnahme gesendet.")
except ModbusIOException as e:
    # Das Abfangen des typischen Antwort-ID-Mismatches
    print("Mitteilung: Sensor hat die ID sofort übernommen und mit der neuen ID geantwortet (erwarteter Timeout/Mismatch).")

client.close()

# Kurze Pause, damit der Sensor sich neu initialisieren kann
time.sleep(1.5)

# Gegentest mit der neuen ID
print(f"Verifiziere neue ID {NEW_ID}...")
client.connect()
res = client.read_holding_registers(address=0, count=2, device_id=NEW_ID)

if not res.isError():
    temp = res.registers[0] / 10.0
    humi = res.registers[1] / 10.0
    print(f"✅ ERFOLG! Sensor antwortet unter ID {NEW_ID}: {temp:.1f}°C | {humi:.1f}%")
else:
    print(f"❌ Keine Antwort von ID {NEW_ID}. Bitte Sensor kurz von der Stromversorgung trennen.")

client.close()

