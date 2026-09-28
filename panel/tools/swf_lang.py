"""Extrai os dados dos arquivos lang do Dofus (SWF com bytecode AS1/AS2) para JSON.

Uso: python swf_lang.py <arquivo.swf> <saida.json>
Interpreta apenas as instrucoes usadas pelos arquivos lang (push, objetos, arrays, set/get member).
"""
import json
import struct
import sys
import zlib


class Ref(dict):
    """Objeto AS2 (tambem usado para variaveis globais criadas implicitamente)."""


def run_actions(data, pos, end, env):
    stack = []
    pool = []

    def pop():
        return stack.pop() if stack else None

    while pos < end:
        code = data[pos]
        pos += 1
        if code == 0:
            break
        length = 0
        if code >= 0x80:
            length = struct.unpack_from('<H', data, pos)[0]
            pos += 2
        payload = data[pos:pos + length]
        pos += length

        if code == 0x88:  # ConstantPool
            count = struct.unpack_from('<H', payload, 0)[0]
            parts = payload[2:].split(b'\x00')
            pool = [dec(p) for p in parts[:count]]
        elif code == 0x96:  # Push
            i = 0
            while i < len(payload):
                t = payload[i]
                i += 1
                if t == 0:
                    j = payload.index(b'\x00', i)
                    stack.append(dec(payload[i:j]))
                    i = j + 1
                elif t == 1:
                    stack.append(struct.unpack_from('<f', payload, i)[0]); i += 4
                elif t in (2, 3):
                    stack.append(None)
                elif t == 4:
                    stack.append(None); i += 1
                elif t == 5:
                    stack.append(bool(payload[i])); i += 1
                elif t == 6:
                    hi, lo = struct.unpack_from('<II', payload, i)
                    stack.append(struct.unpack('<d', struct.pack('<II', lo, hi))[0]); i += 8
                elif t == 7:
                    stack.append(struct.unpack_from('<i', payload, i)[0]); i += 4
                elif t == 8:
                    stack.append(pool[payload[i]] if payload[i] < len(pool) else None); i += 1
                elif t == 9:
                    k = struct.unpack_from('<H', payload, i)[0]
                    stack.append(pool[k] if k < len(pool) else None); i += 2
                else:
                    break
        elif code == 0x1C:  # GetVariable
            name = pop()
            if name not in env:
                env[name] = Ref()
            stack.append(env[name])
        elif code == 0x1D:  # SetVariable
            value = pop(); name = pop()
            env[name] = value
        elif code == 0x4E:  # GetMember
            name = pop(); obj = pop()
            if isinstance(obj, dict):
                key = norm(name)
                if key not in obj:
                    obj[key] = Ref()
                stack.append(obj[key])
            elif isinstance(obj, list) and isinstance(name, (int, float)) and 0 <= int(name) < len(obj):
                stack.append(obj[int(name)])
            else:
                stack.append(None)
        elif code == 0x4F:  # SetMember
            value = pop(); name = pop(); obj = pop()
            if isinstance(obj, dict):
                obj[norm(name)] = value
            elif isinstance(obj, list) and isinstance(name, (int, float)):
                idx = int(name)
                while len(obj) <= idx:
                    obj.append(None)
                obj[idx] = value
        elif code == 0x43:  # InitObject
            n = int(pop() or 0)
            obj = Ref()
            for _ in range(n):
                value = pop(); name = pop()
                obj[norm(name)] = value
            stack.append(obj)
        elif code == 0x42:  # InitArray
            n = int(pop() or 0)
            stack.append([pop() for _ in range(n)])
        elif code == 0x40:  # NewObject
            name = pop(); n = int(pop() or 0)
            args = [pop() for _ in range(n)]
            stack.append([] if name == 'Array' and not args else Ref() if name != 'Array' else args)
        elif code in (0x52, 0x3D):  # CallMethod / CallFunction
            pop()
            if code == 0x52:
                pop()
            n = pop()
            for _ in range(int(n or 0) if isinstance(n, (int, float)) else 0):
                pop()
            stack.append(None)
        elif code == 0x17:  # Pop
            pop()
        elif code == 0x3C:  # DefineLocal
            value = pop(); name = pop()
            env[name] = value
        elif code == 0x41:  # DefineLocal2
            name = pop()
            env.setdefault(name, None)
        elif code == 0x4C:  # PushDuplicate
            if stack:
                stack.append(stack[-1])
        elif code == 0x4D:  # StackSwap
            if len(stack) >= 2:
                stack[-1], stack[-2] = stack[-2], stack[-1]
        elif code == 0x0B:  # Subtract
            b = pop(); a = pop()
            stack.append((a or 0) - (b or 0) if all(isinstance(x, (int, float)) for x in (a, b)) else None)
        elif code == 0x0A:  # Add
            b = pop(); a = pop()
            stack.append((a or 0) + (b or 0) if all(isinstance(x, (int, float)) for x in (a, b)) else None)
        elif code == 0x47:  # Add2
            b = pop(); a = pop()
            if isinstance(a, str) or isinstance(b, str):
                stack.append(f"{a}{b}")
            elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
                stack.append(a + b)
            else:
                stack.append(None)
        # outras instrucoes nao sao usadas pelos arquivos lang
    return pos


def dec(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('latin-1')


def norm(name):
    if isinstance(name, float) and name.is_integer():
        return int(name)
    return name


def parse_swf(path):
    raw = open(path, 'rb').read()
    body = zlib.decompress(raw[8:]) if raw[:3] == b'CWS' else raw[8:]
    nbits = body[0] >> 3
    pos = (5 + 4 * nbits + 7) // 8 + 4
    env = {}
    while pos < len(body):
        code_len = struct.unpack_from('<H', body, pos)[0]
        pos += 2
        code, length = code_len >> 6, code_len & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', body, pos)[0]
            pos += 4
        if code == 12:
            run_actions(body, pos, pos + length, env)
        elif code == 59:
            run_actions(body, pos + 2, pos + length, env)
        elif code == 0:
            break
        pos += length
    return env


def to_json(value):
    if isinstance(value, dict):
        return {str(k): to_json(v) for k, v in value.items() if k is not None}
    if isinstance(value, list):
        return [to_json(v) for v in value]
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


if __name__ == '__main__':
    env = parse_swf(sys.argv[1])
    env = {k: v for k, v in env.items() if k not in ('System', '_parent')}
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump(to_json(env), f, ensure_ascii=False)
