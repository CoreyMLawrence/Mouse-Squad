"""Minimal pure-python PNG read/write (no PIL available on this machine)."""
import zlib, struct

def read_png(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos = 8; idat = b''; w = h = 0; ct = bd = 0; plte = None; trns = None
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos+4])[0]; typ = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+ln]; pos += 12 + ln
        if typ == b'IHDR':
            w, h, bd, ct = struct.unpack('>IIBB', chunk[:10])
        elif typ == b'PLTE': plte = chunk
        elif typ == b'tRNS': trns = chunk
        elif typ == b'IDAT': idat += chunk
        elif typ == b'IEND': break
    assert bd == 8, bd
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(idat); stride = w * ch
    out = bytearray(h * stride); prev = bytearray(stride); p = 0
    for y in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        for x in range(stride):
            a = line[x-ch] if x >= ch else 0; b = prev[x]; c = prev[x-ch] if x >= ch else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + ((a + b) >> 1)) & 255
            elif f == 4:
                pp = a + b - c; pa = abs(pp-a); pb = abs(pp-b); pc = abs(pp-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        out[y*stride:(y+1)*stride] = line; prev = line
    px = []
    for y in range(h):
        row = []
        for x in range(w):
            o = y*stride + x*ch
            if ct == 2: row.append((out[o], out[o+1], out[o+2], 255))
            elif ct == 6: row.append(tuple(out[o:o+4]))
            elif ct == 0: row.append((out[o],)*3 + (255,))
            elif ct == 4: row.append((out[o],)*3 + (out[o+1],))
            elif ct == 3:
                i = out[o]; r, g, b = plte[i*3:i*3+3]
                a = trns[i] if trns and i < len(trns) else 255
                row.append((r, g, b, a))
        px.append(row)
    return w, h, px

def write_png(path, px):
    h = len(px); w = len(px[0])
    raw = bytearray()
    for row in px:
        raw.append(0)
        for p in row: raw += bytes(p if len(p) == 4 else tuple(p) + (255,))
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
                           + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b''))
