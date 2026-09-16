#!/usr/bin/env python3
"""Desenha a montagem em protoboard da conferencia de carga a partir da mesma
fiacao de gerar_netlist.py e grava:

  conferencia_carga_protoboard.svg / .png   duas protoboards de 830 pontos + Arduino Mega
  conferencia_carga_protoboard.md           lista de montagem furo a furo, na ordem de montar

O mesmo desenho entra como folha 4 do projeto EasyEDA (conferencia_carga.json)
e como pagina 3 do PDF: gerar_esquema.py chama este modulo.

Uso:  python3 gerar_protoboard.py       (so SVG/PNG/MD)
      python3 gerar_esquema.py          (tudo, incluindo o projeto EasyEDA e o PDF)

Coordenadas: P1/P2 = placa; letra = linha (a-e acima do canal, f-j abaixo);
numero = coluna (1-63). Os 5 furos de uma coluna do mesmo lado do canal
(a-e ou f-j) sao um unico no ("tira").
"""
import subprocess
from pathlib import Path

from gerar_netlist import comps
from gerar_esquema import NOME, Folha, bezier, esc, pts

AQUI = Path(__file__).parent
NET = {des: pins for des, _, _, _, pins in comps}
DEV = {des: dev for des, dev, _, _, _ in comps}
VALOR = {des: val for des, _, val, _, _ in comps}

P = 16                            # passo entre furos (px)
COLS = 63
X0, YM, Y1, Y2 = 20, 40, 130, 560   # margem esquerda; topo do Mega, da placa 1 e da placa 2


def nome(net):
    return NOME.get(net, net)


class Furo:
    def __init__(self, placa, m, col, linha):
        self.placa, self.m, self.col, self.linha = placa, m, col, linha

    @property
    def xy(self):
        return self.placa.x(self.col), self.placa.y(self.linha)

    def __str__(self):
        return f"P{self.placa.num} {self.linha}{self.col}"


class Trilho:
    """Ponto num barramento de alimentacao: sinal '+'/'-', lado 't' (cima) ou 'b' (baixo)."""

    def __init__(self, placa, sinal, m, col):
        self.placa, self.sinal, self.m, self.col = placa, sinal, m, col

    @property
    def xy(self):
        return self.placa.x(self.col), self.placa.y(self.sinal + self.m)

    def __str__(self):
        return f"P{self.placa.num} barramento {self.sinal} de {'cima' if self.m == 't' else 'baixo'}"


class Mega:
    def __init__(self, pino, x):
        self.pino, self.x = pino, x

    @property
    def xy(self):
        return self.x, YM + 2.4 * P

    def __str__(self):
        return f"Mega {self.pino}"


class Placa:
    def __init__(self, num, titulo, y0):
        self.num, self.titulo, self.y0 = num, titulo, y0
        self.x0, self.w, self.h = X0, (COLS + 6) * P, 17.5 * P
        self.livres = {(m, c): list("abcde" if m == "t" else "jihgf") for m in "tb" for c in range(1, COLS + 1)}

    def x(self, col):
        return self.x0 + (col + 3) * P

    def y(self, linha):
        if linha in "abcde":
            return self.y0 + (4 + "abcde".index(linha)) * P
        if linha in "fghij":
            return self.y0 + (10 + "fghij".index(linha)) * P
        return {"+t": self.y0 + 1.2 * P, "-t": self.y0 + 2.2 * P,
                "-b": self.y0 + 15.3 * P, "+b": self.y0 + 16.3 * P}[linha]

    def furo(self, m, col, linha=None):
        """Ocupa um furo da tira (m, col). Sem `linha`: primeiro livre, nunca e/f (pecas)."""
        livres = self.livres[(m, col)]
        if linha is None:
            linha = next((l for l in livres if l not in "ef"), None)
            if linha is None:
                raise SystemExit(f"tira cheia: P{self.num} {m}{col}")
        if linha not in livres:
            raise SystemExit(f"furo ocupado: P{self.num} {linha}{col}")
        livres.remove(linha)
        return Furo(self, m, col, linha)


