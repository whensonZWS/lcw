import configparser as cfp
import base64
import io

map_name = ''
f = cfp.ConfigParser(strict=False)
f.optionxform=str
f.read(map_name)

raw = ''
for s in f['OverlayPack']:
    raw += f['OverlayPack'][s]
src = io.BytesIO(base64.b64decode(raw))

# print(src.read().hex())
# print(src.tell())
# src.seek(0)
        
        

#print(src.read().hex())

def copy(des: bytearray, src_index: int, count: int):
    #print(f'{src_index=}')
    for i in range(count):
        des.append(des[src_index + i])

def consume(src: io.BytesIO) -> bytearray:
    des = bytearray()
    com = src.read(1)
    dp = 0
    while True:

        com = com[0]
        if com < 0xc0 and com > 0x7f:   
            # command 1

            count = com & 0x3f

            if count == 0:
                break

            for i in range(count):
                des += src.read(1)
                dp += 1
        elif com < 0x80:
            # command 2
            count = (com >> 4) + 3
            pos = ((com & 0x0f) << 8) + src.read(1)[0]
            copy(des,dp-pos,count)
            dp += count
            
        elif com < 0xfe:
            # command 3
            count = (com & 0x3f) + 3
            pos = int.from_bytes(src.read(2), byteorder = 'little')
            copy(des,pos,count)
            dp += count
        elif com == 0xfe:
            # command 4
            count = int.from_bytes(src.read(2), byteorder = 'little')
            b = src.read(1)
            for i in range(count):
                des += b
            dp += count
        
        else:
            # command 5
            count = int.from_bytes(src.read(2), byteorder = 'little')
            pos = int.from_bytes(src.read(2), byteorder = 'little')
            # print(f'{count=},{pos=}')
            copy(des,pos,count)
            dp += count
        
        com = src.read(1)
        

    return des

f = bytearray()
for i in range(32):
    src.read(4)
    p = consume(src)
    f += p


with open('ol.txt','wb') as output:
    output.write(f)




