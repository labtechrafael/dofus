"""Desmontador minimo de ActionScript 2 (para investigar o cliente). Uso: python as2dis.py arquivo.swf texto_da_tag"""
import struct
import sys

import swf

NAMES = {0x04: 'NextFrame', 0x06: 'Play', 0x07: 'Stop', 0x0A: 'Add', 0x0B: 'Subtract', 0x0C: 'Multiply', 0x0D: 'Divide',
         0x0E: 'Equals', 0x0F: 'Less', 0x10: 'And', 0x11: 'Or', 0x12: 'Not', 0x17: 'Pop', 0x1C: 'GetVariable',
         0x1D: 'SetVariable', 0x3C: 'DefineLocal', 0x3D: 'CallFunction', 0x3E: 'Return', 0x3F: 'Modulo', 0x40: 'NewObject',
         0x41: 'DefineLocal2', 0x42: 'InitArray', 0x43: 'InitObject', 0x44: 'TypeOf', 0x47: 'Add2', 0x48: 'Less2',
         0x49: 'Equals2', 0x4A: 'ToNumber', 0x4B: 'ToString', 0x4C: 'PushDuplicate', 0x4D: 'StackSwap', 0x4E: 'GetMember',
         0x4F: 'SetMember', 0x50: 'Increment', 0x51: 'Decrement', 0x52: 'CallMethod', 0x53: 'NewMethod', 0x54: 'InstanceOf',
         0x55: 'Enumerate2', 0x66: 'StrictEquals', 0x67: 'Greater', 0x87: 'StoreRegister', 0x88: 'ConstantPool',
         0x8E: 'DefineFunction2', 0x94: 'With', 0x96: 'Push', 0x99: 'Jump', 0x9B: 'DefineFunction', 0x9D: 'If', 0x9E: 'Call',
         0x9F: 'GotoFrame2', 0x2B: 'CastOp', 0x2C: 'ImplementsOp', 0x69: 'Extends', 0x46: 'Enumerate', 0x3A: 'Delete',
         0x3B: 'Delete2', 0x26: 'Trace', 0x34: 'GetTime', 0x30: 'RandomNumber'}


def disasm(data, pos=0, end=None, out=None, pool=None):
    end = len(data) if end is None else end
    out = [] if out is None else out
    pool = [] if pool is None else pool
    while pos < end:
        at = pos
        code = data[pos]
        pos += 1
        if code == 0:
            out.append((at, 'End', ''))
            continue
        ln = 0
        if code >= 0x80:
            ln = struct.unpack_from('<H', data, pos)[0]
            pos += 2
        pl = data[pos:pos + ln]
        pos += ln
        name = NAMES.get(code, hex(code))
        arg = ''
        if code == 0x88:
            n = struct.unpack_from('<H', pl, 0)[0]
            pool[:] = [p.decode('latin1') for p in pl[2:].split(b'\0')[:n]]
            arg = f'{n} strings'
        elif code == 0x96:
            vals, i = [], 0
            while i < len(pl):
                t = pl[i]; i += 1
                if t == 0:
                    j = pl.index(b'\0', i); vals.append(repr(pl[i:j].decode('latin1'))); i = j + 1
                elif t == 1: vals.append(str(struct.unpack_from('<f', pl, i)[0])); i += 4
                elif t in (2, 3): vals.append('null' if t == 2 else 'undef')
                elif t == 4: vals.append(f'r{pl[i]}'); i += 1
                elif t == 5: vals.append(str(bool(pl[i]))); i += 1
                elif t == 6:
                    hi, lo = struct.unpack_from('<II', pl, i); vals.append(str(struct.unpack('<d', struct.pack('<II', lo, hi))[0])); i += 8
                elif t == 7: vals.append(str(struct.unpack_from('<i', pl, i)[0])); i += 4
                elif t == 8: vals.append(repr(pool[pl[i]]) if pl[i] < len(pool) else '?'); i += 1
                elif t == 9:
                    k = struct.unpack_from('<H', pl, i)[0]; vals.append(repr(pool[k]) if k < len(pool) else '?'); i += 2
                else: break
            arg = ', '.join(vals)
        elif code in (0x99, 0x9D):
            arg = str(struct.unpack_from('<h', pl, 0)[0])
        elif code in (0x9B, 0x8E):
            nm_end = pl.index(b'\0')
            fname = pl[:nm_end].decode('latin1')
            if code == 0x9B:
                npar = struct.unpack_from('<H', pl, nm_end + 1)[0]
                p = nm_end + 3
                for _ in range(npar):
                    p = pl.index(b'\0', p) + 1
                size = struct.unpack_from('<H', pl, p)[0]
            else:
                p = nm_end + 1
                npar, nreg, flags = struct.unpack_from('<HBH', pl, p)
                p += 5
                params = []
                for _ in range(npar):
                    reg = pl[p]; p += 1
                    e = pl.index(b'\0', p); params.append(f'r{reg}:{pl[p:e].decode("latin1")}'); p = e + 1
                size = struct.unpack_from('<H', pl, p)[0]
                fname += '(' + ','.join(params) + ')'
            arg = f'{fname} size={size}'
            out.append((at, name, arg))
            disasm(data, pos, pos + size, out, pool)
            pos += size
            out.append((pos, 'EndFunction', fname))
            continue
        elif code == 0x87:
            arg = f'r{pl[0]}'
        out.append((at, name, arg))
    return out


if __name__ == '__main__':
    s = swf.read_swf(sys.argv[1])
    needle = sys.argv[2].encode()
    for i, (c, d) in enumerate(s.tags):
        if c in (12, 59) and needle in d:
            off = 2 if c == 59 else 0
            print(f'### tag {i} code {c} len {len(d)}')
            for at, name, arg in disasm(d, off):
                print(f'{at:7d} {name:14s} {arg}')