P1 = Placa(1, "Placa 1 - entradas do Mega, LEDs, potenciometros e botoes", Y1)
P2 = Placa(2, "Placa 2 - logica: U1 74HC04, U2 74HC32, U3 74HC86, U4/U5 74HC08, U6 74HC283", Y2)
PL = {1: P1, 2: P2}

tira_net, membros, pontos = {}, {}, {}   # tira -> net ; tira -> [pinos] ; net -> {tiras}
furo_pino = {}                           # (comp, pino) -> Furo | Trilho
pecas, fios, tps = [], [], []


def liga(des, pino, placa, m, col, linha=None):
    """Poe o pino `pino` de `des` num furo da tira (m, col) e registra a tira na net."""
    net = NET[des][pino]
    k = (placa.num, m, col)
    if tira_net.setdefault(k, net) != net:
        raise SystemExit(f"conflito em P{placa.num} {m}{col}: {tira_net[k]} x {net}")
    membros.setdefault(k, []).append(f"{des} p{pino}")
    pontos.setdefault(net, set()).add(k)
    furo_pino[(des, pino)] = placa.furo(m, col, linha)
    return furo_pino[(des, pino)]


# ------------------------------------------------ placa 2: CIs atravessando o canal, pino 1 na linha f
CIS = {"U1": 2, "U2": 11, "U3": 20, "U4": 29, "U5": 38, "U6": 47}
for des, c in CIS.items():
    n = 16 if DEV[des] == "74HC283" else 14
    for k in range(1, n + 1):
        m, col = ("b", c + k - 1) if k <= n // 2 else ("t", c + n - k)
        if str(k) in NET[des]:
            liga(des, str(k), P2, m, col, "f" if m == "b" else "e")
        else:                                            # saida de porta nao usada: so ocupa o furo
            P2.furo(m, col, "f" if m == "b" else "e")
    pecas.append(("dip", P2, c, n, des))

# ------------------------------------------------ placa 1: LEDs
# Sinal numa tira, resistor atravessa o canal (furos e/f da mesma coluna), LED do outro lado.
# 't' = sinal em cima (vem do Mega) e LED embaixo; 'b' = sinal embaixo (vem da placa 2) e LED em cima.
LEDS = [(f"D{b + 1}", 19 - 2 * b, "t") for b in range(10)]          # N0: bit 9 na coluna 1 ... bit 0 na 19
LEDS += [("D12", 23, "t"), ("D11", 25, "t")]                       # B1, B0
LEDS += [("D16", 29, "b"), ("D15", 31, "b"), ("D14", 33, "b"), ("D13", 35, "b")]   # S3..S0
LEDS += [("D17", 39, "b"), ("D18", 41, "b"), ("D19", 43, "b")]     # CONFERIR, ALARME, LIBERADO
COR_LED = {"D17": "#f0c000", "D18": "#e00000", "D19": "#00b000"}
for des, col, ms in LEDS:
    r, ml = "R" + des[1:], "b" if ms == "t" else "t"
    f1 = liga(r, "1", P1, ms, col, "e" if ms == "t" else "f")
    f2 = liga(r, "2", P1, ml, col, "f" if ml == "b" else "e")
    fa = liga(des, "1", P1, ml, col, "g" if ml == "b" else "d")
    fk = liga(des, "2", P1, ml, col + 1, "g" if ml == "b" else "d")
    pecas.append(("res", f1, f2, r))
    pecas.append(("led", fa, fk, des, COR_LED.get(des, "#f07070")))

# ------------------------------------------------ placa 1: potenciometros (3 pinos em linha) e botoes
for des, c in (("RV1", 47), ("RV2", 51)):
    for i, pino in enumerate("123"):
        liga(des, pino, P1, "t", c + i, "c")
    pecas.append(("pot", P1, c, des))

for des, c in (("SW2", 56), ("SW1", 60)):        # tatil de 4 pinos atravessando o canal, colunas c e c+2
    liga(des, "1", P1, "t", c, "e")              # 5 V
    liga(des, "3", P1, "b", c + 2, "f")          # sinal: terminal em diagonal ao de 5 V
    furo_pino[(des, "2")] = P1.furo("t", c + 2, "e")     # 2 e 4 sao ligados internamente a 1 e 3:
    furo_pino[(des, "4")] = P1.furo("b", c, "f")         # ficam nas tiras reservadas, sem fio
    P1.livres[("t", c + 2)] = P1.livres[("b", c)] = []
    pecas.append(("botao", P1, c, des))

