#!/usr/bin/env python3
"""Simbolos da biblioteca do EasyEDA para o esquema.

Cada simbolo fica em esquema/lib/<CHAVE>.json e a geracao funciona offline a partir
deles. Duas origens, gravadas uma vez:
  UUID  - pecas LCSC (folha 1, todas THT) e o Arduino da biblioteca de usuarios: resposta
          da API https://easyeda.com/api/components/<uuid> (a mesma que o editor usa);
  COMUM - itens do painel "Commons Library" do editor (folha 3): nao passam pela API,
          estao embutidos no JS do editor (main.min.js) e sao extraidos de la.

Uso:  python3 biblioteca.py          # baixa os que faltam e resume cada simbolo
"""
import json
import re
import subprocess
from pathlib import Path

LIB = Path(__file__).parent / "lib"

# chave -> uuid do simbolo na biblioteca LCSC (peca THT escolhida)
UUID = {
    "74HC04": "34b42f4df2b2c49cfe01b6f1cdae8848",    # SN74HC04N, DIP-14, C2886
    "74HC32": "b98d8e481d835f0e8f56eb3e0ccb6b3a",    # SN74HC32N, DIP-14, C2894
    "74HC86": "a86c57e1686dd0bcdd0ac30bd6bf73ed",    # SN74HC86N, DIP-14, C2903
    "74HC08": "9a2c7d591b95426a9a360816378b1294",    # 74HC08N, PDIP-14, C5116331
    "74HC283": "541620bc65074420a05a9a7dce2cbb6c",   # CD74HC283E, DIP-16, C139343
    "POT10K": "dfe9f709254442e08fb1cc3eb4590aa4",    # 3386P-1-103, trimpot 10k, C48601064
    "BOTAO": "90fee438319e78e9ced66382aecd6854",     # tatil 6x6 4 pinos, C71843
    "R2K2": "7c90527be68e4f25ae2e703f0d232813",      # CF1/4W 2,2k 5%, C120063
    "R10K": "933873c4b334423ea706d460a2e43c8e",      # MF1/4W 10k 5%, C2903233
    "C100N": "b631514c5dc04a749b0f8ea3b195a955",     # ceramico 100 nF 50 V, passo 2,54, C254089
    "LED_VM": "e608bc9f513b4227adc226f689556425",    # EAILP05RDMA1, 5 mm vermelho, C7178079 (pino 1 = anodo)
    "LED_AM": "158b66005d134d328703a609b03dd193",    # LTL2R3KYD-EM, 5 mm amarelo, C5349085
    "LED_VD": "d3ed971443e244758e7ea89281837404",    # L-53GD, 5 mm verde, C19634105
    "TP": "8de09feb2de34cbe98ca04f37f7f9cbc",        # Keystone 5011, ponto de teste THT, C9900014807
    "MEGA": "58fe6412330c450884d28cbc43303f1e",      # ARDUINOMEGA2560 (charlyyoel15, biblioteca de usuarios): caixa com D0-D53, A0-A15, 5V, GND
}

EDITOR_JS = "https://easyeda.com/editor/6.5.57/js/main.min.js"
# chave -> nome do item no painel "Commons Library" do editor (folha 3; pinos: ver README)
COMUM = {
    "R_AXIAL": "R_AXIAL-0.4_EU",       # resistor axial 10 mm, simbolo IEC (retangulo)
    "TRIMPOT": "R_3386P_EU",           # trimpot 3386P: 1 e 3 nas pontas, 2 = cursor (em cima)
    "C_RAD": "C_RAD-0.2_EU",           # ceramico radial, passo 5 mm
    "LED_5MM_VM": "LED-TH-5mm_R",      # LED 5 mm vermelho (pino 1 = anodo)
    "LED_5MM_VD": "LED-TH-5mm_G",      # LED 5 mm verde
    "BOTAO_6X6": "K4-6×6_TH",          # tatil 6x6 THT, 4 pinos: 1-2 de um lado, 3-4 do outro
}


def baixar(chave):
    uuid = UUID[chave]
    url = f"https://easyeda.com/api/components/{uuid}?version=6.5.57&uuid={uuid}"
    j = json.loads(subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=60).stdout)
    assert j.get("success"), f"{chave}: resposta inesperada da API"
    LIB.mkdir(exist_ok=True)
    (LIB / f"{chave}.json").write_text(json.dumps(j["result"], ensure_ascii=False), encoding="utf-8")


