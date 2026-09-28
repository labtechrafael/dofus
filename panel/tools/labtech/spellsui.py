"""Patch do cliente: filtro "Tipo de feitiço" com as 12 racas na janela de feitiços.

A classe da janela (dofus.graphics.gapi.ui.Spells, no loader.swf) e ofuscada, entao em vez de editar o codigo
dela o patch roda depois (DoAction no core.swf) e embrulha dois pontos:
  - o metodo que monta a lista (\x1a\x06\x16): na primeira vez acrescenta as 12 racas no combo; quando o filtro
    escolhido e uma raca (tipo 101..112), monta a lista completa e deixa so os feiticos daquela classe;
  - nada mais: o combo ja grava o "type" do item escolhido no filtro (\x17\x1e\t) e chama o metodo acima.
O AS2 e compilado pelo JPEXS (ffdec-cli -replace) a partir de um SWF modelo.
"""
import json
import os
import subprocess
import tempfile

import swf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
FFDEC = os.path.join(ROOT, 'runtime', 'ffdec', 'ffdec-cli.jar')
JAVA = os.path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe')
CLASS_SPELLS = os.path.join(ROOT, 'panel', 'data', 'class-spells.json')
NAMES = ['Feca', 'Osamodas', 'Enutrof', 'Sram', 'Xelor', 'Ecaflip', 'Eniripsa', 'Iop', 'Cra', 'Sadida', 'Sacrier', 'Pandawa']
MARKER = '__ltSpellsRaca'


def _chars(name):
    """Nome ofuscado -> expressao AS2 (String.fromCharCode), sem depender de escapes no compilador."""
    return 'String.fromCharCode(' + ','.join(str(ord(c)) for c in name) + ')'


def source():
    spells = json.load(open(CLASS_SPELLS, encoding='utf-8'))
    rows = []
    for i in range(12):
        rows.append('[' + ','.join(str(s) for s in spells[str(i + 1)]) + ']')
    labels = ','.join(f'"{n}"' for n in NAMES)
    return f'''
_global.{MARKER} = true;
_global.__ltRacaSpells = [{",".join(rows)}];
_global.__ltRacaNomes = [{labels}];
var P = _global.dofus[{_chars(chr(0x1d) + chr(0x19) + chr(0x10))}].gapi.ui.Spells.prototype;
var KR = {_chars(chr(0x1a) + chr(0x06) + chr(0x16))};
if (P.__ltRefresh == undefined) {{
    P.__ltRefresh = P[KR];
    P[KR] = function() {{
        var KF = {_chars(chr(0x17) + chr(0x1e) + chr(0x09))};
        var KC = {_chars(chr(0x19) + chr(0x10) + chr(0x02))};
        var KL = {_chars(chr(0x19) + chr(0x0e) + chr(0x09))};
        var cb = this[KC];
        var cdp = cb.dataProvider;
        if (cdp != undefined && cdp.__ltRacas != true) {{
            cdp.__ltRacas = true;
            var i = 0;
            while (i < 12) {{
                cdp.push({{label: "Ra" + String.fromCharCode(231) + "a: " + _global.__ltRacaNomes[i], type: 101 + i}});
                i++;
            }}
            var sel = cb.selectedIndex;
            cb.dataProvider = cdp;
            cb.selectedIndex = sel;
        }}
        var f = this[KF];
        if (f > 100 && f < 113) {{
            this[KF] = -2;
            this.__ltRefresh.apply(this, arguments);
            this[KF] = f;
            var lst = _global.__ltRacaSpells[f - 101];
            var ok = new Object();
            var k = 0;
            while (k < lst.length) {{
                ok[String(lst[k])] = 1;
                k++;
            }}
            var dp = this[KL].dataProvider;
            var j = dp.length - 1;
            while (j >= 0) {{
                if (ok[String(dp[j].ID)] != 1) {{
                    dp.splice(j, 1);
                }}
                j--;
            }}
            this[KL].dataProvider = dp;
        }} else {{
            this.__ltRefresh.apply(this, arguments);
        }}
    }};
}}
'''


def weapon_source():
    """Manopla sempre visivel: no Dofus Retro a arma (acessorio 0) so e encaixada nas animacoes de ataque.
    Quando o sprite encaixa o escudo (acessorio 4, a Caneca) e a arma e a Manopla (7_3001/7_3002), encaixa tambem a
    arma num clipe irmao espelhado (a outra mao), que acompanha o ponto de encaixe a cada quadro."""
    cls = f'_global[{_chars(chr(0x19) + chr(0x04))}].battlefield[{_chars(chr(0x1d) + chr(0x1a) + chr(0x02))}]'
    return f'''
var G = {cls}.prototype;
if (G.__ltApplyAcc == undefined && G.applyAccessory != undefined) {{
    G.__ltApplyAcc = G.applyAccessory;
    G.applyAccessory = function(mc, idx, lbl) {{
        var r = this.__ltApplyAcc.apply(this, arguments);
        if (idx == 4 && mc != undefined) {{
            var data = this.getSpriteData(mc);
            var arma = data.accessories[0];
            var g = String(arma.gfx);
            if (g == "7_3001" || g == "7_3002") {{
                var p = mc._parent;
                var nome = "__ltArme_" + mc._name;
                p[nome].removeMovieClip();
                var w = p.createEmptyMovieClip(nome, p.getNextHighestDepth());
                w._x = -mc._x;
                w._y = mc._y;
                w.__ph = mc;
                w.onEnterFrame = function() {{
                    if (this.__ph._parent == undefined) {{
                        this.removeMovieClip();
                        return;
                    }}
                    this._x = -this.__ph._x;
                    this._y = this.__ph._y;
                }};
                this.__ltApplyAcc.apply(this, [w, 0, lbl]);
            }}
        }}
        return r;
    }};
}}
'''


def compile_as2(src):
    """Compila AS2 com o JPEXS e devolve os bytes da DoAction."""
    tmp = tempfile.mkdtemp(prefix='lt_as2_')
    tpl, out, as_file = (os.path.join(tmp, n) for n in ('tpl.swf', 'out.swf', 'code.as'))
    a = swf.ActionBuilder()
    a.push('__ltTpl', 1).set_variable()
    swf.write_swf(swf.Swf(b'FWS', 8, swf.rect(0, 100, 0, 100), 25 << 8, 1, [(12, a.bytes()), (1, b''), (0, b'')]),
                  tpl, compress=False)
    with open(as_file, 'w', encoding='utf-8') as f:
        f.write(src)
    r = subprocess.run([JAVA, '-jar', FFDEC, '-replace', tpl, out, '\\frame_1\\DoAction', as_file],
                       capture_output=True, timeout=600)
    if not os.path.exists(out):
        raise RuntimeError('JPEXS nao compilou o patch: ' + r.stdout.decode('utf-8', 'replace') + r.stderr.decode('utf-8', 'replace'))
    s = swf.read_swf(out)
    return next(d for c, d in s.tags if c == 12)


def patch_code():
    return compile_as2(source())   # weapon_source() desligado: a manopla faz parte do corpo (remodel.add_gauntlet)
