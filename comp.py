import io



def encode(src) -> bytearray:
    des = bytearray()
    size = len(src)
    p = 0   # src pointer
    
    if size == 0:
        return des
    rel = True if size > (1<<16) else False
    if rel:
        des.append(0)
    cmd_one = True
    cmd_one_p = 0
    des.append(0x81)
    des.append(src[p])
    p += 1

    while p < size:
        # command 4?
        
        if size-p > 64 and src[p] == src[p+64]:
            rle_max = min(size, p+0xffff)
            for rle_p in range(p,rle_max):
                if src[p] != src[rle_p]:
                    break
            run_len = rle_p - p
            if run_len >= 0x41:
                #print('c4')
                cmd_one = False
                des.append(0xfe)
                des.append(run_len & 0xff)
                des.append(run_len >> 8 & 0xff)
                des.append(src[p])
                p = rle_p
                continue

        block_size = 0
        
        if rel:
            off_s = max(0,p-0xffff)
        else:
            off_s = 0

        off_p = off_s
        while off_p < p:
            while off_p < p and src[off_p] != src[p]:
                off_p += 1
            if off_p >= p:
                break
            i = 1
            while p + i < size:
                if src[off_p+i] != src[p+i]:
                    break
                i += 1
                
            if i>= block_size:
                
                block_size = i
                off_sp = off_p
            off_p += 1
        
        if block_size <= 2:
            # command 1
            
            if cmd_one and des[cmd_one_p] < 0xBF:
                des[cmd_one_p] += 1
                des.append(src[p])
                p += 1
                #print('c1add')
            else:
                #print('c1')
                cmd_one_p = len(des)
                des.append(0x81)
                des.append(src[p])
                p += 1
                cmd_one = True
        else:
            rel_off = p - off_sp
            # command 5
            if block_size > 0xa or rel_off > 0xfff:
                if block_size > 0x40:
                    #print('c5')
                    des.append(0xff)
                    des.append(block_size & 0xff)
                    des.append(block_size >> 8 & 0xff)
                else:
                    # command 3
                    #print('c3')
                    des.append(block_size-3 | 0xc0)

                offset = rel_off if rel else off_sp
            else:
                # command 2
                offset = (rel_off << 8) | (16 * (block_size - 3) + (rel_off >> 8))
                #print('c2')
            des.append(offset & 0xff)
            des.append(offset >> 8 & 0xff)
            p += block_size
            cmd_one = False
    des.append(0x80)
    return des



def main():
    import base64
    with open('b','rb') as infile, open('c.txt','w') as outfile:
        des = bytearray()
        for i in range(32):
            src = infile.read(8192)
            sec = encode(src)
            print(len(sec))
            des.append(len(sec) & 0xff)
            des.append(len(sec) >> 8)
            des.append(8192 & 0xff)
            des.append(8192 >> 8)
            des += sec
            if i == 4:
                print(sec.hex())
            print(i, 'done')
        b64e = base64.b64encode(des).decode()
        k = 0
        outfile.write('[OverlayPack]\n')
        while k*71 < len(b64e):
            outfile.write(f'{k+1}={b64e[k*71:(k+1)*71]}\n')
            k += 1
        
        


if __name__ == '__main__':
    main()