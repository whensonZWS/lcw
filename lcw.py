
import io



def copy(des: bytearray, src_index: int, count: int):
    print(f'{src_index=},{count=}')
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
            print(f'c1,{count=},{com=}')

            if count == 0:
                break

            for i in range(count):
                des += src.read(1)
                dp += 1
        elif com < 0x80:
            # command 2, com start with 0
            count = (com >> 4) + 3
            pos = ((com & 0x0f) << 8) + src.read(1)[0]
            print(f'c2,{count=},{com=},{pos=}')
            copy(des,dp-pos,count)
            dp += count
            
        elif com < 0xfe:
            # command 3, com start with 11
            count = (com & 0x3f) + 3
            pos = int.from_bytes(src.read(2), byteorder = 'little')
            print(f'c3,{count=},{com=},{pos=}')
            if rel:
                copy(des,dp-pos,count)
            else:
                copy(des,pos,count)
            dp += count
        elif com == 0xfe:
            # command 4, com=0xfe, count: int16, b: one byte of content
            count = int.from_bytes(src.read(2), byteorder = 'little')
            print(f'c4,{count=},{com=}')
            b = src.read(1)
            for i in range(count):
                des += b
            dp += count
        
        else:
            # command 5, com=0xff, count: int16, pos: int16
            count = int.from_bytes(src.read(2), byteorder = 'little')
            pos = int.from_bytes(src.read(2), byteorder = 'little')
            print(f'c5,{count=},{com=},{pos=}')
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
    map_name = 'C:/Users/whenson/Documents/Tencent Files/1156535822/FileRecv/srech-left.map'
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
    import base64
    with open('c','r') as infile:
        raw = infile.read()
    src = io.BytesIO(base64.b64decode(raw))
    src.read()
    size = src.tell()
    src.seek(0)
    # build up
    f = bytearray()
    c = 0
    while src.tell() < size:
        src.read(4)
        f += decode(src)
        print('c',c)
        c += 1

    with open('d','wb') as output:
        output.write(f)

def main3():
    src = io.BytesIO(bytearray.fromhex('81fffeaa0aff811efefc01ff821e1efffd01ab0afffe01aa0aff0e029b0eff0a02a80efee801ffc8a90cfff701a90c811efff801b212ff0002a80cff6003b21280'))
    print(decode(src))

if __name__ == '__main__':
    main()