def extrair_comuns(js):
    """{nome: simbolo} da Commons Library embutida no main.min.js do editor (objeto JS -> JSON)."""
    fim = js.find(',lc=[{title:"Supply Flag"')
    ini = js.rfind("={", 0, fim) + 1
    tok = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^"\']+')
    partes = []
    for m in tok.finditer(js[ini:fim]):
        t = m.group(0)
        if t.startswith("'"):                          # string JS de aspas simples -> JSON
            t = '"' + t[1:-1].replace("\\'", "'").replace('"', '\\"') + '"'
        elif not t.startswith('"'):                    # fora de string: chaves sem aspas, !0/!1
            t = re.sub(r'(?<=[{,])([A-Za-z_$][\w$]*)\s*:', r'"\1":', t).replace("!0", "true").replace("!1", "false")
        partes.append(t)
    return json.loads("".join(partes))


def baixar_comum():
    """Grava em lib/ os itens de COMUM que faltam, lendo o JS do editor uma vez so."""
    js = subprocess.run(["curl", "-s", EDITOR_JS], capture_output=True, text=True, timeout=120).stdout
    comuns = extrair_comuns(js)
    LIB.mkdir(exist_ok=True)
    for chave, nome in COMUM.items():
        arq = LIB / f"{chave}.json"
        if not arq.exists():
            arq.write_text(json.dumps({"title": nome, "dataStr": comuns[nome]}, ensure_ascii=False), encoding="utf-8")


def carregar(chave):
    arq = LIB / f"{chave}.json"
    if not arq.exists():
        baixar_comum() if chave in COMUM else baixar(chave)
    return json.loads(arq.read_text(encoding="utf-8"))


# ------------------------------------------------------------- deslocamento das primitivas
_TOK = re.compile(r"[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)(?:e-?\d+)?")
_NARGS = {"M": 2, "L": 2, "T": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "A": 7, "Z": 0}


def _num(v):
    return f"{v:g}"


def _caminho(d, dx, dy):
    """Desloca um caminho SVG ('M 460 290 h -10', 'M360,310h10'). Comandos minusculos sao relativos."""
    toks = _TOK.findall(d)
    out, i, cmd = [], 0, None
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]
            out.append(cmd)
            i += 1
            if cmd.upper() == "Z":
                continue
        n = _NARGS[cmd.upper()]
        args = [float(t) for t in toks[i:i + n]]
        i += n
        if cmd.isupper():
            if cmd == "H":
                args[0] += dx
            elif cmd == "V":
                args[0] += dy
            elif cmd == "A":
                args[5] += dx
                args[6] += dy
            else:
                args = [a + (dx if k % 2 == 0 else dy) for k, a in enumerate(args)]
        out.extend(_num(a) for a in args)
    return " ".join(out)


def _fim(d):
    """Ponto final de um caminho SVG simples (M/L/H/V absolutos ou relativos), o traco de um pino."""
    toks, x, y, i, cmd = _TOK.findall(d), 0.0, 0.0, 0, "M"
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd, i = t, i + 1
        elif cmd in "MLml":
            a, b = float(t), float(toks[i + 1])
            x, y = (a, b) if cmd.isupper() else (x + a, y + b)
            i += 2
        elif cmd in "Hh":
            x = float(t) if cmd == "H" else x + float(t)
            i += 1
        elif cmd in "Vv":
            y = float(t) if cmd == "V" else y + float(t)
            i += 1
        else:
            i += 1
    return x, y


def _pontos(s, dx, dy):
    v = [float(t) for t in s.split()]
    return " ".join(_num(a + (dx if k % 2 == 0 else dy)) for k, a in enumerate(v))


