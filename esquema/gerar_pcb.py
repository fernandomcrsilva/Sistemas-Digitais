#!/usr/bin/env python3
"""Gera a placa de circuito impresso da conferencia de carga a partir da mesma
fiacao de gerar_netlist.py:

  conferencia_carga_pcb.json   PCB no formato EasyEDA Std (docType 3)
  conferencia_carga_pcb.svg    previa (vermelho = topo, azul = fundo, amarelo = silk)

Uso:  python3 gerar_pcb.py

No EasyEDA Std: Arquivo > Abrir > EasyEDA... e escolha o .json. Placa de 2
camadas, so componentes THT. O Arduino Mega NAO fica na placa: liga-se pelo
conector J1 (5 V, GND, A0, A1, D22-D33) com jumpers.

Unidades do EasyEDA: 1 = 10 mil (0,254 mm). Grade de roteamento: 50 mil.
"""
import heapq
import json
import math
from pathlib import Path

from gerar_netlist import comps
from gerar_esquema import NOME

AQUI = Path(__file__).parent
NET = {des: pins for des, _, _, _, pins in comps}
VALOR = {des: val for des, _, val, _, _ in comps}

OX, OY = 4000, 3000            # origem da placa no canvas do EasyEDA
W, H = 620, 360                # 6,2 x 3,6 pol = 157 x 91 mm
G = 5                          # passo da grade de roteamento (50 mil)
LARG_TRILHA, FOLGA = 1.0, 0.6  # 10 mil, 6 mil
VIA_D, VIA_FURO_R = 3.2, 0.8   # 0,8 mm / furo 0,4 mm


def nome_net(n):
    return NOME.get(n, n) if n else ""


# ------------------------------------------------------------ footprints
# pad: (numero, x, y, forma, diametro, raio_do_furo)   silk: ("pl", pts) | ("c", cx, cy, r)
def dip(n):
    m = n // 2
    pads = [(i + 1, 0, i * 10, "RECT" if i == 0 else "ELLIPSE", 6.2, 1.6) for i in range(m)]
    pads += [(m + 1 + i, 30, (m - 1 - i) * 10, "ELLIPSE", 6.2, 1.6) for i in range(m)]
    yb = (m - 1) * 10 + 5
    silk = [("pl", [(-5, -5), (35, -5), (35, yb), (-5, yb), (-5, -5)]), ("pl", [(11, -5), (11, -2), (19, -2), (19, -5)])]
    return {"pads": pads, "silk": silk, "txt": (-5, -8)}


FP = {
    "DIP14": dip(14), "DIP16": dip(16),
    "RES": {"pads": [(1, 0, 0, "ELLIPSE", 6.2, 1.6), (2, 40, 0, "ELLIPSE", 6.2, 1.6)],
            "silk": [("pl", [(8, -4), (32, -4), (32, 4), (8, 4), (8, -4)]), ("pl", [(4, 0), (8, 0)]), ("pl", [(32, 0), (36, 0)])],
            "txt": (8, -7)},
    "LED5": {"pads": [(1, 0, 0, "RECT", 6.2, 1.6), (2, 10, 0, "ELLIPSE", 6.2, 1.6)],
             "silk": [("c", 5, 0, 10), ("pl", [(13.5, -7.5), (13.5, 7.5)])],   # lado plano = catodo
             "txt": (-5, -13)},
    "CAP": {"pads": [(1, 0, 0, "ELLIPSE", 6.2, 1.6), (2, 10, 0, "ELLIPSE", 6.2, 1.6)],
            "silk": [("pl", [(-3, -5), (13, -5), (13, 5), (-3, 5), (-3, -5)])], "txt": (-3, -8)},
    "POT": {"pads": [(1, 0, 0, "RECT", 7, 2), (2, 10, 0, "ELLIPSE", 7, 2), (3, 20, 0, "ELLIPSE", 7, 2)],
            "silk": [("pl", [(-8, -14), (28, -14), (28, 6), (-8, 6), (-8, -14)])], "txt": (-8, -17)},
    # tactile 6x6 mm: pinos 1-2 ligados entre si, 3-4 idem; contato entre os pares
    "SW6": {"pads": [(1, 0, 0, "RECT", 7, 2), (2, 25.6, 0, "ELLIPSE", 7, 2),
                     (3, 0, 17.7, "ELLIPSE", 7, 2), (4, 25.6, 17.7, "ELLIPSE", 7, 2)],
            "silk": [("pl", [(1, -3), (24.6, -3), (24.6, 20.7), (1, 20.7), (1, -3)]), ("c", 12.8, 8.85, 7)],
            "txt": (-4, -7)},
    "HDR16": {"pads": [(i + 1, 0, i * 10, "RECT" if i == 0 else "ELLIPSE", 6.2, 2) for i in range(16)],
              "silk": [("pl", [(-5, -5), (5, -5), (5, 155), (-5, 155), (-5, -5)])], "txt": (-5, -8)},
    "TP": {"pads": [(1, 0, 0, "ELLIPSE", 8, 2)], "silk": [("c", 0, 0, 5.5)], "txt": (-5, -8)},
}


