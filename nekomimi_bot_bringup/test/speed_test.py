import serial
import time

PORT = '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0'
BAUDRATE = 1000000

def checksum(data):
    return (~(sum(data) & 0xFF)) & 0xFF

def write_speed(ser, servo_id, speed):
    if speed < 0: speed_value = (abs(int(speed)) | 0x8000)
    else: speed_value = int(speed)

    spd_l = speed_value & 0xFF
    spd_h = (speed_value >> 8) & 0xFF

    # 書き込みパケット生成
    packet = [
        0xFF, 0xFF,           # header
        servo_id,              # ID
        0x05,                  # length
        0x03,                  # command = WRITE
        0x2E,                  # register address (speed)
        spd_l, spd_h           # data
    ]
    packet.append(checksum(packet[2:]))
    ser.write(bytearray(packet))

def read_register(ser, servo_id, address, size):
    packet = [
        0xFF, 0xFF,
        servo_id,
        0x04,       # length
        0x02,       # READ
        address,
        size
    ]
    packet.append(checksum(packet[2:]))

    ser.reset_input_buffer()   # ← 重要（ゴミ消す）
    ser.write(bytearray(packet))

    time.sleep(0.02)

    res = ser.read(20)  # 適当なサイズ
    print(f"ID {servo_id} response: {res.hex()}")
    return res

def main():
    with serial.Serial(PORT, BAUDRATE, timeout=0.1) as ser:
        print("Connected to STS3032 (speed mode).")
        try:
            while True:
                print("Forward 300 ...")
                write_speed(ser, 11, 300)
                write_speed(ser, 12, 300)
                read_register(ser, 11, 0x56, 2)
                read_register(ser, 12, 0x56, 2)
                time.sleep(3)

                print("Stop")
                write_speed(ser, 11, 0)
                write_speed(ser, 12, 0)
                read_register(ser, 11, 0x56, 2)
                read_register(ser, 12, 0x56, 2)
                time.sleep(2)

                print("Reverse 300 ...")
                write_speed(ser, 11, -300)
                write_speed(ser, 12, -300)
                read_register(ser, 11, 0x56, 2)
                read_register(ser, 12, 0x56, 2)
                time.sleep(3)

                print("Stop")
                write_speed(ser, 11, 0)
                write_speed(ser, 12, 0)
                read_register(ser, 11, 0x56, 2)
                read_register(ser, 12, 0x56, 2)
                time.sleep(2)


        except KeyboardInterrupt:
            print("\nStopping safely...")
            write_speed(ser, 11, 0)
            write_speed(ser, 12, 0)


if __name__ == "__main__":
    main()