def _desloca(sh, dx, dy):
    """Desloca uma primitiva de simbolo do EasyEDA Std. Devolve None para tipos ignorados."""
    c = sh.split("~")
    t = c[0]
    if t in ("R", "E", "I", "J", "N"):
        c[1], c[2] = _num(float(c[1]) + dx), _num(float(c[2]) + dy)
    elif t == "T":                                  # T~marca~x~y~...
        c[2], c[3] = _num(float(c[2]) + dx), _num(float(c[3]) + dy)
    elif t in ("PL", "PG", "B"):
        c[1] = _pontos(c[1], dx, dy)
    elif t in ("PT", "A"):
        c[1] = _caminho(c[1], dx, dy)
    elif t == "P":
        seg = sh.split("^^")
        cab = seg[0].split("~")
        cab[4], cab[5] = _num(float(cab[4]) + dx), _num(float(cab[5]) + dy)
        seg[0] = "~".join(cab)
        seg[1] = _pontos(seg[1].replace("~", " "), dx, dy).replace(" ", "~")
        p2 = seg[2].split("~")
        p2[0] = _caminho(p2[0], dx, dy)
        seg[2] = "~".join(p2)
        for k in (3, 4):                            # nome e numero do pino
            f = seg[k].split("~")
            f[1], f[2] = _num(float(f[1]) + dx), _num(float(f[2]) + dy)
            seg[k] = "~".join(f)
        f = seg[5].split("~")                       # ponto de inversao
        f[1], f[2] = _num(float(f[1]) + dx), _num(float(f[2]) + dy)
        seg[5] = "~".join(f)
        if len(seg) > 6 and seg[6]:                 # marca de clock
            f = seg[6].split("~")
            f[1] = _caminho(f[1], dx, dy)
            seg[6] = "~".join(f)
        return "^^".join(seg)
    else:
        return None
    return "~".join(c)


def _pt(tam):
    return round(float(str(tam).replace("pt", "") or 7) * 1.33, 1)


def svg_de_shape(sh):
    """Primitiva do EasyEDA Std (ja deslocada) -> elemento SVG equivalente."""
    c = sh.split("~")
    t = c[0]
    e = lambda v: v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if t == "R":
        return (f'<rect x="{c[1]}" y="{c[2]}" width="{c[5]}" height="{c[6]}" rx="{c[3] or 0}" '
                f'fill="{c[10] if c[10].lower() != "none" else "none"}" stroke="{c[7]}" stroke-width="{c[8] or 1}"/>')
    if t == "E":
        return f'<ellipse cx="{c[1]}" cy="{c[2]}" rx="{c[3]}" ry="{c[4]}" fill="{c[8]}" stroke="{c[5]}" stroke-width="{c[6] or 1}"/>'
    if t in ("PL", "PG"):
        tag = "polyline" if t == "PL" else "polygon"
        return f'<{tag} points="{c[1]}" fill="{c[5]}" stroke="{c[2]}" stroke-width="{c[3] or 1}"/>'
    if t in ("PT", "A"):
        return f'<path d="{c[1]}" fill="{c[5]}" stroke="{c[2]}" stroke-width="{c[3] or 1}"/>'
    if t == "T":
        if c[13] != "1":
            return ""
        rot = f' transform="rotate({c[4]} {c[2]} {c[3]})"' if c[4] not in ("", "0") else ""
        return (f'<text x="{c[2]}" y="{c[3]}" font-size="{_pt(c[7])}" fill="{c[5]}" text-anchor="{c[14]}" '
                f'font-weight="{c[8] if c[8] in ("bold", "normal") else "normal"}"{rot}>{e(c[12])}</text>')
    if t == "P":
        seg = sh.split("^^")
        out = [f'<path d="{seg[2].split("~")[0]}" fill="none" stroke="{seg[2].split("~")[1]}" stroke-width="1"/>']
        for k, tam in ((3, 7), (4, 7)):                      # nome e numero do pino
            f = seg[k].split("~")
            if f[0] == "1":
                rot = f' transform="rotate({f[3]} {f[1]} {f[2]})"' if f[3] not in ("", "0") else ""
                out.append(f'<text x="{f[1]}" y="{f[2]}" font-size="{tam}" fill="{f[8] if len(f) > 8 and f[8] else "#0000FF"}" text-anchor="{f[5]}"{rot}>{e(f[4])}</text>')
        f = seg[5].split("~")
        if f[0] == "1":                                      # bolinha de inversao
            out.append(f'<circle cx="{f[1]}" cy="{f[2]}" r="3" fill="none" stroke="#880000"/>')
        return "".join(out)
    return ""