def gira(x, y, rot):
    return {0: (x, y), 90: (-y, x), 180: (-x, -y), 270: (y, -x)}[rot]


# ------------------------------------------------------------ posicionamento
pecas = []   # dict(des, fp, x, y, rot, nets{num: net}, valor)


def coloca(des, fp, x, y, rot=0, nets=None, valor=""):
    if nets is None:
        nets = {int(k): v for k, v in NET[des].items()}
    pecas.append({"des": des, "fp": fp, "x": x, "y": y, "rot": rot, "nets": nets, "valor": valor or VALOR.get(des, "")})


# conector do Arduino Mega (jumpers): 1=5V 2=GND 3=A0 4=A1 5..14=D22..D31 15=D32 16=D33
J1 = {1: "VCC", 2: "GND", 3: "A0_CURSOR", 4: "A1_CURSOR"}
J1.update({5 + b: f"N0_{b}" for b in range(10)})
J1.update({15: "B_0", 16: "B_1"})
coloca("J1", "HDR16", 25, 40, 0, J1, "Mega: 5V GND A0 A1 D22-D33")

# fileira de LEDs no topo (bit 9 -> bit 0, B1 B0, S3..S0, status); resistor em pe abaixo
ordem = [f"D{b + 1}" for b in range(9, -1, -1)] + ["D12", "D11", "D16", "D15", "D14", "D13", "D17", "D18", "D19"]
for i, d in enumerate(ordem):
    x = 75 + i * 25
    r = d.replace("D", "R")
    coloca(d, "LED5", x, 30)
    coloca(r, "RES", x, 90, 270)          # pino 1 (sinal) embaixo, pino 2 (anodo) em cima

# CIs com 100 nF ao lado
for i, (u, pkg) in enumerate((("U2", "DIP14"), ("U3", "DIP14"), ("U1", "DIP14"), ("U5", "DIP14"), ("U4", "DIP14"), ("U6", "DIP16"))):
    x = 90 + i * 80
    coloca(u, pkg, x, 150)
    coloca(f"C{i + 1}", "CAP", x + 55, 155, 90)

# potenciometros, botoes e pull-downs na borda inferior
coloca("RV1", "POT", 80, 330)
coloca("RV2", "POT", 160, 330)
for sw, rpd, x in (("SW2", "Rpd2", 280), ("SW1", "Rpd1", 400)):
    coloca(sw, "SW6", x, 310, 0, valor="push-button")
    coloca(rpd, "RES", x, 290)

# pontos de teste
TPS = [("X0", "N0_0", 55, 80), ("X1", "N0_1", 55, 95), ("X2", "N0_2", 55, 110), ("X3", "N0_3", 55, 125),
       ("B0", "B_0", 55, 150), ("B1", "B_1", 55, 165), ("P1", "P1", 345, 310), ("P0", "P0", 465, 310),
       ("FALHA", "FALHA", 90, 250), ("DIFERENTE", "DIFERENTE", 140, 250), ("IGUAL", "IGUAL", 200, 250),
       ("H", "H", 250, 250), ("S0", "S0", 300, 250), ("S1", "S1", 340, 250), ("S2", "S2", 380, 250),
       ("S3", "S3", 420, 250), ("C_OUT", "COUT", 470, 250)]