# ------------------------------------------------ jumpers curtos de toda tira de VCC/GND ao barramento do seu lado
for k, net in sorted(tira_net.items()):
    if net in ("VCC", "GND"):
        pn, m, col = k
        fios.append(("trilho", net, PL[pn].furo(m, col), Trilho(PL[pn], "+" if net == "VCC" else "-", m, col)))


# ------------------------------------------------ pecas entre uma tira e o barramento: 100 nF e pull-downs
def para_trilho(des, placa, m, col, sinal, tipo, pino_furo="1", pino_trilho="2"):
    f = liga(des, pino_furo, placa, m, col)
    furo_pino[(des, pino_trilho)] = t = Trilho(placa, sinal, m, col)
    pecas.append((tipo, f, t, des))


for n in range(1, 7):                                        # C_n na tira do VCC de U_n, ao barramento -
    para_trilho(f"C{n}", P2, "t", CIS[f"U{n}"], "-", "cap", "2", "1")
para_trilho("Rpd2", P1, "b", 58, "-", "resv")               # pull-down de P1
para_trilho("Rpd1", P1, "b", 62, "-", "resv")               # pull-down de P0

# ------------------------------------------------ fios: Mega -> placa 1, depois encadeando as tiras de cada net
MEGA = {f"N0_{b}": f"D{22 + b}" for b in range(10)}
MEGA.update({"B_0": "D32", "B_1": "D33", "A0_CURSOR": "A0", "A1_CURSOR": "A1"})
ordem = lambda k: (k[0], k[1] != "t", k[2])                  # placa, lado (cima primeiro), coluna
for net in sorted(pontos, key=lambda n: (n not in MEGA, n)):
    if net in ("VCC", "GND"):
        continue
    ts = sorted(pontos[net], key=ordem)
    if net in MEGA:
        f = PL[ts[0][0]].furo(ts[0][1], ts[0][2])
        fios.append(("mega", net, Mega(MEGA[net], f.xy[0]), f))
    for a, b in zip(ts, ts[1:]):
        fa, fb = PL[a[0]].furo(a[1], a[2]), PL[b[0]].furo(b[1], b[2])
        fios.append(("entre" if a[0] != b[0] else "interno", net, fa, fb))

# alimentacao: Mega -> barramentos de cima da placa 1; pontes cima/baixo e placa 1 -> placa 2
fios += [("mega", "VCC", Mega("5V", P1.x(-1.4)), Trilho(P1, "+", "t", -1.4)),
         ("mega", "GND", Mega("GND", P1.x(-0.7)), Trilho(P1, "-", "t", -0.7)),
         ("ponte", "VCC", Trilho(P1, "+", "t", -1.4), Trilho(P1, "+", "b", -1.4)),
         ("ponte", "GND", Trilho(P1, "-", "t", -0.7), Trilho(P1, "-", "b", -0.7)),
         ("ponte", "VCC", Trilho(P1, "+", "b", COLS + 1.4), Trilho(P2, "+", "t", COLS + 1.4)),
         ("ponte", "GND", Trilho(P1, "-", "b", COLS + 0.7), Trilho(P2, "-", "t", COLS + 0.7)),
         ("ponte", "VCC", Trilho(P2, "+", "t", COLS + 1.4), Trilho(P2, "+", "b", COLS + 1.4)),
         ("ponte", "GND", Trilho(P2, "-", "t", COLS + 0.7), Trilho(P2, "-", "b", COLS + 0.7))]

# ------------------------------------------------ pontos de teste: um furo livre na tira do pino indicado
for des, pino in (("R4", "1"), ("R3", "1"), ("R2", "1"), ("R1", "1"), ("R12", "1"), ("R11", "1"),
                  ("SW2", "3"), ("SW1", "3"), ("U2", "3"), ("U2", "6"), ("U1", "4"), ("U5", "3"),
                  ("U6", "4"), ("U6", "1"), ("U6", "13"), ("U6", "10"), ("U6", "9")):
    f0 = furo_pino[(des, pino)]
    tps.append((nome(NET[des][pino]), f0.placa.furo(f0.m, f0.col)))

