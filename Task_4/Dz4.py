import csv


def assemble(input_file, output_file, log_file):
    try:
        with open(input_file, 'r') as src, open(output_file, 'wb') as out, open(log_file, 'w', newline='') as log:
            writer = csv.writer(log)
            writer.writerow(["Instruction", "A", "B", "C", "D"])
            for line in src:
                if not line.strip():
                    continue
                parts = line.strip().split()
                opcode = parts[0]
                if opcode == "LOAD_CONST":
                    a = 2
                    b = int(parts[1])
                    c = int(parts[2])
                    if b > 2047 or c > 262143:
                        raise ValueError(f"Значение для b или c слишком большое: b={b}, c={c}")
                    encoded = (a << 49) | (b << 38) | (c << 12)
                    if encoded >= (1 << 56):
                        raise ValueError(f"Значение для LOAD_CONST слишком большое: {encoded}")
                    out.write(encoded.to_bytes(7, byteorder='big'))
                    writer.writerow(["LOAD_CONST", a, b, c])
                elif opcode == "SHIFT_RIGHT":
                    a = 15
                    b = int(parts[1])
                    c = int(parts[2])
                    d = int(parts[3])
                    if b > 2047 or c > 262143 or d > 262143:
                        raise ValueError(f"Значение для b, c или d слишком большое: b={b}, c={c}, d={d}")
                    encoded = (a << 49) | (b << 38) | (c << 12) | d
                    if encoded >= (1 << 56):
                        raise ValueError(f"Значение для SHIFT_RIGHT слишком большое: {encoded}")
                    out.write(encoded.to_bytes(7, byteorder='big'))
                    writer.writerow(["SHIFT_RIGHT", a, b, c, d])
                elif opcode == "LOAD_MEMORY":
                    a = 14
                    b = int(parts[1])
                    c = int(parts[2])
                    if b > 2047 or c > 262143:
                        raise ValueError(f"Значение для b или c слишком большое: b={b}, c={c}")
                    encoded = (a << 49) | (b << 38) | (c << 12)
                    if encoded >= (1 << 56):
                        raise ValueError(f"Значение для LOAD_MEMORY слишком большое: {encoded}")
                    out.write(encoded.to_bytes(7, byteorder='big'))
                    writer.writerow(["LOAD_MEMORY", a, b, c])
                elif opcode == "STORE_MEMORY":
                    a = 10
                    b = int(parts[1])
                    c = int(parts[2])
                    d = int(parts[3])
                    if b > 2047 or c > 262143 or d > 262143:
                        raise ValueError(f"Значение для b, c или d слишком большое: b={b}, c={c}, d={d}")
                    encoded = (a << 49) | (b << 38) | (c << 12) | d
                    if encoded >= (1 << 56):
                        raise ValueError(f"Значение для STORE_MEMORY слишком большое: {encoded}")
                    out.write(encoded.to_bytes(7, byteorder='big'))
                    writer.writerow(["STORE_MEMORY", a, b, c, d])
                elif opcode == "SHIFT_LEFT":
                    a = 16
                    b = int(parts[1])
                    c = int(parts[2])
                    d = int(parts[3])
                    if b > 2047 or c > 262143 or d > 262143:
                        raise ValueError(f"Значение для b, c или d слишком большое: b={b}, c={c}, d={d}")
                    encoded = (a << 49) | (b << 38) | (c << 12) | d
                    if encoded >= (1 << 56):
                        raise ValueError(f"Значение для SHIFT_LEFT слишком большое: {encoded}")
                    out.write(encoded.to_bytes(7, byteorder='big'))
                    writer.writerow(["SHIFT_LEFT", a, b, c, d])
        print(f"Файлы {output_file} и {log_file} успешно созданы.")
    except Exception as e:
        print(f"Ошибка при создании файлов: {e}")


def interpret(binary_file, result_file, mem_start, mem_end):
    try:
        memory = [0] * mem_end
        with open(binary_file, 'rb') as bin_file:
            while True:
                byte = bin_file.read(7)
                if not byte:
                    break
                instruction = int.from_bytes(byte, byteorder='big')
                a = (instruction >> 49) & 0xF
                b = (instruction >> 38) & 0x7FF
                c = (instruction >> 12) & 0x7FFFF
                d = instruction & 0xFFF

                if a == 2:
                    memory[b] = c
                elif a == 15:
                    memory[b] = memory[c] >> memory[d]
                elif a == 14:
                    memory[b] = memory[c]
                elif a == 10:
                    memory[b] = memory[c] + memory[d]
                elif a == 16:
                    memory[b] = memory[c] << memory[d]

        with open(result_file, 'w', newline='') as result:
            writer = csv.writer(result)
            writer.writerow(["Address", "Value"])
            for i in range(mem_start, mem_end):
                writer.writerow([i, memory[i]])
        print(f"Результаты сохранены в файл {result_file}.")
    except Exception as e:
        print(f"Ошибка при интерпретации бинарного файла: {e}")


if __name__ == "__main__":
    assemble('programm.txt', 'program.bin', 'log.csv')
    interpret('program.bin', 'result.csv', 0, 16)