for i, (rotulo, net, x, y) in enumerate(TPS, 1):
    coloca(f"TP{i}", "TP", x, y, 0, {1: net}, rotulo)

# ------------------------------------------------------------ pads absolutos
pads = []   # dict(des, num, x, y, forma, d, furo, net)
for pc in pecas:
    for num, px, py, forma, d, furo in FP[pc["fp"]]["pads"]:
        rx, ry = gira(px, py, pc["rot"])
        pads.append({"des": pc["des"], "num": num, "x": pc["x"] + rx, "y": pc["y"] + ry,
                     "forma": forma, "d": d, "furo": furo, "net": pc["nets"].get(num, "")})

# ------------------------------------------------------------ roteador
NX, NY = W // G + 1, H // G + 1
dono = [[[None] * NY for _ in range(NX)] for _ in range(2)]    # [camada][gx][gy] -> net | "#"
for c in range(2):
    for gx in range(NX):
        dono[c][gx][0] = dono[c][gx][NY - 1] = "#"
    for gy in range(NY):
        dono[c][0][gy] = dono[c][NX - 1][gy] = "#"


via_ok = [[True] * NY for _ in range(NX)]      # celula longe o bastante de todo pad


def marca(c, gx, gy, net):
    atual = dono[c][gx][gy]
    if atual is None or atual == net:
        dono[c][gx][gy] = net
    else:
        dono[c][gx][gy] = "#"