# ------------------------------------------------ conferencia: todo pino da netlist tem furo
for des, _, _, _, pins in comps:
    for pino in pins:
        assert (des, pino) in furo_pino, f"pino sem furo: {des} p{pino}"
assert {n for n in pontos} == {n for pins in NET.values() for n in pins.values()}


# ================================================================ desenho: SVG (previa) + folha do EasyEDA
# Cada primitiva vai para as duas listas: `svg` (previa/PDF) e `shape` (folha 4 do projeto EasyEDA Std).
svg, shape = [], []
_n = [0]
COR = {"VCC": "#d00000", "GND": "#111111", "P0": "#e07000", "P1": "#e07000"}
PALETA = ["#00a000", "#8000c0", "#008080", "#a05000", "#c0007a", "#607000", "#0040a0",
          "#c04000", "#209090", "#7a0040", "#4060a0", "#a0a000", "#d04080", "#306030"]
cor_net = {}


def cor(net):
    if net in COR or nome(net) in COR:
        return COR.get(net) or COR[nome(net)]
    if net in MEGA:
        return "#1f5fd0"
    return cor_net.setdefault(net, PALETA[len(cor_net) % len(PALETA)])


def gid():
    _n[0] += 1
    return f"gge{_n[0]}"


def hex6(c):
    """EasyEDA so aceita #RRGGBB."""
    return c if c == "none" or len(c) == 7 else "#" + "".join(ch * 2 for ch in c[1:])


def rect(x, y, w, h, fill, stroke=None, rx=0):
    stroke = stroke or fill
    svg.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="{stroke}"/>')
    shape.append(f"R~{x:g}~{y:g}~{rx:g}~{rx:g}~{w:g}~{h:g}~{hex6(stroke)}~1~0~{hex6(fill)}~{gid()}~0")


def circ(cx, cy, r, fill, stroke=None, sw=1):
    stroke = stroke or fill
    svg.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>')
    shape.append(f"E~{cx:g}~{cy:g}~{r:g}~{r:g}~{hex6(stroke)}~{sw:g}~0~{hex6(fill)}~{gid()}~0")


def poly(pontos, stroke, sw=1):
    p = pts(pontos)
    svg.append(f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{sw:g}"/>')
    shape.append(f"PL~{p}~{hex6(stroke)}~{sw:g}~0~none~{gid()}~0")


def T(x, y, s, tam=8, anc="middle", c="#000", peso="normal", halo=False, rot=0):
    extra = ' paint-order="stroke" stroke="#fff" stroke-width="3"' if halo else ""
    tr = f' transform="rotate({rot} {x:g} {y:g})"' if rot else ""
    svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{tam}" text-anchor="{anc}" fill="{c}" '
               f'font-weight="{peso}"{extra}{tr}>{esc(s)}</text>')
    shape.append(f"T~L~{x:g}~{y:g}~{rot}~{hex6(c)}~~{round(tam / 1.33, 1):g}pt~{peso}~normal~~comment~{s}~1~{anc}~{gid()}~0")


def desenha_placa(pl):
    rect(pl.x0, pl.y0, pl.w, pl.h, "#f3f2e9", "#8a8a80", rx=6)
    rect(pl.x(-1.7), pl.y("e") + 0.55 * P, (COLS + 3.4) * P, 0.9 * P, "#e2e1d6")
    for key, c, claro in (("+t", "#d00000", "#eaa8a8"), ("-t", "#0050c0", "#a8bce6"), ("-b", "#0050c0", "#a8bce6"), ("+b", "#d00000", "#eaa8a8")):
        y = pl.y(key)
        poly([(pl.x(-1.7), y), (pl.x(COLS + 1.7), y)], c, 1.2)
        T(pl.x(-2.3), y + 3, key[0], 9, c=c, peso="bold")
        for col in range(1, COLS + 1):
            circ(pl.x(col), y, 1.8, claro)
    for linha in "abcdefghij":
        T(pl.x(0), pl.y(linha) + 3, linha, 8, c="#666666")
        for col in range(1, COLS + 1):
            circ(pl.x(col), pl.y(linha), 2.3, "#c4c4b8")
    for col in [1] + list(range(5, COLS + 1, 5)):
        T(pl.x(col), pl.y0 + 3.3 * P, str(col), 7, c="#666666")
        T(pl.x(col), pl.y0 + 14.95 * P, str(col), 7, c="#666666")
    T(pl.x0, pl.y0 - 6, pl.titulo, 11, "start", peso="bold")


