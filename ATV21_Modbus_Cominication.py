import serial
import time
import struct

# Seri bağlantıyı aç
ser = serial.Serial(
    port='/dev/ttyUSB0',  # USB-RS485 dönüştürücü takılan yer
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

def modbus_crc(data):
    """ CRC16 hesaplama fonksiyonu """
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def send_modbus_command(device_address, function_code, register_address, value):
    """ ATV21'e Modbus RTU komutu gönderir """
    message = struct.pack('>BBHH', device_address, function_code, register_address, value)
    message += modbus_crc(message)  # CRC ekle
    ser.write(message)
    time.sleep(0.1)  # Cihazın yanıt vermesi için bekleme
    response = ser.read(8)  # Cihazdan gelen yanıtı oku
    return response

# **Örnek Kullanım**: ATV21 motor sürücüsünü çalıştırma
device_id = 1   # ATV21 Modbus ID (genellikle 1)
func_code = 6   # Tek Register Yazma (Modbus function 0x06)
reg_address = 0x2000  # ATV21'in "Hız Referansı" register adresi
speed_value = 200  # Çalışma frekansı (örnek: 20.0 Hz için 200 gönder)

response = send_modbus_command(device_id, func_code, reg_address, speed_value)
print("Yanıt:", response.hex())

# **Motoru Başlat**
reg_address = 0x2001  # Çalıştırma komutu adresi
run_command = 1  # Motoru çalıştır

response = send_modbus_command(device_id, func_code, reg_address, run_command)
print("Motor başlatıldı, yanıt:", response.hex())

ser.close()
