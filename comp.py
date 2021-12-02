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
                cmd_one = False
                des.append(0xfe)
                des.append(run_len & 0xff)
                des.append(run_len >> 8)
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
            if cmd_one and src[cmd_one_p] < 0xBF:
                cmd_one_p += 1
                des.append(src[p])
                p += 1
            else:
                cmd_one_p = p
                des.append(0x81)
                des.append(src[p])
                p += 1
                cmd_one = True
        else:
            rel_off = len(des) - off_sp
            # command 5
            if block_size > 0xa or rel_off > 0xffff:
                if block_size > 0x40:
                    des.append(0xff)
                    des.append(run_len & 0xff)
                    des.append(run_len >> 8)
                else:
                    des.append(block_size-3 | 0xc0)

                offset = rel_off if rel else off_sp
            else:
                # command 2
                offset = rel_off << 8 | (16 * (block_size - 3) + (rel_off >> 8))
            des.append(offset & 0xff)
            des.append(offset >> 8)
            p += block_size
            cmd_one = False
    des.append(0x80)
    return des



def main():
    b = b'\xff\xff\xff\xff\xff\xff\xff\xff'
    c = encode(b)
    print(c.hex())

if __name__ == '__main__':
    main()