def desenha_fio(tipo, net, a, b, t=0.5):
    """t = posicao do rotulo ao longo do fio (0..1)."""
    c = cor(net)
    (x1, y1), (x2, y2) = a.xy, b.xy
    if isinstance(a, Furo) and isinstance(b, Furo) and a.placa is b.placa and a.m == b.m:
        pl = a.placa                                   # mesmo lado da mesma placa: arco por fora
        bulge = min(1.6 * P + abs(x2 - x1) * 0.16, 7 * P)
        cy = pl.y0 - bulge if a.m == "t" else pl.y0 + pl.h + bulge
        poly(bezier((x1, y1), ((x1 + x2) / 2, cy), (x2, y2), 16), c, 2)
        lx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * (x1 + x2) / 2 + t * t * x2
        ly = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t * t * y2
    else:
        poly([(x1, y1), (x2, y2)], c, 2)
        lx, ly = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
    for x, y in ((x1, y1), (x2, y2)):
        circ(x, y, 2.6, c)
    if tipo in ("interno", "entre") or (tipo == "mega" and net not in ("VCC", "GND")):
        T(lx, ly - 3, nome(net), 8, c=c, peso="bold", halo=True)


BANDAS = {"2.2k": ("#dd0000", "#dd0000", "#dd0000"), "10k": ("#7a3b00", "#000000", "#f08000")}


def desenha_res(f1, f2, des, dx=0):
    (x, y1), (_, y2) = f1.xy, f2.xy
    x, ym = x + dx, (y1 + y2) / 2
    poly([(x - dx, y1), (x, ym - 0.55 * P), (x, ym + 0.55 * P), (x - dx, y2)], "#777777", 1.5)
    rect(x - 0.28 * P, ym - 0.55 * P, 0.56 * P, 1.1 * P, "#e9d9a8", "#8a7a50", rx=2)
    for i, bc in enumerate(BANDAS[VALOR[des]]):
        rect(x - 0.28 * P, ym - 0.4 * P + i * 0.28 * P, 0.56 * P, 0.14 * P, bc)


def desenha_cap(f, t, des):
    (x, y1), (_, y2) = f.xy, t.xy
    x, ym = x + 0.4 * P, (y1 + y2) / 2
    poly([(x - 0.4 * P, y1), (x, ym + 0.35 * P), (x, ym - 0.35 * P), (x - 0.4 * P, y2)], "#777777", 1.5)
    rect(x - 0.32 * P, ym - 0.36 * P, 0.64 * P, 0.72 * P, "#e8c84a", "#8a7a20", rx=3)
    T(x + 0.45 * P, ym + 2, "100n", 6, "start", c="#555555")


def desenha_led(fa, fk, des, corl):
    (xa, ya), (xk, yk) = fa.xy, fk.xy
    xm = (xa + xk) / 2
    circ(xm, ya, 0.72 * P, corl, "#660000")
    poly([(xk + 0.2 * P, ya - 0.45 * P), (xk + 0.2 * P, ya + 0.45 * P)], "#660000", 2.5)   # lado chato = catodo
    sinal = nome(NET["R" + des[1:]]["1"])
    T(xm, ya + (1.35 * P if fa.m == "b" else -1.05 * P), {"CONFERIR": "CONF", "LIBERADO": "LIB"}.get(sinal, sinal), 7, peso="bold", halo=True)


def desenha_pot(pl, c, des):
    x, y = pl.x(c + 1), pl.y("b")
    circ(x, y, 1.25 * P, "#3a6ea5", "#112233")
    circ(x, y, 0.55 * P, "#ddddee", "#112233")
    poly([(x, y), (x + 0.5 * P, y - 0.5 * P)], "#112233", 2)
    T(x, pl.y("e") - 0.15 * P, f"{des} {VALOR[des]} ({MEGA[NET[des]['2']]})", 7, peso="bold", halo=True)