class Simbolo:
    """Um simbolo da biblioteca, pronto para ser colocado varias vezes."""

    def __init__(self, chave):
        r = carregar(chave)
        d = r["dataStr"]
        self.chave, self.titulo = chave, r["title"]
        self.c_para = d["head"]["c_para"]
        self.ox, self.oy = float(d["head"]["x"]), float(d["head"]["y"])
        self.shapes = d["shape"]
        bb = d["BBox"]
        self.bbox = (bb["x"] - self.ox, bb["y"] - self.oy, bb["width"], bb["height"])   # relativo a origem
        self.uuid = d["head"].get("uuid") or r.get("uuid", "")
        self.pinos = {}                              # numero -> (dx, dy, rotacao) relativo a origem
        self.nomes = {}                              # numero -> nome do pino no simbolo (VCC, GND, 1A...)
        self.saida = {}                              # numero -> sentido do fio que sai do pino (pelo traco do pino)
        for sh in self.shapes:
            if sh.startswith("P~"):
                seg = sh.split("^^")
                cab = seg[0].split("~")
                x, y = float(cab[4]), float(cab[5])
                self.pinos[cab[3]] = (x - self.ox, y - self.oy, int(float(cab[6] or 0)))
                self.nomes[cab[3]] = seg[3].split("~")[4]
                fx, fy = _fim(seg[2].split("~")[0])   # o traco vai do ponto de conexao ao corpo
                self.saida[cab[3]] = ((x > fx) - (x < fx), (y > fy) - (y < fy))

    def colocar(self, des, x, y, gid, valor=None, pos_des=None, pos_val=None, val_visivel=True, bom=True):
        """Coloca a origem do simbolo em (x, y). Devolve (bloco LIB, {pino: (x, y)}).

        `gid` e uma funcao que devolve ids novos. Os textos de designador e valor
        vao acima e abaixo do simbolo, salvo posicoes explicitas. Com bom=False a peca
        fica fora da BOM e da conversao para PCB (folha so ilustrativa).
        """
        dx, dy = x - self.ox, y - self.oy
        cp = self.c_para
        pre = cp.get("pre", "U?").rstrip("?") or "U"
        attrs = [("package", cp.get("package", "")), ("nameAlias", ""),
                 ("BOM_Manufacturer Part", cp.get("Manufacturer Part", "")), ("BOM_Supplier", cp.get("Supplier", "")),
                 ("BOM_Supplier Part", cp.get("Supplier Part", "")), ("BOM_Manufacturer", cp.get("Manufacturer", "")),
                 ("BOM_JLCPCB Part Class", cp.get("JLCPCB Part Class", "")), ("spicePre", pre),
                 ("spiceSymbolName", valor or cp.get("name", self.titulo)), ("Contributor", cp.get("Contributor", ""))]
        c_str = "".join(f"{k}`{v}`" for k, v in attrs)
        sn = "yes" if bom else "none"
        # campos do LIB no editor 6.5.57: x, y, c_para, rotacao, importFlag, gId, puuid, uuid, locked,
        # bind_pcb_id, convert_to_pcb, add_into_bom
        sub = [f"LIB~{x:g}~{y:g}~{c_str}~0~~{gid()}~{self.uuid}~~0~~{sn}~{sn}"]
        for sh in self.shapes:
            novo = _desloca(sh, dx, dy)
            if novo is None:
                continue
            novo = re.sub(r"gge\d+", lambda m: gid(), novo)
            sub.append(novo)
        bx, by, bw, bh = self.bbox
        px, py = pos_des or (x + bx, y + by - 4)
        vx, vy = pos_val or (x + bx, y + by + bh + 12)
        sub.append(f"T~P~{px:g}~{py:g}~0~#000080~~9pt~normal~normal~~comment~{des}~1~start~{gid()}~0~pinpart")
        sub.append(f"T~N~{vx:g}~{vy:g}~0~#000080~~8pt~normal~normal~~comment~{valor or cp.get('name', self.titulo)}~{int(val_visivel)}~start~{gid()}~0~pinpart")
        pinos = {n: (x + ddx, y + ddy) for n, (ddx, ddy, _) in self.pinos.items()}
        return "#@$".join(sub), pinos

    def fora(self, num):
        """Vetor unitario para fora do simbolo no pino `num` (sentido do fio de saida)."""
        if self.saida[num] != (0, 0):
            return self.saida[num]
        rot = self.pinos[num][2]                     # traco degenerado: usa a rotacao do pino
        return {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}[rot % 360]


if __name__ == "__main__":
    for chave in list(UUID) + list(COMUM):
        s = Simbolo(chave)
        pinos = sorted(s.pinos, key=lambda n: (not n.isdigit(), int(n) if n.isdigit() else n))
        print(f"{chave:<10} {s.titulo[:28]:<28} {s.c_para.get('Supplier Part', ''):<10} bbox={tuple(round(v, 1) for v in s.bbox)} "
              f"pinos={len(pinos)} {' '.join(f'{n}{'←→↑↓'[[(-1, 0), (1, 0), (0, -1), (0, 1)].index(s.fora(n))]}' for n in pinos[:16])}")
