import serial
import time
import struct

# --- 通信設定 ---
# お使いの環境に合わせてCOMポート名を変更してください (例: Windows: 'COM3', Linux: '/dev/ttyUSB0')
SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 1000000 # STS/SCSシリーズのデフォルト通信速度
SERVO_ID = 21 # 制御したいサーボのID

# --- コマンド定数 ---
# コマンド長: 9バイト (Instruction:1 + Address:1 + Position:2 + Time:2 + Speed:2)
# FEETECHプロトコルではInstructionとAddressもLengthに含めるためLengthは8ではなく9
PACKET_LENGTH = 0x09
INSTRUCTION_WRITE_DATA = 0x03
ADDR_GOAL_POSITION = 0x2A # 目標位置 (Goal Position) のレジスタアドレス

def calculate_checksum(data_bytes):
    """
    FEETECHサーボのチェックサムを計算する
    チェックサムは (ID + Length + Instruction + Parameters...) の合計値の
    下位1バイトのビット反転 (NOT) です。
    """
    # Sum: IDから最後のデータバイトまでの合計
    servo_sum = sum(data_bytes)
    # 下位8ビット (mod 256)
    low_byte_sum = servo_sum & 0xFF
    # ビット反転 (NOT)
    checksum = (~low_byte_sum) & 0xFF
    return checksum

def make_move_packet(servo_id, position, speed, time_ms=0):
    """
    サーボを特定の目標位置に移動させるためのパケットを生成する
    Position, Time, Speedはそれぞれ2バイトのLittle Endian (下位バイト -> 上位バイト) です。
    """
    # Goal Position (0-4095)
    pos_low = position & 0xFF
    pos_high = (position >> 8) & 0xFF

    # Goal Time (0-数千 ms)
    time_low = time_ms & 0xFF
    time_high = (time_ms >> 8) & 0xFF
    
    # Goal Speed (0-1023) 
    # STS3032の場合、速度は1000単位で設定することが推奨される
    # speed_low = speed & 0xFF
    # speed_high = (speed >> 8) & 0xFF
    
    # マニュアルの例に合わせ、Goal Position (2A) から6バイト連続で送信
    # 2A:Goal_Position_L, 2B:Goal_Position_H, 2C:Goal_Time_L, 2D:Goal_Time_H, 2E:Goal_Speed_L, 2F:Goal_Speed_H
    
    # 今回はTimeを使わずSpeedで動作時間を制御するため、Timeを0に、Speedを任意の値に設定
    data_bytes = [
        INSTRUCTION_WRITE_DATA, # Instruction (0x03)
        ADDR_GOAL_POSITION,     # Address (0x2A)
        pos_low,                # Position Low Byte
        pos_high,               # Position High Byte
        time_low,               # Time Low Byte (0x00)
        time_high,              # Time High Byte (0x00)
        speed & 0xFF,           # Speed Low Byte
        (speed >> 8) & 0xFF     # Speed High Byte
    ]
    
    # チェックサムの対象となるバイト列
    checksum_data = [
        servo_id,
        PACKET_LENGTH,
    ] + data_bytes
    
    checksum = calculate_checksum(checksum_data)

    # パケットの組み立て: Header(2) + ID(1) + Length(1) + Data(9) + Checksum(1) = 14 bytes
    packet = [
        0xFF, 0xFF,             # Header
        servo_id,               # ID
        PACKET_LENGTH,          # Length
    ] + data_bytes + [checksum]

    return bytes(packet)

def move_servo(ser, servo_id, position, speed):
    """サーボを指定位置に移動させる"""
    if not (0 <= position <= 4095):
        print(f"Error: Position {position} is out of range (0-4095).")
        return

    packet = make_move_packet(servo_id, position, speed)
    print(f"Sending packet: {packet.hex().upper()}")
    ser.write(packet)
    time.sleep(0.01) # サーボが応答するのを待つ


def torque_enable(ser, servo_id=1, enable=True):
    val = 1 if enable else 0
    packet = [
        0xFF, 0xFF,
        servo_id,
        0x04,       # データ長
        0x03,       # Write
        0x28,       # トルクスイッチのアドレス
        val
    ]
    chksum = (~sum(packet[2:]) & 0xFF)
    packet.append(chksum)

    ser.write(bytearray(packet))


# --- メイン処理 ---
if __name__ == '__main__':
    try:
        # シリアルポートを開く (pyserialを使用)
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            timeout=0.1,  # タイムアウト設定
            write_timeout=0.1
        )

        # torque_enable(ser, SERVO_ID, False)
        # time.sleep(2.0)
        # torque_enable(ser, SERVO_ID, True)
        # time.sleep(2.0)

        print(f"Serial port {SERIAL_PORT} opened successfully at {BAUD_RATE} bps.")

        # --- 制御の実行 ---

        # 1. 初期位置 (例えば、0度 / Position 0) に移動
        # (Position 0, Speed 500)
        print("Moving to initial position (0 degrees / Position 0)...")
        move_servo(ser, 21, 2048, 1024)
        time.sleep(1)
        move_servo(ser, 11, 0, 1500)
        move_servo(ser, 12, 0, 1500)
        time.sleep(5) # 動作完了を待つ

        # # 2. 中間位置 (例えば、180度 / Position 2048) に移動
        # # (Position 2048, Speed 1000)
        # print("Moving to 180 degrees (Position 2048)...")
        # move_servo(ser, SERVO_ID, 2048, 1000)
        # time.sleep(10)

        # 3. 終了位置 (例えば、360度 / Position 4095) に移動
        # (Position 4095, Speed 500)
        print("Moving to 360 degrees (Position 4095)...")
        # move_servo(ser, SERVO_ID, 1024, 512)
        move_servo(ser, 11, 0, 0)
        move_servo(ser, 12, 0, 0)
        time.sleep(10)

        print("Position control sequence finished.")

    except serial.SerialException as e:
        print(f"Serial Error: {e}")
        print("Please check the port name, connection, and power supply.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")