b = bytearray()
a = 0x6523
b.append(a & 0xff)
b.append(a >> 8)
print(b.hex())