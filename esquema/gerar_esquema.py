#!/usr/bin/env python3
"""Desenha o esquema da conferencia de carga a partir da fiacao de
gerar_netlist.py e grava, da mesma descricao:

  conferencia_carga.json   projeto EasyEDA Std com quatro folhas: 1 = circuito que
                           sera montado (simbolos LCSC), 2 = notas de modelagem e
                           testes, 3 = montagem com o Arduino no centro e pecas da
                           Commons Library, 4 = protoboard (de gerar_protoboard.py)
  conferencia_carga.pdf    as quatro folhas exportadas (via rsvg-convert)
  conferencia_carga.svg / _notas.svg / _montagem.svg / _protoboard.svg   previa de cada folha

Uso:  python3 gerar_esquema.py

No EasyEDA Std (easyeda.com/editor): Arquivo > Abrir > EasyEDA... e escolha o
.json; depois Arquivo > Salvar para ter o projeto editavel na nuvem.
"""
import json
import math
import subprocess
from pathlib import Path

from gerar_netlist import comps
from biblioteca import Simbolo, svg_de_shape

AQUI = Path(__file__).parent
# Preencha antes de entregar - mesmos nomes e matriculas do cabecalho do .ino.
INTEGRANTES = "<NOME - MATRICULA> (representante), <NOME - MATRICULA>, <NOME - MATRICULA>"
NET = {des: pins for des, _, _, _, pins in comps}
DEV = {des: dev for des, dev, _, _, _ in comps}
VALOR = {des: val for des, _, val, _, _ in comps}
CHAVE = {des: chave for des, _, _, chave, _ in comps}        # simbolo LCSC da folha 1
LED_COR = {"LED": "vermelho 5 mm", "LED_VM": "vermelho 5 mm", "LED_AM": "amarelo 5 mm", "LED_VD": "verde 5 mm"}

# nomes de net como aparecem no desenho (a netlist usa nomes internos)
NOME = {f"N0_{b}": f"X{b}" if b < 4 else f"N0_{b}" for b in range(10)}
NOME.update({"B_0": "B0", "B_1": "B1", "Ae1": "A1e", "Ae0": "A0e",
             "Be1": "B1e", "Be0": "B0e", "COUT": "C_OUT"})


def net(des, pino):
    return NOME.get(NET[des][pino], NET[des][pino])


# --------------------------------------------------------------- cores
SIMB, PINO, TXT, FIO, NETL = "#880000", "#0000FF", "#000000", "#008800", "#0000FF"
ROT = {"L": 180, "R": 0, "U": 90, "D": 270}
FONTE = "Arial, Liberation Sans, sans-serif"
MONO = "Liberation Mono, DejaVu Sans Mono, monospace"


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def pts(seq):
    return " ".join(f"{x:g} {y:g}" for x, y in seq)