for p in pads:
    r = p["d"] / 2
    alcance = r + FOLGA + LARG_TRILHA / 2
    alc_via = r + FOLGA + VIA_D / 2
    p["celulas"] = []
    for gx in range(max(0, int((p["x"] - alc_via) // G)), min(NX, int((p["x"] + alc_via) // G) + 2)):
        for gy in range(max(0, int((p["y"] - alc_via) // G)), min(NY, int((p["y"] + alc_via) // G) + 2)):
            if math.hypot(gx * G - p["x"], gy * G - p["y"]) <= alc_via:
                via_ok[gx][gy] = False
    for gx in range(max(1, int((p["x"] - alcance) // G)), min(NX - 1, int((p["x"] + alcance) // G) + 2)):
        for gy in range(max(1, int((p["y"] - alcance) // G)), min(NY - 1, int((p["y"] + alcance) // G) + 2)):
            dist = math.hypot(gx * G - p["x"], gy * G - p["y"])
            if dist <= alcance:
                for c in range(2):
                    marca(c, gx, gy, p["net"] or "#")
                if dist <= r and p["net"]:
                    p["celulas"].append((gx, gy))
    if p["net"] and not p["celulas"]:
        p["celulas"].append((round(p["x"] / G), round(p["y"] / G)))
    p["celula"] = min(p["celulas"], key=lambda cg: math.hypot(cg[0] * G - p["x"], cg[1] * G - p["y"])) if p["celulas"] else None


def custo_passo(c, dx, dy):
    # fundo (c=1) prefere horizontal, topo (c=0) prefere vertical
    if c == 1:
        return 1 if dy == 0 else 2.5
    return 1 if dx == 0 else 2.5


def dijkstra(fontes, alvos, net):
    dist, prev, fila = {}, {}, []
    for s in fontes:
        dist[s] = 0
        heapq.heappush(fila, (0, s))
    while fila:
        d, u = heapq.heappop(fila)
        if d > dist.get(u, 1e18):
            continue
        if u in alvos:
            cam = [u]
            while cam[-1] in prev:
                cam.append(prev[cam[-1]])
            return cam[::-1]
        c, gx, gy = u
        viz = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx_, ny_ = gx + dx, gy + dy
            if 0 <= nx_ < NX and 0 <= ny_ < NY and dono[c][nx_][ny_] in (None, net):
                viz.append(((c, nx_, ny_), custo_passo(c, dx, dy)))
        oc = 1 - c
        if via_ok[gx][gy] and dono[oc][gx][gy] is None and dono[c][gx][gy] is None:   # via em celula livre
            viz.append(((oc, gx, gy), 8))
        for v, w in viz:
            nd = d + w
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(fila, (nd, v))
    return None


trilhas, vias, falhas = [], [], []     # trilhas: (camada, net, [(x, y), ...])
por_net = {}
for p in pads:
    if p["net"]:
        por_net.setdefault(p["net"], []).append(p)

for net, lista in sorted(por_net.items(), key=lambda kv: -len(kv[1])):
    # tocos do centro do pad ate a celula da grade (pads fora da grade)
    for p in lista:
        cx, cy = p["celula"][0] * G, p["celula"][1] * G
        if (cx, cy) != (p["x"], p["y"]):
            trilhas.append((0, net, [(p["x"], p["y"]), (cx, cy)]))
    if len(lista) < 2:
        continue
    ligados = [lista[0]]
    conectado = {(c, gx, gy) for c in range(2) for gx, gy in lista[0]["celulas"]}
    restantes = lista[1:]
    while restantes:
        p = min(restantes, key=lambda q: min(abs(q["x"] - l["x"]) + abs(q["y"] - l["y"]) for l in ligados))
        restantes.remove(p)
        ligados.append(p)
        fontes = [(c, gx, gy) for c in range(2) for gx, gy in p["celulas"]]
        cam = dijkstra(fontes, conectado, net)
        if cam is None:
            falhas.append((net, p["des"], p["num"]))
            conectado |= set(fontes)
            continue
        # segmenta por camada
        seg = [cam[0]]
        for u in cam[1:]:
            if u[0] != seg[-1][0]:                       # troca de camada = via
                vias.append((net, seg[-1][1] * G, seg[-1][2] * G))
                trilhas.append((seg[0][0], net, [(a[1] * G, a[2] * G) for a in seg]))
                seg = [u]
            else:
                seg.append(u)
        trilhas.append((seg[0][0], net, [(a[1] * G, a[2] * G) for a in seg]))
        for c, gx, gy in cam:
            dono[c][gx][gy] = net
            conectado.add((c, gx, gy))
        for c, gx, gy in cam:
            if dono[1 - c][gx][gy] == net:               # celula de via: ocupa as duas camadas
                conectado.add((1 - c, gx, gy))


def simplifica(pts):
    out = [pts[0]]
    for i in range(1, len(pts)):
        if i + 1 < len(pts) and ((pts[i - 1][0] == pts[i][0] == pts[i + 1][0]) or (pts[i - 1][1] == pts[i][1] == pts[i + 1][1])):
            continue
        out.append(pts[i])
    return out


# ------------------------------------------------------------ saida EasyEDA
_n = [0]


def gid():
    _n[0] += 1
    return f"gge{_n[0]}"


def f(v):
    return f"{v + 0:g}"


shape = []
shape.append(f"TRACK~1~10~~{OX} {OY} {OX + W} {OY} {OX + W} {OY + H} {OX} {OY + H} {OX} {OY}~{gid()}~0")
for hx, hy in ((10, 10), (W - 10, 10), (10, H - 10), (W - 10, H - 10)):
    shape.append(f"HOLE~{OX + hx}~{OY + hy}~12.6~{gid()}~0")

pads_por_peca = {}
for p in pads:
    pads_por_peca.setdefault(p["des"], []).append(p)
for pc in pecas:
    fp = FP[pc["fp"]]
    sub = [f"LIB~{f(OX + pc['x'])}~{f(OY + pc['y'])}~package`{pc['fp']}`~0~~{gid()}~1"]
    tx, ty = gira(*fp["txt"], pc["rot"])
    sub.append(f"TEXT~P~{f(OX + pc['x'] + tx)}~{f(OY + pc['y'] + ty)}~0.8~0~none~3~~4.5~{pc['des']}~~~{gid()}~0")
    for s in fp["silk"]:
        if s[0] == "pl":
            pts = " ".join(f"{f(OX + pc['x'] + a)} {f(OY + pc['y'] + b)}" for a, b in (gira(x, y, pc["rot"]) for x, y in s[1]))
            sub.append(f"TRACK~0.8~3~~{pts}~{gid()}~0")
        else:
            cx, cy = gira(s[1], s[2], pc["rot"])
            sub.append(f"CIRCLE~{f(OX + pc['x'] + cx)}~{f(OY + pc['y'] + cy)}~{s[3]}~0.8~3~{gid()}~0")
    for p in pads_por_peca[pc["des"]]:
        x, y, d = OX + p["x"], OY + p["y"], p["d"]
        pontos = ""
        if p["forma"] == "RECT":
            h = d / 2
            pontos = f"{f(x - h)} {f(y - h)} {f(x + h)} {f(y - h)} {f(x + h)} {f(y + h)} {f(x - h)} {f(y + h)}"
        sub.append(f"PAD~{p['forma']}~{f(x)}~{f(y)}~{d}~{d}~11~{nome_net(p['net'])}~{p['num']}~{p['furo']}~{pontos}~0~{gid()}~0~~Y~0")
    shape.append("#@$".join(sub))
for camada, net, pts in trilhas:
    pts = simplifica(pts)
    s = " ".join(f"{f(OX + x)} {f(OY + y)}" for x, y in pts)
    shape.append(f"TRACK~{LARG_TRILHA}~{1 if camada == 0 else 2}~{nome_net(net)}~{s}~{gid()}~0")
for net, x, y in vias:
    shape.append(f"VIA~{f(OX + x)}~{f(OY + y)}~{VIA_D}~{nome_net(net)}~{VIA_FURO_R}~{gid()}~0")
for rotulo, net, x, y in TPS:
    shape.append(f"TEXT~L~{f(OX + x + 6)}~{f(OY + y + 2)}~0.8~0~none~3~~4~{rotulo}~~~{gid()}~0")
shape.append(f"TEXT~L~{OX + 75}~{OY + H - 8}~0.8~0~none~3~~5~AP1 Sistemas Digitais 2026.2 - Conferencia de carga - turma 6a~~~{gid()}~0")

pcb = {
    "head": {"docType": "3", "editorVersion": "6.5.57", "newgId": True, "c_para": {}, "x": OX, "y": OY, "hasIdFlag": True},
    "canvas": f"CA~1000~1000~#000000~yes~#FFFFFF~10~1000~1000~line~0.5~mil~1~45~~0.5~{OX}~{OY}~0~yes",
    "shape": shape,
    "layers": ["1~TopLayer~#FF0000~true~true~true~", "2~BottomLayer~#0000FF~true~false~true~",
               "3~TopSilkLayer~#FFCC00~true~false~true~", "4~BottomSilkLayer~#66CC33~true~false~true~",
               "5~TopPasteMaskLayer~#808080~true~false~true~", "6~BottomPasteMaskLayer~#800000~true~false~true~",
               "7~TopSolderMaskLayer~#800080~true~false~true~0.3", "8~BottomSolderMaskLayer~#AA00FF~true~false~true~0.3",
               "9~Ratlines~#6464FF~true~false~true~", "10~BoardOutLine~#FF00FF~true~false~true~",
               "11~Multi-Layer~#C0C0C0~true~false~true~", "12~Document~#FFFFFF~true~false~true~",
               "Hole~Hole~#222222~~false~true~", "DRCError~DRCError~#FAD609~~false~true~"],
    "objects": ["All~true~false", "Component~true~true", "Prefix~true~true", "Name~true~false", "Track~true~true",
                "Pad~true~true", "Via~true~true", "Hole~true~true", "Copper_Area~true~true", "Circle~true~true",
                "Arc~true~true", "Solid_Region~true~true", "Text~true~true", "Image~true~true", "Rect~true~true",
                "Dimension~true~true", "Protractor~true~true"],
    "BBox": {"x": OX, "y": OY, "width": W, "height": H},
    "preference": {"hideFootprints": "", "hideNets": ""},
    "DRCRULE": {"Default": {"trackWidth": LARG_TRILHA, "clearance": FOLGA, "viaHoleDiameter": VIA_D, "viaHoleD": VIA_FURO_R * 2},
                "isRealtime": False, "isDrcOnRoutingOrPlaceVia": False, "checkObjectToCopperarea": True, "showDRCRangeLine": True},
    "netColors": {},
}
(AQUI / "conferencia_carga_pcb.json").write_text(json.dumps(pcb, ensure_ascii=False, indent=1), encoding="utf-8")

# ------------------------------------------------------------ previa SVG
ESC = 3
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W * ESC}" height="{H * ESC}" viewBox="-2 -2 {W + 4} {H + 4}" font-family="Arial, sans-serif">',
       f'<rect x="-2" y="-2" width="{W + 4}" height="{H + 4}" fill="#1c1c1c"/>',
       f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0f2b16" stroke="#FF00FF" stroke-width="0.6"/>']
for camada, cor in ((1, "#2f5cff"), (0, "#ff3333")):
    for c, net, pts in trilhas:
        if c == camada:
            svg.append(f'<polyline points="{" ".join(f"{x:g},{y:g}" for x, y in pts)}" fill="none" stroke="{cor}" stroke-width="{LARG_TRILHA}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
for net, x, y in vias:
    svg.append(f'<circle cx="{x:g}" cy="{y:g}" r="{VIA_D / 2}" fill="#bbbbbb"/><circle cx="{x:g}" cy="{y:g}" r="{VIA_FURO_R}" fill="#1c1c1c"/>')
for p in pads:
    if p["forma"] == "RECT":
        svg.append(f'<rect x="{p["x"] - p["d"] / 2:g}" y="{p["y"] - p["d"] / 2:g}" width="{p["d"]}" height="{p["d"]}" fill="#d0d0d0"/>')
    else:
        svg.append(f'<circle cx="{p["x"]:g}" cy="{p["y"]:g}" r="{p["d"] / 2}" fill="#d0d0d0"/>')
    svg.append(f'<circle cx="{p["x"]:g}" cy="{p["y"]:g}" r="{p["furo"]}" fill="#1c1c1c"/>')
for pc in pecas:
    fp = FP[pc["fp"]]
    for s in fp["silk"]:
        if s[0] == "pl":
            pts = " ".join(f"{pc['x'] + a:g},{pc['y'] + b:g}" for a, b in (gira(x, y, pc["rot"]) for x, y in s[1]))
            svg.append(f'<polyline points="{pts}" fill="none" stroke="#FFCC00" stroke-width="0.8"/>')
        else:
            cx, cy = gira(s[1], s[2], pc["rot"])
            svg.append(f'<circle cx="{pc["x"] + cx:g}" cy="{pc["y"] + cy:g}" r="{s[3]}" fill="none" stroke="#FFCC00" stroke-width="0.8"/>')
    tx, ty = gira(*fp["txt"], pc["rot"])
    svg.append(f'<text x="{pc["x"] + tx:g}" y="{pc["y"] + ty:g}" font-size="4.5" fill="#FFCC00">{pc["des"]}</text>')
for rotulo, net, x, y in TPS:
    svg.append(f'<text x="{x + 6:g}" y="{y + 2:g}" font-size="4" fill="#FFCC00">{rotulo}</text>')
for hx, hy in ((10, 10), (W - 10, 10), (10, H - 10), (W - 10, H - 10)):
    svg.append(f'<circle cx="{hx}" cy="{hy}" r="6.3" fill="#1c1c1c" stroke="#888" stroke-width="0.5"/>')
# ratsnest do que nao roteou
for net, des, num in falhas:
    p = next(q for q in pads if q["des"] == des and q["num"] == num)
    o = next(q for q in pads if q["net"] == net and (q["des"], q["num"]) != (des, num))
    svg.append(f'<line x1="{p["x"]:g}" y1="{p["y"]:g}" x2="{o["x"]:g}" y2="{o["y"]:g}" stroke="#ffffff" stroke-width="0.5" stroke-dasharray="2,2"/>')
svg.append("</svg>")
(AQUI / "conferencia_carga_pcb.svg").write_text("\n".join(svg), encoding="utf-8")

print(f"{len(pecas)} pecas, {len(pads)} pads, {len(por_net)} nets, {len(trilhas)} trilhas, {len(vias)} vias, "
      f"{len(falhas)} ligacoes sem rota" + (f": {falhas}" if falhas else ""))