def desenha_botao(pl, c, des):
    x, y = pl.x(c + 1), (pl.y("e") + pl.y("f")) / 2
    rect(x - 1.1 * P, y - 1.1 * P, 2.2 * P, 2.2 * P, "#2f2f2f", "#000000", rx=3)
    circ(x, y, 0.6 * P, "#aa0000", "#000000")
    T(x, pl.y("g") + 0.35 * P, f"{des} = {nome(NET[des]['3'])}", 7, peso="bold", halo=True)


def desenha_dip(pl, c, n, des):
    x1, x2 = pl.x(c) - 0.5 * P, pl.x(c + n // 2 - 1) + 0.5 * P
    y1, y2 = pl.y("e") - 0.4 * P, pl.y("f") + 0.4 * P
    rect(x1, y1, x2 - x1, y2 - y1, "#2b2b2b", "#000000", rx=3)
    circ(x1, (y1 + y2) / 2, 0.35 * P, "#f3f2e9")          # entalhe (metade de fora some no fundo da placa)
    circ(x1 + 0.45 * P, y2 - 0.45 * P, 2.2, "#ffffff")    # pino 1
    T((x1 + x2) / 2, (y1 + y2) / 2 + 3, f"{des}  {DEV[des]}", 9, c="#ffffff", peso="bold")
    for k in range(1, n + 1):
        m, col = ("b", c + k - 1) if k <= n // 2 else ("t", c + n - k)
        T(pl.x(col), (y2 - 3) if m == "b" else (y1 + 8), str(k), 6, c="#dddddd")


def desenha_mega():
    x1, x2 = P1.x0, P1.x0 + P1.w
    rect(x1, YM, x2 - x1, 2.4 * P, "#1b7a8c", "#0d4a55", rx=5)
    T(x1 + 8, YM + 15, "Arduino Mega 2560 (fora das placas) - pinos usados:", 9, "start", c="#ffffff", peso="bold")
    for tipo, _, a, _ in fios:
        if tipo == "mega":
            circ(a.x, YM + 2.4 * P, 3, "#ffffff")
            T(a.x, YM + 2.4 * P - (16 if a.pino == "GND" else 6), a.pino, 7, c="#ffffff", peso="bold")


def desenha_tp(nm, f):
    x, y = f.xy
    circ(x, y, 0.38 * P, "#ffffff", "#c000c0", 2)
    if f.m == "b":
        T(x + 3, y + 0.6 * P, "TP " + nm, 6.5, "start", c="#c000c0", peso="bold", halo=True, rot=90)
    else:
        T(x + 3, y - 0.6 * P, "TP " + nm, 6.5, "end", c="#c000c0", peso="bold", halo=True, rot=90)


def legenda(y):
    itens = [("#d00000", "5 V"), ("#111111", "GND"), ("#1f5fd0", "Arduino -> placa 1"), ("#e07000", "botoes P1/P0"),
             ("#00a000", "demais cores: sinais internos (nome sobre o fio)"), ("#c000c0", "o = ponto de teste (TP)")]
    x = X0
    for c, s in itens:
        poly([(x, y), (x + 22, y)], c, 3)
        T(x + 27, y + 3, s, 8, "start")
        x += 27 + 5.2 * len(s) + 24
    notas = ["Cada coluna de 5 furos do mesmo lado do canal e um unico no. CIs e resistores dos LEDs atravessam o canal (furos e/f da mesma coluna).",
             "LED: perna longa (anodo) na coluna do resistor; lado chato (catodo) na coluna seguinte, com jumper ao barramento -. Cada LED com 2,2 k em serie.",
             "Botoes tateis: usar os dois terminais em diagonal (sao sempre os contatos da chave). Solto = 0 pelo pull-down de 10 k ao barramento -.",
             "Se os barramentos da sua protoboard forem partidos no meio (coluna 30/31), emende cada metade com um jumper. 100 nF junto ao VCC de cada CI.",
             "Lista furo a furo, na ordem de montagem, em conferencia_carga_protoboard.md. Mesma fiacao do esquema (gerar_netlist.py)."]
    for i, s in enumerate(notas):
        T(X0, y + 18 + i * 12, "- " + s, 8, "start")


_folha = None


def folha():
    """Folha com o desenho, nos dois formatos (EasyEDA e SVG). Desenha uma unica vez."""
    global _folha
    if _folha is not None:
        return _folha
    W, H = X0 * 2 + P1.w, Y2 + P2.h + 7.5 * P + 95
    T(X0, 24, "Trabalho AP1 - Sistemas Digitais 2026.2 - Turma 6a - Folha 4/4: montagem em protoboard (2 placas de 830 pontos + Arduino Mega 2560)", 13, "start", peso="bold")
    desenha_mega()
    desenha_placa(P1)
    desenha_placa(P2)
    for tipo in ("trilho", "ponte", "mega", "entre", "interno"):       # fios por baixo das pecas
        for i, (t, net, a, b) in enumerate(f for f in fios if f[0] == tipo):
            desenha_fio(t, net, a, b, (0.5, 0.32, 0.68)[i % 3])
    for pc in pecas:
        {"dip": desenha_dip, "res": desenha_res, "led": desenha_led, "cap": desenha_cap, "pot": desenha_pot,
         "botao": desenha_botao, "resv": lambda f, t, des: desenha_res(f, t, des, dx=0.4 * P)}[pc[0]](*pc[1:])
    for nm, f in tps:
        desenha_tp(nm, f)
    legenda(Y2 + P2.h + 7.5 * P + 10)
    _folha = Folha(W, H)
    _folha.shape, _folha.svg = shape, svg
    return _folha


# ================================================================ lista de montagem (Markdown)
def tabela(cab, linhas):
    return ["| " + " | ".join(cab) + " |", "| " + " | ".join("-" * len(c) for c in cab) + " |",
            *("| " + " | ".join(str(c) for c in l) + " |" for l in linhas), ""]


def lista_md():
    tira = lambda f: membros.get((f.placa.num, f.m, f.col), [])
    L = ["# Montagem em protoboard — conferência de carga", "",
         "Gerado por `gerar_protoboard.py` a partir da mesma fiação do esquema (`gerar_netlist.py`);",
         "desenho em `conferencia_carga_protoboard.png`. Duas protoboards de 830 pontos (63 colunas;",
         "linhas a–e acima do canal central, f–j abaixo) e o Arduino Mega fora das placas.", "",
         "**Coordenadas:** `P1 c19` = placa 1, linha c, coluna 19. Os 5 furos de uma coluna do mesmo",
         "lado do canal são um único nó, então qualquer furo livre da mesma tira serve. Os furos",
         "indicados são os do desenho.", "",
         "## 1. Alimentação", ""]
    L += [f"- Mega **{a.pino}** → {b} (extremidade esquerda)." for t, _, a, b in fios if t == "mega" and isinstance(a, Mega) and a.pino in ("5V", "GND")]
    L += [f"- Ponte: {a} ↔ {b} ({'esquerda' if a.col < 1 else 'direita'})." for t, _, a, b in fios if t == "ponte"]
    L += ["- Barramento **+** = 5 V, **−** = GND, nas duas placas. Se os barramentos forem partidos no meio (coluna 30/31), emende cada metade.", "",
          "## 2. CIs na placa 2 (atravessando o canal, entalhe para a esquerda, pino 1 na linha f)", ""]
    linhas = []
    for des, c in CIS.items():
        n = 16 if DEV[des] == "74HC283" else 14
        linhas.append((des, DEV[des], f"{c}–{c + n // 2 - 1}", f"P2 f{c}", f"pino {n} em {furo_pino[(des, str(n))]}", f"pino {n // 2} em {furo_pino[(des, str(n // 2))]}"))
    L += tabela(("CI", "Tipo", "Colunas", "Pino 1", "VCC", "GND"), linhas)
    L += ["## 3. Jumpers curtos aos barramentos (+ = 5 V, − = GND)", ""]
    L += tabela(("Furo", "Barramento", "Liga"), [(f, "+ (5 V)" if net == "VCC" else "− (GND)", ", ".join(tira(f))) for t, net, f, _ in fios if t == "trilho"])
    L += ["## 4. Capacitores de 100 nF e pull-downs de 10 k (de um furo direto ao barramento −)", ""]
    L += tabela(("Peça", "Valor", "De", "Para"), [(pc[3], VALOR[pc[3]], pc[1], pc[2]) for pc in pecas if pc[0] in ("cap", "resv")])
    L += ["## 5. LEDs na placa 1 (resistor de 2,2 k atravessa o canal; catodo na coluna seguinte, com jumper ao −)", ""]
    res = {pc[3]: (pc[1], pc[2]) for pc in pecas if pc[0] == "res"}
    linhas = []
    for tipo, fa, fk, des, corl in (p for p in pecas if p[0] == "led"):
        r = "R" + des[1:]
        cor_nome = {"D17": "amarelo", "D18": "vermelho", "D19": "verde"}.get(des, "qualquer")
        linhas.append((des, nome(NET[r]["1"]), cor_nome, f"{r}: {res[r][0]} ↔ {res[r][1]}", fa, fk))
    L += tabela(("LED", "Sinal", "Cor", "Resistor", "Anodo (perna longa)", "Catodo (lado chato)"), linhas)
    L += ["## 6. Potenciômetros e botões (placa 1)", ""]
    L += tabela(("Peça", "Ligação"), [
        (f"{des} {VALOR[des]}", f"pino 1 em {furo_pino[(des, '1')]} (5 V pelo jumper) · cursor em {furo_pino[(des, '2')]} → Mega {MEGA[NET[des]['2']]} · pino 3 em {furo_pino[(des, '3')]} (GND pelo jumper)") for des in ("RV1", "RV2")] + [
        (f"{des} (tátil 4 pinos)", f"atravessa o canal nas colunas {c} e {c + 2}; 5 V no terminal {furo_pino[(des, '1')]}; sinal {nome(NET[des]['3'])} no terminal em diagonal {furo_pino[(des, '3')]}; as tiras P1 t{c + 2}/b{c} ficam só para o botão") for des, c in (("SW2", 56), ("SW1", 60))])
    L += ["## 7. Fios do Arduino Mega para a placa 1", ""]
    L += tabela(("Pino do Mega", "Sinal", "Furo"), [(a.pino, nome(net), b) for t, net, a, b in fios if t == "mega" and a.pino not in ("5V", "GND")])
    L += ["## 8. Fios entre as placas", ""]
    L += tabela(("Sinal", "De", "Para"), [(nome(net), a, b) for t, net, a, b in fios if t == "entre"])
    L += ["## 9. Fios internos da placa 2", ""]
    L += tabela(("Sinal", "De", "Para"), sorted(((nome(net), a, b) for t, net, a, b in fios if t == "interno"), key=lambda l: l[0]))
    L += ["## 10. Pontos de teste (furo livre na tira do sinal)", ""]
    L += tabela(("TP", "Furo"), tps)
    n = {t: sum(1 for f in fios if f[0] == t) for t in ("trilho", "ponte", "mega", "entre", "interno")}
    L += [f"Total: {sum(n.values())} fios ({n['trilho']} jumpers a barramento, {n['ponte']} pontes, {n['mega']} do Mega, {n['entre']} entre placas, {n['interno']} internos), "
          f"{len(pecas)} peças, {len(tps)} pontos de teste.", ""]
    return "\n".join(L)


def main():
    """Grava SVG, PNG e lista. A folha entra no projeto EasyEDA e no PDF por gerar_esquema.py."""
    (AQUI / "conferencia_carga_protoboard.svg").write_text(folha().svg_texto(), encoding="utf-8")
    (AQUI / "conferencia_carga_protoboard.md").write_text(lista_md(), encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", "2300", "-o", str(AQUI / "conferencia_carga_protoboard.png"),
                    str(AQUI / "conferencia_carga_protoboard.svg")], check=True)
    print(f"{len(pecas)} pecas, {len(fios)} fios, {len(tps)} pontos de teste, {len(tira_net)} tiras usadas")


if __name__ == "__main__":
    main()