class Folha:
    """Acumula os elementos nos dois formatos ao mesmo tempo."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.shape, self.svg = [], []
        self._n = 0
        self.tp = 0
        self.bom = True                              # False: pecas da folha fora da BOM e da PCB (folha 3)

    def gid(self):
        self._n += 1
        return f"gge{self._n}"

    # ---- primitivas livres
    def fio(self, seq):
        self.shape.append(f"W~{pts(seq)}~{FIO}~1~0~none~{self.gid()}~0")
        self.svg.append(f'<polyline points="{pts(seq)}" fill="none" stroke="{FIO}" stroke-width="1"/>')

    def juncao(self, x, y):
        self.shape.append(f"J~{x:g}~{y:g}~2.5~#CC0000~{self.gid()}~0")
        self.svg.append(f'<circle cx="{x:g}" cy="{y:g}" r="2.5" fill="#CC0000"/>')

    def netlabel(self, x, y, nome, lado="R"):
        anc = "start" if lado == "R" else "end"
        tx = x + 4 if lado == "R" else x - 4
        self.shape.append(f"N~{x:g}~{y:g}~0~{NETL}~{nome}~{self.gid()}~{anc}~{tx:g}~{y + 3:g}~~7pt~0")
        self.svg.append(f'<text x="{tx:g}" y="{y + 3:g}" font-size="9" fill="{NETL}" text-anchor="{anc}">{esc(nome)}</text>')

    def texto(self, x, y, s, tam="9pt", cor=TXT, anc="start", peso="normal", fam=""):
        self.shape.append(f"T~L~{x:g}~{y:g}~0~{cor}~{fam}~{tam}~{peso}~normal~~comment~{s}~1~{anc}~{self.gid()}~0")
        px = round(float(tam[:-2]) * 1.33, 1)
        f = MONO if "Courier" in fam else FONTE
        self.svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{px}" font-family="{f}" font-weight="{peso}" fill="{cor}" text-anchor="{anc}" xml:space="preserve">{esc(s)}</text>')

    def moldura(self, x, y, w, h, titulo):
        self.shape.append(f"R~{x:g}~{y:g}~~~{w:g}~{h:g}~#0000FF~1~1~none~{self.gid()}~0")
        self.svg.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" fill="none" stroke="#0000FF" stroke-width="1" stroke-dasharray="6,4"/>')
        self.texto(x + 6, y + 14, titulo, "10pt", "#0000FF", peso="bold")

    def flag(self, tipo, x, y):
        """Bandeira VCC/GND com o ponto de conexao em (x, y)."""
        if tipo == "GND":
            pls = [[(x, y), (x, y + 10)], [(x - 10, y + 10), (x + 10, y + 10)],
                   [(x - 6, y + 14), (x + 6, y + 14)], [(x - 2, y + 18), (x + 2, y + 18)]]
            tx, ty, anc = x, y + 30, "middle"
            part = "part_netLabel_gnD"
        else:
            pls = [[(x, y), (x, y - 10)], [(x - 8, y - 10), (x + 8, y - 10)]]
            tx, ty, anc = x, y - 14, "middle"
            part = "part_netLabel_VCC"
        cor = "#000080"
        sh = "^^".join(f"PL~{pts(p)}~{cor}~1~0~none~{self.gid()}~0" for p in pls)
        self.shape.append(f"F~{part}~{x:g}~{y:g}~~{self.gid()}~0^^{x:g}~{y:g}^^{tipo}~{cor}~{tx:g}~{ty:g}~0~{anc}~1~~9pt^^{sh}")
        for p in pls:
            self.svg.append(f'<polyline points="{pts(p)}" fill="none" stroke="{cor}" stroke-width="1"/>')
        self.svg.append(f'<text x="{tx:g}" y="{ty:g}" font-size="11" fill="{cor}" text-anchor="{anc}">{tipo}</text>')

    # ---- simbolos
    def simbolo(self, des, nome, x, y, sym, pkg="", pre=""):
        """sym = dict(shapes, pins, des, val). Devolve {pino: (x, y) do ponto}."""
        sub, pontos = [], {}
        pre = pre or "".join(c for c in des if c.isalpha())[:2]
        sub.append(f"LIB~{x:g}~{y:g}~package`{pkg}`spicePre`{pre}`spiceSymbolName`{nome}`~0~~{self.gid()}~0")
        for sh in sym["shapes"]:
            k = sh[0]
            if k == "rect":
                _, rx, ry, w, h = sh
                sub.append(f"R~{x + rx:g}~{y + ry:g}~~~{w:g}~{h:g}~{SIMB}~1~0~none~{self.gid()}~0")
                self.svg.append(f'<rect x="{x + rx:g}" y="{y + ry:g}" width="{w:g}" height="{h:g}" fill="none" stroke="{SIMB}" stroke-width="1"/>')
            elif k == "pl":
                p = [(x + a, y + b) for a, b in sh[1]]
                sub.append(f"PL~{pts(p)}~{SIMB}~1~0~none~{self.gid()}~0")
                self.svg.append(f'<polyline points="{pts(p)}" fill="none" stroke="{SIMB}" stroke-width="1"/>')
            elif k == "el":
                _, cx, cy, r = sh
                sub.append(f"E~{x + cx:g}~{y + cy:g}~{r:g}~{r:g}~{SIMB}~1~0~none~{self.gid()}~0")
                self.svg.append(f'<circle cx="{x + cx:g}" cy="{y + cy:g}" r="{r:g}" fill="none" stroke="{SIMB}" stroke-width="1"/>')
        for marca, (dx, dy, anc), s in (("P", sym["des"], des), ("N", sym["val"], nome)):
            vis = 0 if (marca == "N" and sym.get("val_oculto")) else 1
            if s:
                sub.append(f"T~{marca}~{x + dx:g}~{y + dy:g}~0~{TXT}~~9pt~normal~normal~~comment~{s}~{vis}~{anc}~{self.gid()}~0")
                if vis:
                    self.svg.append(f'<text x="{x + dx:g}" y="{y + dy:g}" font-size="11" fill="{TXT}" text-anchor="{anc}">{esc(s)}</text>')
        for num, nm, px, py, d, ln, mostra_nome in sym["pins"]:
            ax, ay = x + px, y + py
            ex, ey = ax, ay
            if d == "L":
                ex += ln
            elif d == "R":
                ex -= ln
            elif d == "U":
                ey += ln
            else:
                ey -= ln
            path = f"M {ax:g} {ay:g} L {ex:g} {ey:g}"
            if d in "LR":                     # numero acima da linha, nome dentro da caixa
                nx, ny, nanc = (ax + ex) / 2, ay - 2, "middle"
                mx, my, manc = (ex + 3, ay + 3, "start") if d == "L" else (ex - 3, ay + 3, "end")
            else:
                nx, ny, nanc = ax + 3, (ay + ey) / 2 + 3, "start"
                mx, my, manc = (ex, ey + 10, "middle") if d == "U" else (ex, ey - 4, "middle")
            mn = 1 if mostra_nome else 0
            sub.append(f"P~show~0~{num}~{ax:g}~{ay:g}~{ROT[d]}~{self.gid()}~0^^{ax:g}~{ay:g}^^{path}~{SIMB}"
                       f"^^{mn}~{mx:g}~{my:g}~0~{nm}~{manc}~~7pt^^1~{nx:g}~{ny:g}~0~{num}~{nanc}~~7pt"
                       f"^^0~{ax:g}~{ay:g}^^0~M {ax:g} {ay:g}")
            self.svg.append(f'<line x1="{ax:g}" y1="{ay:g}" x2="{ex:g}" y2="{ey:g}" stroke="{SIMB}" stroke-width="1"/>')
            self.svg.append(f'<text x="{nx:g}" y="{ny:g}" font-size="8" fill="{PINO}" text-anchor="{nanc}">{num}</text>')
            if mostra_nome:
                self.svg.append(f'<text x="{mx:g}" y="{my:g}" font-size="9" fill="{PINO}" text-anchor="{manc}">{esc(nm)}</text>')
            pontos[str(num)] = (ax, ay)
        self.shape.append("#@$".join(sub))
        return pontos

    # ---- simbolos da biblioteca do EasyEDA (pecas LCSC, ver biblioteca.py)
    def lib(self, des, chave, x, y, valor=None, **kw):
        """Coloca a origem do simbolo `chave` em (x, y). Devolve ({pino: (x, y)}, Simbolo)."""
        simb = SIMB.setdefault(chave, Simbolo(chave))
        bloco, pinos = simb.colocar(des, x, y, self.gid, valor, bom=self.bom, **kw)
        self.shape.append(bloco)
        self.svg.extend(svg_de_shape(sub) for sub in bloco.split("#@$")[1:])
        return pinos, simb

    def toco(self, p, d, nome=None, ln=20):
        """Fio curto saindo do pino p na direcao d = (dx, dy), com netlabel opcional no fim."""
        (x, y), (dx, dy) = p, d
        ex, ey = x + dx * ln, y + dy * ln
        self.fio([(x, y), (ex, ey)])
        if nome:
            self.netlabel(ex, ey, nome, "L" if dx < 0 else "R")
        return ex, ey

    def pinos_rotulados(self, des, q, s, ln=(30, 60)):
        """Toco + rotulo em cada pino ligado do CI. Pinos de alimentacao viram bandeiras;
        entradas ociosas ao GND vao a um barramento lateral com uma bandeira so.
        Comprimentos alternados por paridade do pino, para os rotulos nao se empilharem."""
        ociosas = {}
        for num, nome_net in NET[des].items():
            d = s.fora(num)
            if s.nomes.get(num, "").upper() in ("VCC", "GND", "VDD", "VSS"):
                self.toco_flag(q[num], d, nome_net)
            elif nome_net == "GND":
                ociosas.setdefault(d, []).append(self.toco(q[num], d, ln=ln[int(num) % 2]))
            else:
                self.toco(q[num], d, NOME.get(nome_net, nome_net), ln[int(num) % 2])
        for d, pontos in ociosas.items():
            self.entradas_gnd(pontos, d[0])

    def toco_flag(self, p, d, tipo, ln=20):
        self.flag(tipo, *self.toco(p, d, ln=ln))

    def ponto_teste(self, x, y, nome):
        """Ponto de teste (Keystone 5011) em (x, y), ligado a net `nome` por rotulo."""
        self.tp += 1
        p, s = self.lib(f"TP{self.tp}", "TP", x, y, nome, val_visivel=False)
        self.toco(p["1"], s.fora("1"), nome)

    def entradas_gnd(self, pontos, lado=-1):
        """Entradas nao usadas: barramento curto (a esquerda se lado < 0, a direita se > 0) ate uma bandeira GND."""
        xs = [p[0] for p in pontos]
        ys = [p[1] for p in pontos]
        bx, by = (min(xs) - 20 if lado < 0 else max(xs) + 20), max(ys) + 20
        for x, y in pontos:
            self.fio([(bx, y), (x, y)])
        self.fio([(bx, min(ys)), (bx, by)])
        for y in ys[1:]:
            self.juncao(bx, y)
        self.flag("GND", bx, by)

    def banco_leds(self, x, y0, passo, itens, r_chave="R2K2", led_valor=False):
        """Fileiras 'net -> resistor -> LED -> GND'. itens: (net, R, D, chave do LED).
        O fio de entrada comeca em (x - 60, y); o catodo vai a um GND comum a direita.
        led_valor: a cor vira o nome do LED (simbolo generico da folha 3, sem codigo de peca)."""
        for i, (nome, r, d, chave) in enumerate(itens):
            y = y0 + i * passo
            pr, _ = self.lib(r, r_chave, x, y, VALOR[r], pos_des=(x - 20, y - 8), pos_val=(x - 8, y + 16))
            pd, _ = self.lib(d, chave, x + 80, y, LED_COR[CHAVE[d]] if led_valor else None, pos_des=(x + 62, y - 20), val_visivel=False)
            self.fio([(x - 60, y), pr["1"]])
            self.fio([pr["2"], pd["1"]])
            self.fio([pd["2"], (x + 140, y)])
            if nome:
                self.netlabel(x - 60, y, nome, "L")
        yb = y0 + (len(itens) - 1) * passo
        self.fio([(x + 140, y0), (x + 140, yb + 20)])
        for i in range(1, len(itens)):
            self.juncao(x + 140, y0 + i * passo)
        self.flag("GND", x + 140, yb + 20)

    def caixa(self, des, nome, x, y, pinos_esq, pinos_dir, w=100, passo=20, topo=None, base=None):
        """Retangulo generico com pinos nomeados (usado so para o modulo Arduino, que nao e peca de BOM)."""
        sym, _ = S_CAIXA(pinos_esq, pinos_dir, w, passo, topo, base)
        return self.simbolo(des, nome, x, y, sym, "", "M")

    # ---- gravacao
    def folha_json(self, titulo):
        return {"docType": "1", "title": titulo, "description": "", "dataStr": {
            "head": {"docType": "1", "editorVersion": "6.5.57", "newgId": True,
                     "c_para": {"Prefix Start": "1"}, "c_spiceCmd": None},
            "canvas": f"CA~1000~1000~#FFFFFF~yes~#CCCCCC~10~{self.w}~{self.h}~line~10~pixel~5~0~0",
            "shape": self.shape,
            "BBox": {"x": 0, "y": 0, "width": self.w, "height": self.h},
            "colors": {}}}

    def svg_texto(self):
        return "\n".join([
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" font-family="{FONTE}">',
            '<defs><pattern id="g" width="10" height="10" patternUnits="userSpaceOnUse">'
            '<path d="M 10 0 L 0 0 0 10" fill="none" stroke="#E4E4E4" stroke-width="0.5"/></pattern></defs>',
            f'<rect width="{self.w}" height="{self.h}" fill="#FFFFFF"/>',
            f'<rect width="{self.w}" height="{self.h}" fill="url(#g)"/>',
            *self.svg, "</svg>"])


SIMB = {}   # cache dos simbolos da biblioteca


# ------------------------------------------------------------ caixa do Arduino
def bezier(p0, p1, p2, n=12):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append((round((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], 1),
                    round((1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1], 1)))
    return out


def S_CAIXA(esq, dir_, w=100, passo=20, topo=None, base=None):
    """esq/dir_: (num, nome) ou (num, nome, y). Caixa de (20,20) a (20+w, 20+h)."""
    def ys(lst):
        return [(e[0], e[1], e[2] if len(e) > 2 else 40 + i * passo) for i, e in enumerate(lst)]
    esq, dir_ = ys(esq), ys(dir_)
    h = max([y for _, _, y in esq + dir_] + [40]) - 20 + 20
    pins = [(n, nm, 0, y, "L", 20, 1) for n, nm, y in esq]
    pins += [(n, nm, w + 40, y, "R", 20, 1) for n, nm, y in dir_]
    if topo:
        pins.append((topo[0], topo[1], 20 + w / 2, 0, "U", 20, 1))
    if base:
        pins.append((base[0], base[1], 20 + w / 2, h + 40, "D", 20, 1))
    return {"shapes": [("rect", 20, 20, w, h)], "pins": pins,
            "des": (20, 12, "start"), "val": (20 + w, 12, "end")}, h


# ------------------------------------------------------------ alocacao das portas (texto)
QUAD = [("1", "2", "3"), ("4", "5", "6"), ("9", "10", "8"), ("12", "13", "11")]   # DIP-14 de 2 entradas
HEX = [("1", "2"), ("3", "4"), ("5", "6"), ("9", "8"), ("11", "10"), ("13", "12")]  # 74HC04
OPER = {"74HC08": ".", "74HC32": "+", "74HC86": "xor"}


def alocacao(des):
    """Linhas 'pinos: equacao' de um CI de portas, derivadas da netlist."""
    pins, dev, L = NET[des], DEV[des], []
    if dev == "74HC04":
        for a, y in HEX:
            if y in pins:
                L.append(f"{a}>{y}:  {net(des, y)} = {net(des, a)}'")
    else:
        for a, b, y in QUAD:
            if y in pins:
                L.append(f"{a},{b}>{y}:  {net(des, y)} = {net(des, a)} {OPER[dev]} {net(des, b)}")
    ociosas = [p for p in sorted(pins, key=int) if pins[p] == "GND" and p not in ("7", "8")]
    if ociosas:
        L.append("ociosas ao GND: " + ", ".join(ociosas))
    return L


# ================================================================ folha 1
def folha_esquema():
    f = Folha(2700, 1000)
    f.texto(30, 30, "Trabalho AP1 - Sistemas Digitais 2026.2 - Turma 6a - Folha 1/4: conferencia de carga para inspecao (Arduino Mega 2560)", "14pt", peso="bold")
    f.texto(30, 48, f"Integrantes: {INTEGRANTES}     Prof. Clayton J A Silva", "9pt")
    f.texto(30, 64, "Simbolos da biblioteca LCSC do EasyEDA (pecas THT, com footprint e codigo de peca). O Arduino Mega e um modulo: caixa com os pinos usados.", "8pt", "#444444")

    # ---- bloco 1: aquisicao ------------------------------------------------
    f.moldura(30, 80, 760, 600, "1. Aquisicao - Arduino Mega 2560, potenciometros e barramentos N0 (D22-D31) e B (D32-D33)")
    esq = [("5V", "5V", 40), ("GND", "GND", 60), ("A0", "A0", 120), ("A1", "A1", 280)]
    dir_ = [(f"D{22 + i}", f"D{22 + i}", 40 + i * 40) for i in range(12)]
    ax, ay = 230, 130
    p = f.caixa("M1", "Arduino Mega 2560", ax, ay, esq, dir_, w=120)
    f.fio([(p["5V"][0] - 40, p["5V"][1]), p["5V"]])
    f.flag("VCC", p["5V"][0] - 40, p["5V"][1])
    f.fio([(p["GND"][0] - 40, p["GND"][1]), p["GND"]])
    f.flag("GND", p["GND"][0] - 40, p["GND"][1])
    # trimpots 3386P: 1 = 5 V, 2 = cursor (pino de cima), 3 = GND
    for rv, pino in (("RV1", "A0"), ("RV2", "A1")):
        px, py = p[pino]
        q, s = f.lib(rv, "POT10K", px - 110, py + 50, VALOR[rv])
        c = f.toco(q["2"], s.fora("2"))
        f.fio([c, (c[0], py), (px, py)])
        f.toco_flag(q["1"], s.fora("1"), "VCC")
        f.toco_flag(q["3"], s.fora("3"), "GND")
    # barramentos: pino do Mega -> fio com netlabel -> R -> LED -> GND comum
    lx = 560
    f.banco_leds(lx, ay + 40, 40, [(NOME[NET[f"R{i + 1}"]["1"]], f"R{i + 1}", f"D{i + 1}", "LED_VM") for i in range(12)])
    for i in range(12):
        f.fio([p[f"D{22 + i}"], (lx - 60, ay + 40 + i * 40)])
    f.texto(60, 650, "N0 = analogRead(A0) e N1 = analogRead(A1): 10 bits (0-1023), passo 5 V/1024 = 4,88 mV. X = N0 mod 16 = x3x2x1x0, A = x1x0, B = N1 mod 4.", "8pt", "#444444")
    f.texto(60, 664, "Codigos ciclicos, sem reescalonar. N0_4..N0_9 so vao a LED. Cada LED com 2,2 k em serie (~1,4 mA).", "8pt", "#444444")

    # ---- bloco 3: botoes ---------------------------------------------------
    f.moldura(30, 700, 760, 190, "3. Conferencia - push-buttons R = P1P0 (solto = 0 pelo pull-down de 10 k, pressionado = 1)")
    for i, (sw, rpd) in enumerate((("SW2", "Rpd2"), ("SW1", "Rpd1"))):
        x, y = 330 + i * 300, 770
        q, s = f.lib(sw, "BOTAO", x, y, "tatil 6x6")
        f.toco_flag(q["1"], s.fora("1"), "VCC", 30)
        no = f.toco(q["3"], s.fora("3"), NOME.get(NET[sw]["3"], NET[sw]["3"]), ln=40)
        r, sr = f.lib(rpd, "R10K", no[0] + 60, no[1] + 40, VALOR[rpd])     # pino 1 no sinal, 2 ao GND
        f.fio([no, (no[0], no[1] + 40), r["1"]])
        f.toco_flag(r["2"], sr.fora("2"), "GND")
        f.texto(x + 45, y - 8, "2 e 4 ligados a 1 e 3", "7pt", "#444444")
    f.texto(60, 875, "Os botoes codificam um numero, nao guardam confirmacao: soltar ou pressionar refaz a conferencia. R = 0 com os dois soltos e selecao valida.", "8pt", "#444444")

    # ---- bloco 2: logica em cinco CIs de portas ------------------------------
    f.moldura(810, 80, 1310, 560, "2, 4, 5 e 7. Logica - validacao, comparador, habilitacao e LEDs de status (uma caixa por CI; equacoes por porta abaixo)")
    for i, des in enumerate(("U1", "U2", "U3", "U4", "U5")):
        x, y = 960 + i * 250, 250
        q, s = f.lib(des, DEV[des], x, y, DEV[des])
        f.pinos_rotulados(des, q, s)
        for k, linha in enumerate(alocacao(des)):
            f.texto(x - 115, 350 + k * 12, linha, "7pt", fam="Courier New")
    f.texto(830, 470, "Validacao: FALHA = x3 + x2 (U2, portas 1,2>3). Comparador so com portas: DIFERENTE = (A1 xor P1) + (A0 xor P0) (U3 1,2>3 e 4,5>6; U2 4,5>6), IGUAL = DIFERENTE' (U1 3>4).", "8pt", "#444444")
    f.texto(830, 484, "Habilitacao: H = FALHA'.IGUAL (U1 1>2, U5 1,2>3); as quatro AND de U4 liberam A1 A0 B1 B0 com H - com H = 0 o somador recebe 0 + 0.", "8pt", "#444444")
    f.texto(830, 498, "Status: EXCESSO = S3 + S2 (U2 9,10>8); CONFERIR = FALHA'.DIFERENTE (U5 4,5>6); ALARME = FALHA + EXCESSO (U2 12,13>11); LIBERADO = H.EXCESSO' (U5 9,10>8, U1 5>6).", "8pt", "#444444")
    f.texto(830, 512, "ALARME nao realimenta H: nada sai de U2 pino 11 alem do LED. Saidas nao usadas (U1 8, 10, 12; U3 8, 11; U5 11) ficam abertas; entradas ociosas ao GND.", "8pt", "#444444")
    f.texto(830, 526, "A e X sao os mesmos nos (A1 A0 = X1 X0). Todos os rotulos de net desta folha ligam-se entre si; os pontos de teste estao no bloco 9.", "8pt", "#444444")

    # ---- bloco 6: somador --------------------------------------------------
    f.moldura(2140, 80, 530, 560, "6. Somador 74HC283 - C_in = 0, bits superiores em 0, S3..S0 nos LEDs")
    q, s = f.lib("U6", "74HC283", 2290, 250, DEV["U6"])
    f.pinos_rotulados("U6", q, s)
    f.texto(2160, 380, "Indice 1 do datasheet = LSB: A0e/B0e nos pinos 5/6, A1e/B1e nos pinos 3/2.", "8pt", "#444444")
    f.texto(2160, 394, "3 + 3 = 0110: o carry do estagio 1 aparece em S2. S3 e C_OUT ficam em 0", "8pt", "#444444")
    f.texto(2160, 408, "com operandos <= 3. S2 e S3 vao ao LED e ao OR de EXCESSO: o excedente", "8pt", "#444444")
    f.texto(2160, 422, "continua visivel (nao zera a soma).", "8pt", "#444444")
    f.banco_leds(2360, 460, 40, [("S0", "R13", "D13", "LED_VM"), ("S1", "R14", "D14", "LED_VM"),
                                  ("S2", "R15", "D15", "LED_VM"), ("S3", "R16", "D16", "LED_VM")])

    # ---- bloco 7: LEDs de status --------------------------------------------
    f.moldura(810, 700, 500, 190, "7. Liberacao da carga - LEDs de status")
    f.banco_leds(1000, 750, 40, [("CONFERIR", "R17", "D17", "LED_AM"), ("ALARME", "R18", "D18", "LED_VM"), ("LIBERADO", "R19", "D19", "LED_VD")])
    f.texto(830, 882, "Exatamente um dos tres aceso em qualquer situacao.", "7pt", "#444444")

    # ---- bloco 8: alimentacao ----------------------------------------------
    f.moldura(1330, 700, 600, 190, "8. Alimentacao - 5 V e GND do Mega comuns a todos os CIs; 100 nF junto ao VCC de cada CI")
    for n in range(1, 7):
        x = 1390 + (n - 1) * 90
        q, s = f.lib(f"C{n}", "C100N", x, 780, VALOR[f"C{n}"])
        f.toco_flag(q["2"], s.fora("2"), "VCC")
        f.toco_flag(q["1"], s.fora("1"), "GND")
        f.texto(x + 14, 785, f"U{n}", "7pt", "#444444")
    f.texto(1350, 882, "VCC: pino 14 de U1-U5 e 16 de U6. GND: pino 7 de U1-U5 e 8 de U6. Lista: 6 CIs, 19 LEDs, 21 resistores, 6 capacitores, 2 trimpots, 2 botoes.", "7pt", "#444444")

    # ---- bloco 9: pontos de teste --------------------------------------------
    f.moldura(1950, 700, 720, 190, "9. Pontos de teste (Keystone 5011) - X, A, B, R, FALHA, IGUAL, DIFERENTE, H, S e carry final")
    nomes = ["X0", "X1", "X2", "X3", "B0", "B1", "P0", "P1", "FALHA", "DIFERENTE", "IGUAL", "H", "S0", "S1", "S2", "S3", "C_OUT"]
    for k, nome in enumerate(nomes):
        f.ponto_teste(1975 + (k % 6) * 118, 745 + (k // 6) * 45, nome)
    f.texto(1970, 880, "A1 A0 = X1 X0 (mesmos nos). Na protoboard, cada TP e um furo livre da tira do sinal.", "7pt", "#444444")
    return f


# ================================================================ folha 2
def bits(v, n):
    return [(v >> i) & 1 for i in range(n - 1, -1, -1)]


def notas():
    L = []
    L += ["1. VALIDACAO DE X -> FALHA      X = N0 mod 16 = x3x2x1x0 ; A = x1x0",
          "  X | x3 x2 x1 x0 | A | FALHA"]
    for X in range(16):
        x3, x2, x1, x0 = bits(X, 4)
        L.append(f" {X:2d} |  {x3}  {x2}  {x1}  {x0} | {X % 4} |   {int(X >= 4)}")
    L += ["Canonica: FALHA = Sm(4,5,6,7,8,9,10,11,12,13,14,15)",
          "Mapa K (linhas x3x2, colunas x1x0):   00 01 11 10",
          "                                 00    0  0  0  0",
          "                                 01    1  1  1  1",
          "                                 11    1  1  1  1",
          "                                 10    1  1  1  1",
          "Dois lacos de 8 celulas (x3 = 1 e x2 = 1):  FALHA = x3 + x2   -> U2A (74HC32)",
          "x1 e x0 nao aparecem: X = 6 tem A = 2 e continua invalido.", ""]

    L += ["2. COMPARADOR A x R -> IGUAL / DIFERENTE",
          "  # | A1 A0 P1 P0 | A R | IGUAL DIF"]
    for m in range(16):
        a1, a0, p1, p0 = bits(m, 4)
        ig = int(a1 == p1 and a0 == p0)
        L.append(f" {m:2d} |  {a1}  {a0}  {p1}  {p0} | {m >> 2} {m & 3} |   {ig}    {1 - ig}")
    L += ["Canonica: IGUAL = Sm(0,5,10,15)  - mintermos isolados na diagonal do mapa K,",
          "sem laco possivel; a simplificacao vem do fatoramento:",
          "IGUAL = (A1'P1' + A1P1)(A0'P0' + A0P0) = (A1 xnor P1)(A0 xnor P0)",
          "Forma usada no circuito (74HC86 tem saida totem-pole; 74HC266 e dreno aberto):",
          "  DIFERENTE = (A1 xor P1) + (A0 xor P0)   -> U3A, U3B (74HC86) + U2B (74HC32)",
          "  IGUAL     = DIFERENTE'                  -> U1B (74HC04)", ""]

    L += ["3. HABILITACAO H",
          " FALHA IGUAL | H", "   0     0   | 0", "   0     1   | 1", "   1     0   | 0", "   1     1   | 0",
          "H = FALHA' . IGUAL                        -> U1A (74HC04) + U5A (74HC08)",
          "A1e = A1.H  A0e = A0.H  B1e = B1.H  B0e = B0.H  -> U4A..U4D (74HC08)",
          "Com H = 0 o somador recebe 0 + 0. ALARME nao entra em H (sem realimentacao).", ""]

    L += ["4. SOMADOR 74HC283 (A3 = A2 = B3 = B2 = 0, C_in = 0)",
          " A B | A1A0 B1B0 | S3 S2 S1 S0 | S | Cout"]
    for A in range(4):
        for B in range(4):
            s3, s2, s1, s0 = bits(A + B, 4)
            L.append(f" {A} {B} |  {A >> 1}{A & 1}   {B >> 1}{B & 1}  |  {s3}  {s2}  {s1}  {s0} | {A + B} |  0")
    L += ["Carry: o carry do estagio 0 (A0 = B0 = 1) entra no estagio 1; o do estagio 1",
          "entra no estagio 2 e aparece em S2 (3 + 3 = 0110). Estagios 2 e 3 recebem 0 + 0,",
          "logo S3 = Cout = 0 nesta faixa. Por isso S2 precisa ser preservado.", ""]

    L += ["5. LEDS DE STATUS   EXCESSO = S3 + S2 (total > 3)",
          " FALHA IGUAL EXCESSO | CONF ALARME LIB | obs",
          "   0     0     0     |  1     0     0  | divergencia, S = 0",
          "   0     0     1     |  x     x     x  | impossivel: H = 0 => S = 0",
          "   0     1     0     |  0     0     1  | carga de 0 a 3 pecas",
          "   0     1     1     |  0     1     0  | 4 a 6 pecas, dividir ciclo",
          "   1     0     0     |  0     1     0  | codigo invalido",
          "   1     0     1     |  x     x     x  | impossivel",
          "   1     1     0     |  0     1     0  | invalido prevalece",
          "   1     1     1     |  x     x     x  | impossivel",
          "CONFERIR = FALHA'.DIFERENTE  -> U5B     ALARME = FALHA + EXCESSO -> U2D",
          "LIBERADO = H.EXCESSO'        -> U5C     (U1C gera nEXCESSO, U2C gera EXCESSO)",
          "Exatamente um dos tres LEDs aceso em qualquer combinacao possivel.", ""]

    L += ["6. REGISTRO DE TESTES (preencher no prototipo; esperado conforme modelagem)",
          "Bloco: aquisicao (pot min/meio/max, LEDs = serial, 10 digitos)  obtido: ____",
          "Bloco: validacao, 16 codigos de X (FALHA = 1 para X >= 4)        obtido: ____",
          "Bloco: comparador, 16 pares A/R (IGUAL e DIFERENTE complementares) obtido: ____",
          "Bloco: somador, 16 somas com H = 1 ; bloqueio com H = 0 (S = 0)  obtido: ____",
          "Integracao (N0 N1 via TESTE, R nos botoes):",
          "  # |  N0  N1 |  X A B |  R | H | S | CON AL LIB | obtido | OK"]
    casos = [(0, 0, "00"), (1, 1, "00"), (2, 1, "10"), (2, 2, "10"), (2, 3, "10"), (3, 3, "11"),
             (2, 1, "00"), (6, 1, "10"), (15, 3, "11"), (16, 1, "00"), (18, 5, "10"), (2, 6, "10")]
    for i, (n0, n1, r) in enumerate(casos, 1):
        X, A, B = n0 % 16, n0 % 4, n1 % 4
        falha = X >= 4
        igual = A == int(r, 2)
        h = int(not falha and igual)
        s = (A + B) * h
        exc = s >= 4
        con, al, lib = int(not falha and not igual), int(falha or exc), int(h and not exc)
        L.append(f" {i:2d} | {n0:3d} {n1:3d} | {X:2d} {A} {B} | {r} | {h} | {s} |  {con}   {al}   {lib}  | ______ | __")
    L += ["Sequencia com potenciometros (item 2.6): X = 2 -> P1 pressionado (R = 10) -> B = 1: S = 3,",
          "LIBERADO -> B = 2: S = 4, ALARME e S visivel -> solta P1: S = 0, CONFERIR -> X = 6: ALARME.",
          "Transicoes breves (ADC, atualizacao sequencial dos pinos, contato dos botoes) sao",
          "aceitas: a avaliacao considera as saidas estabilizadas."]
    return L


def folha_notas():
    linhas = notas()
    f = Folha(1200, 900)
    f.texto(30, 30, "Trabalho AP1 - Sistemas Digitais 2026.2 - Turma 6a - Folha 2/4: notas de modelagem (etapa 1) e registro de testes", "14pt", peso="bold")
    f.texto(30, 48, f"Integrantes: {INTEGRANTES}", "9pt")
    # secoes em colunas
    secoes, atual = [], []
    for s in linhas:
        atual.append(s)
        if s == "":
            secoes.append(atual)
            atual = []
    secoes.append(atual)
    col, y, passo, topo, fundo = 0, 80, 11.5, 80, f.h - 20
    for sec in secoes:
        if y + len(sec) * passo > fundo:
            col, y = col + 1, topo
        assert 30 + col * 560 + 560 <= f.w, "notas nao cabem na folha: aumente a altura"
        for s in sec:
            if s:
                f.texto(30 + col * 560, y, s, "8pt", fam="Courier New")
            y += passo
    return f


# ================================================================ folha 3
MEGA_PINO = {**{str(22 + b): f"N0_{b}" for b in range(10)}, "32": "B_0", "33": "B_1",
             "A0": "A0_CURSOR", "A1": "A1_CURSOR", "5V": "VCC", "GND.": "GND"}   # pino do simbolo MEGA -> net


def folha_montagem():
    """O circuito da folha 1 redesenhado como diagrama de montagem: o Arduino (simbolo da biblioteca
    de usuarios do EasyEDA) no centro e pecas genericas da Commons Library em volta, ligadas por fios."""
    f = Folha(2400, 780)
    f.bom = False                                    # BOM e PCB vem da folha 1
    f.texto(30, 30, "Trabalho AP1 - Sistemas Digitais 2026.2 - Turma 6a - Folha 3/4: montagem - Arduino Mega 2560 com pecas da Commons Library do EasyEDA", "14pt", peso="bold")
    f.texto(30, 48, f"Integrantes: {INTEGRANTES}     Prof. Clayton J A Silva", "9pt")
    f.texto(30, 64, "Mesma fiacao da folha 1 (gerar_netlist.py) com os simbolos genericos do painel Commons Library (R_AXIAL, R_3386P, C_RAD, LED-TH-5mm, K4-6x6) e o Arduino da biblioteca de usuarios. As pecas desta folha ficam fora da BOM e da PCB.", "8pt", "#444444")

    # ---- Arduino no centro: 5 V e GND por bandeira, trimpots nos analogicos, D22-D33 nos LEDs
    mx, my = 340, 340
    m, sm = f.lib("M1", "MEGA", mx, my, "Arduino Mega 2560", pos_val=(mx + 40, my - 226))
    f.toco_flag(m["5V"], sm.fora("5V"), "VCC")
    f.toco_flag(m["GND."], sm.fora("GND."), "GND")
    for rv, pino, (ox, oy) in (("RV1", "A0", (mx - 240, my - 70)), ("RV2", "A1", (mx - 160, my - 10))):
        q, s = f.lib(rv, "TRIMPOT", ox, oy, VALOR[rv])          # cursor (pino 2) sobe ate a linha do pino analogico
        c = f.toco(q["2"], s.fora("2"))
        f.fio([c, (c[0], m[pino][1]), m[pino]])
        f.toco_flag(q["1"], s.fora("1"), "VCC")
        f.toco_flag(q["3"], s.fora("3"), "GND")
    px = mx + 100                                    # x dos pinos digitais do lado direito
    desl = [20, 30, 40, 50, 60, 70, 80, 70, 60, 50, 40, 30]   # leque: pinos a passo 10 -> fileiras a passo 40, sem cruzar
    itens = []
    for i in range(12):
        pino, ry = str(22 + i), my - 100 + 40 * i
        f.fio([m[pino], (px + desl[i], m[pino][1]), (px + desl[i], ry), (px + 100, ry)])
        itens.append((NOME[MEGA_PINO[pino]], f"R{i + 1}", f"D{i + 1}", "LED_5MM_VM"))
    f.banco_leds(px + 160, my - 100, 40, itens, "R_AXIAL", led_valor=True)
    f.texto(50, 730, "N0 = analogRead(A0) em D22-D31 e B = N1 mod 4 em D32-D33: um LED por bit, 2,2 k em serie. X = N0 mod 16 = x3x2x1x0, A = x1x0.", "8pt", "#444444")

    # ---- logica: os seis CIs (caixas DIP da LCSC; a Commons Library nao tem portas) com rotulos de net
    for i, des in enumerate(("U1", "U2", "U3", "U4", "U5", "U6")):
        x, y = 960 + i * 250, 230
        q, s = f.lib(des, DEV[des], x, y, DEV[des])
        f.pinos_rotulados(des, q, s)
    f.texto(840, 100, "Logica (blocos 2, 4, 5, 6 e 7 da folha 1): rotulos iguais ligam-se entre si e com as fileiras dos LEDs; equacoes por porta na folha 1.", "8pt", "#444444")

    # ---- botoes R = P1P0 (1-2 = 5 V, 3-4 = sinal com pull-down de 10 k)
    for i, (sw, rpd) in enumerate((("SW2", "Rpd2"), ("SW1", "Rpd1"))):
        x, y = 940 + i * 220, 555
        q, s = f.lib(sw, "BOTAO_6X6", x, y, "tatil 6x6", pos_des=(x - 10, y - 20))
        a, b = f.toco(q["2"], s.fora("2"), ln=15), f.toco(q["1"], s.fora("1"), ln=15)
        f.fio([a, b])
        f.flag("VCC", *a)
        a, b = f.toco(q["4"], s.fora("4"), ln=15), f.toco(q["3"], s.fora("3"), ln=15)
        f.fio([a, b])
        no = f.toco(a, (1, 0), NOME.get(NET[sw]["3"], NET[sw]["3"]))
        r, sr = f.lib(rpd, "R_AXIAL", no[0] + 40, no[1] + 45, VALOR[rpd])
        f.fio([no, (no[0], no[1] + 45), r["1"]])
        f.toco_flag(r["2"], sr.fora("2"), "GND")
    f.texto(880, 500, "Botoes (bloco 3): solto = 0 pelo pull-down, pressionado = 1.", "8pt", "#444444")

    # ---- LEDs de status e da soma, capacitores de desacoplamento
    f.banco_leds(1480, 520, 40, [("CONFERIR", "R17", "D17", "LED_5MM_VM"), ("ALARME", "R18", "D18", "LED_5MM_VM"),
                                  ("LIBERADO", "R19", "D19", "LED_5MM_VD")], "R_AXIAL", led_valor=True)
    f.texto(1400, 500, "Status: exatamente um aceso.", "8pt", "#444444")
    f.banco_leds(1780, 520, 40, [(f"S{k}", f"R{13 + k}", f"D{13 + k}", "LED_5MM_VM") for k in range(4)], "R_AXIAL", led_valor=True)
    f.texto(1700, 500, "Soma S3..S0 (U6).", "8pt", "#444444")
    for n in range(1, 7):
        x, y = 2020 + ((n - 1) % 3) * 120, 540 + ((n - 1) // 3) * 80
        q, s = f.lib(f"C{n}", "C_RAD", x, y, VALOR[f"C{n}"])
        f.toco_flag(q["1"], s.fora("1"), "GND")
        f.toco_flag(q["2"], s.fora("2"), "VCC")
        f.texto(x + 14, y + 46, f"U{n}", "7pt", "#444444")
    f.texto(1980, 500, "100 nF junto ao VCC de cada CI.", "8pt", "#444444")
    return f


def main():
    import gerar_protoboard                     # importa aqui: ele depende deste modulo
    folhas = [(folha_esquema(), "1 - Esquema", "conferencia_carga.svg"),
              (folha_notas(), "2 - Notas de modelagem e testes", "conferencia_carga_notas.svg"),
              (folha_montagem(), "3 - Montagem (Commons Library)", "conferencia_carga_montagem.svg"),
              (gerar_protoboard.folha(), "4 - Montagem em protoboard", "conferencia_carga_protoboard.svg")]
    projeto = {"editorVersion": "6.5.57", "docType": "5", "title": "AP1 Conferencia de carga",
               "description": "Sistemas Digitais 2026.2 - turma 6a", "colors": {},
               "schematics": [f.folha_json(titulo) for f, titulo, _ in folhas]}
    (AQUI / "conferencia_carga.json").write_text(json.dumps(projeto, ensure_ascii=False, indent=1), encoding="utf-8")
    for f, _, svg in folhas[:3]:
        (AQUI / svg).write_text(f.svg_texto(), encoding="utf-8")
    gerar_protoboard.main()                     # grava o SVG da folha 4, o PNG e a lista de montagem
    # um SVG por pagina -> PDF unico com as quatro folhas
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o", str(AQUI / "conferencia_carga.pdf"), *(str(AQUI / svg) for _, _, svg in folhas)], check=True)
    print("; ".join(f"folha {k + 1}: {len(f.shape)} elementos" for k, (f, _, _) in enumerate(folhas)) + f"; {folhas[0][0].tp} pontos de teste")


if __name__ == "__main__":
    main()
