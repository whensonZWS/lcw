
import io



def copy(des: bytearray, src_index: int, count: int):
    for i in range(count):   
        des.append(des[src_index + i])

def decode(src: io.BytesIO) -> bytearray:
    des = bytearray()
    com = src.read(1)
    dp = 0
    rel = False
    if com != b'' and com[0] == 0:
        rel = True
        com = src.read(1)

    while com != b'':
        com = com[0]
        if com < 0xc0 and com > 0x7f:   
            # command 1, com start with 10

            count = com & 0x3f

            if count == 0:
                break

            for i in range(count):
                des += src.read(1)
                dp += 1
        elif com < 0x80:
            # command 2, com start with 0
            count = (com >> 4) + 3
            pos = ((com & 0x0f) << 8) + src.read(1)[0]
            print(f'{count=},{com=}')
            copy(des,dp-pos,count)
            dp += count
            
        elif com < 0xfe:
            # command 3, com start with 11
            count = (com & 0x3f) + 3
            pos = int.from_bytes(src.read(2), byteorder = 'little')
            if rel:
                copy(des,dp-pos,count)
            else:
                copy(des,pos,count)
            dp += count
        elif com == 0xfe:
            # command 4, com=0xfe, count: int16, b: one byte of content
            count = int.from_bytes(src.read(2), byteorder = 'little')
            b = src.read(1)
            for i in range(count):
                des += b
            dp += count
        
        else:
            # command 5, com=0xff, count: int16, pos: int16
            count = int.from_bytes(src.read(2), byteorder = 'little')
            pos = int.from_bytes(src.read(2), byteorder = 'little')
            if rel:
                copy(des,dp-pos,count)
            else:
                copy(des,pos,count)
            dp += count
        
        com = src.read(1)   

    return des

def main():
    # example code
    import configparser as cfp
    import base64
    map_name = './random-map.map'
    f = cfp.ConfigParser(strict=False)
    f.optionxform=str
    f.read(map_name)
    # read all the overlaypack section of an ini file into raw and convert it into a byte stream
    raw = ''
    for s in f['OverlayPack']:
        raw += f['OverlayPack'][s]
    src = io.BytesIO(base64.b64decode(raw))
    # get length of byte stream
    src.read()
    size = src.tell()
    src.seek(0)
    # build up
    f = bytearray()
    while src.tell() < size:
        src.read(4)
        f += decode(src)

    with open('b','wb') as output:
        output.write(f)

def main2():
    s = io.BytesIO(bytes.fromhex('81ff400280'))
    print(decode(s))

if __name__ == '__main__':
    main2()