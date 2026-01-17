import serial
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 1000000
SERVO_ID = 11

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

def main():
    with serial.Serial(PORT, BAUDRATE, timeout=0.1) as ser:
        print("Connected to STS3032 (speed mode).")
        try:
            while True:
                print("Forward 300 ...")
                write_speed(ser, SERVO_ID, 300)
                time.sleep(3)

                print("Stop")
                write_speed(ser, SERVO_ID, 0)
                time.sleep(2)

                print("Reverse 300 ...")
                write_speed(ser, SERVO_ID, -300)
                time.sleep(3)

                print("Stop")
                write_speed(ser, SERVO_ID, 0)
                time.sleep(2)


        except KeyboardInterrupt:
            print("\nStopping safely...")
            write_speed(ser, SERVO_ID, 0)


if __name__ == "__main__":
    main()

