import os
import csv
import numpy as np
from pathlib import Path

def decoder(file_pattern):
    raw_data = f'../RAW_DATA/{file_pattern}'

    def decode_7bit_ascii(hex_string: str) -> bytes:
        if len(hex_string) % 2 != 0:
            hex_string = hex_string[:-1]
        
        ascii_bytes = bytes.fromhex(hex_string)
        bitbuf = 0
        n_bits = 0
        out = bytearray()

        for b in ascii_bytes:
            chunk = b & 0x7F
            bitbuf |= chunk << n_bits
            n_bits += 7
            while n_bits >= 8:
                out.append(bitbuf & 0xFF)
                bitbuf >>= 8
                n_bits -= 8
        return bytes(out)


    def parse_line(line: str) -> dict:
        parts = line.rstrip('\n').split(';')
        if len(parts) < 10: # here instead of originally 11
            raise ValueError("")
        parsed = {
            'time_sync': int(parts[1]),
            'avg_rate': float(parts[2]),
            'min_rate': float(parts[3]),
            'max_rate': float(parts[4]),
            'n_samples': int(parts[5]),
            'sensor_type': int(parts[6]),
            'max_g': float(parts[7]),
            'temperature': float(parts[8]),
            'payload_hex': parts[9],
            'crc_hex': parts[10] if len(parts)>10 else None,
        }
        return parsed


    # multiple file processing (ret)
    raw_data = Path(raw_data)
    csv_data = f'../CSV_DATA/{file_pattern}_csv/'
    csv_path = Path(csv_data)
    os.makedirs(csv_path, exist_ok=True)

    for file in raw_data.iterdir():

        with file.open('r', encoding='utf-8', errors='ignore') as fh:
            line_x = fh.readline()

        # read frequency from the raw data files (ret)
        fq = float(line_x.split(';')[2])
        dt = 1/fq

        pkt = parse_line(line_x)
        raw = decode_7bit_ascii(pkt['payload_hex'])

        # changes hexadecimal problem (Aebi Manuel)
        remainder = len(raw) % 4
        if remainder != 0:
            raw = raw[:-remainder]

        data = np.frombuffer(raw, dtype='<f4').tolist()

        n = len(data)
        time = [i*dt for i in range(n)]

        name = file.stem
        dst_file = csv_path / f"{name}.csv"

        with dst_file.open('w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Time [s]', 'Distance[mm]'])
            for t, value in zip(time, data):
                writer.writerow([t, value])

        print(f'{os.path.basename(dst_file)} successfully decoded with a frequency of {fq} Hz')

    print('All files successfully decoded')