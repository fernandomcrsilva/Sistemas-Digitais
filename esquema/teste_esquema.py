#!/usr/bin/env python3
"""Extrai a conectividade das folhas 1 e 3 de conferencia_carga.json do jeito que o
EasyEDA faz (fios que se tocam, pinos sobre fios, rotulos de net e bandeiras VCC/GND)
e confere pino a pino contra a netlist de gerar_netlist.py. Pega toco que nao encosta
no pino, rotulo errado, curto e pino esquecido.

Uso:  python3 esquema/teste_esquema.py   ->  termina com "teste_esquema: OK"
"""
import json
from pathlib import Path

from gerar_netlist import comps
from gerar_esquema import NOME, MEGA_PINO

NET = {des: pins for des, _, _, _, pins in comps}
EPS = 0.01


def sobre(p, a, b):
    """p esta no segmento a-b?"""
    (px, py), (ax, ay), (bx, by) = p, a, b
    if abs((bx - ax) * (py - ay) - (by - ay) * (px - ax)) > EPS * max(1, abs(bx - ax) + abs(by - ay)):
        return False
    return min(ax, bx) - EPS <= px <= max(ax, bx) + EPS and min(ay, by) - EPS <= py <= max(ay, by) + EPS


class Uniao:
    def __init__(self):
        self.pai = {}

    def achar(self, a):
        self.pai.setdefault(a, a)
        while self.pai[a] != a:
            self.pai[a] = self.pai[self.pai[a]]
            a = self.pai[a]
        return a

    def unir(self, a, b):
        self.pai[self.achar(a)] = self.achar(b)


def conectividade(shapes):
    """Ilhas de conexao da folha, com as regras do EasyEDA: fio liga em fio ou pino so pelas
    pontas; encostar no meio de um fio exige ponto de juncao (J); a juncao liga tudo que
    passa por ela; rotulo e bandeira ligam onde encostam."""
    fios, pinos, rotulos, juncoes = [], [], [], []      # (id, [pontos]) ; (id, ponto) ; (nome, ponto) ; ponto
    for sh in shapes:
        t = sh.split("~")[0]
        if t == "W":
            v = [float(x) for x in sh.split("~")[1].split()]
            fios.append((f"W{len(fios)}", list(zip(v[::2], v[1::2]))))
        elif t == "J":
            c = sh.split("~")
            juncoes.append((float(c[1]), float(c[2])))
        elif t == "N":
            c = sh.split("~")
            rotulos.append((c[5], (float(c[1]), float(c[2]))))
        elif t == "F":
            seg = sh.split("^^")
            c = seg[0].split("~")
            rotulos.append((seg[2].split("~")[0], (float(c[2]), float(c[3]))))
        elif t == "LIB":
            partes = sh.split("#@$")
            des = next(p.split("~")[12] for p in partes if p.startswith("T~P~"))
            for p in partes:
                if p.startswith("P~"):
                    c = p.split("^^")[0].split("~")
                    pinos.append(((des, c[3]), (float(c[4]), float(c[5]))))
    u = Uniao()
    for fid, pts in fios:                       # fio: uma so ilha
        for k in range(len(pts)):
            u.unir(fid, (fid, k))

    def mesmo(a, b):
        return abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS

    def toca(ponto, meio=False):
        """Ids dos fios/pinos que o ponto encosta; meio=True aceita o meio de um fio."""
        j = meio or any(mesmo(ponto, jp) for jp in juncoes)
        ids = []
        for fid, pts in fios:
            if mesmo(ponto, pts[0]) or mesmo(ponto, pts[-1]) or \
               (j and any(sobre(ponto, pts[k], pts[k + 1]) for k in range(len(pts) - 1))):
                ids.append(fid)
        ids += [pid for pid, pt in pinos if mesmo(pt, ponto)]
        return ids

    for fid, pts in fios:                       # ponta de fio em fio ou em pino
        for pt in (pts[0], pts[-1]):
            for outro in toca(pt):
                u.unir(fid, outro)
    for pid, pt in pinos:                       # pino em ponta de fio (ou no meio, com juncao)
        for outro in toca(pt):
            u.unir(pid, outro)
    for jp in juncoes:                          # juncao liga tudo que passa por ela
        ids = toca(jp, meio=True)
        for outro in ids[1:]:
            u.unir(ids[0], outro)
    for nome, pt in rotulos:
        for outro in toca(pt, meio=True):
            u.unir(("NET", nome), outro)
    grupos = {}
    for pid, _ in pinos:
        grupos.setdefault(u.achar(pid), {"pinos": set(), "nomes": set()})["pinos"].add(pid)
    for nome, _ in rotulos:
        r = u.achar(("NET", nome))
        if r in grupos:
            grupos[r]["nomes"].add(nome)
    return grupos, {pid for pid, _ in pinos}


def lint(shapes):
    """Defeitos geometricos que o EasyEDA aceita mas enganam quem le: ponta de fio (ou pino) no
    meio de outro fio sem ponto de juncao, fios sobrepostos no mesmo trecho, fio atravessando o
    corpo de um simbolo, ponta de fio solta e juncao fora de fio."""
    fios, juncoes, pinos, pontos_rot, corpos = [], [], [], [], []
    for sh in shapes:
        t = sh.split("~")[0]
        if t == "W":
            v = [float(x) for x in sh.split("~")[1].split()]
            fios.append(list(zip(v[::2], v[1::2])))
        elif t == "J":
            c = sh.split("~")
            juncoes.append((float(c[1]), float(c[2])))
        elif t == "N":
            c = sh.split("~")
            pontos_rot.append((float(c[1]), float(c[2])))
        elif t == "F":
            c = sh.split("^^")[0].split("~")
            pontos_rot.append((float(c[2]), float(c[3])))
        elif t == "LIB":
            partes = sh.split("#@$")
            des = next(p.split("~")[12] for p in partes if p.startswith("T~P~"))
            xs, ys = [], []
            for p in partes[1:]:
                k = p.split("~")[0]
                if k == "P":
                    c = p.split("^^")[0].split("~")
                    pinos.append((des, c[3], (float(c[4]), float(c[5]))))
                elif k == "R":
                    c = p.split("~")
                    xs += [float(c[1]), float(c[1]) + float(c[5])]
                    ys += [float(c[2]), float(c[2]) + float(c[6])]
                elif k in ("PL", "PG"):
                    v = [float(x) for x in p.split("~")[1].split()]
                    xs += v[::2]
                    ys += v[1::2]
                elif k == "E":
                    c = p.split("~")
                    xs += [float(c[1]) - float(c[3]), float(c[1]) + float(c[3])]
                    ys += [float(c[2]) - float(c[4]), float(c[2]) + float(c[4])]
            if xs:
                corpos.append((des, min(xs), min(ys), max(xs), max(ys)))

    def mesmo(a, b):
        return abs(a[0] - b[0]) < EPS and abs(a[1] - b[1]) < EPS

    def no_meio(p, pts):
        return any(sobre(p, pts[k], pts[k + 1]) for k in range(len(pts) - 1)) and not mesmo(p, pts[0]) and not mesmo(p, pts[-1])

    def em_juncao(p):
        return any(mesmo(p, j) for j in juncoes)

    def toca_ponta(p, i):
        return any(mesmo(p, f[0]) or mesmo(p, f[-1]) for k, f in enumerate(fios) if k != i)

    erros = []
    for i, f in enumerate(fios):
        for p in (f[0], f[-1]):
            if any(no_meio(p, g) for k, g in enumerate(fios) if k != i) and not em_juncao(p):
                erros.append(f"ponta de fio no meio de outro sem juncao em {p}")
            preso = toca_ponta(p, i) or em_juncao(p) or any(mesmo(p, q) for _, _, q in pinos) or any(mesmo(p, q) for q in pontos_rot)
            if not preso:
                erros.append(f"ponta de fio solta em {p}")
    for des, num, p in pinos:
        if any(no_meio(p, g) for g in fios) and not em_juncao(p):
            erros.append(f"pino {des}.{num} no meio de um fio sem juncao em {p}")
    for j in juncoes:
        if not any(any(sobre(j, f[k], f[k + 1]) for k in range(len(f) - 1)) for f in fios):
            erros.append(f"juncao fora de fio em {j}")
    segs = [(i, f[k], f[k + 1]) for i, f in enumerate(fios) for k in range(len(f) - 1)]
    for a in range(len(segs)):
        ia, p1, p2 = segs[a]
        for b in range(a + 1, len(segs)):
            ib, q1, q2 = segs[b]
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            if abs(dx * (q1[1] - p1[1]) - dy * (q1[0] - p1[0])) > EPS or abs(dx * (q2[1] - p1[1]) - dy * (q2[0] - p1[0])) > EPS:
                continue                                    # nao colineares
            ln = dx * dx + dy * dy
            t1 = ((q1[0] - p1[0]) * dx + (q1[1] - p1[1]) * dy) / ln
            t2 = ((q2[0] - p1[0]) * dx + (q2[1] - p1[1]) * dy) / ln
            if min(max(t1, t2), 1) - max(min(t1, t2), 0) > EPS:
                erros.append(f"fios sobrepostos entre {p1}-{p2} e {q1}-{q2}")
    for des, x0, y0, x1, y1 in corpos:
        for f in fios:
            for k in range(len(f) - 1):
                (ax, ay), (bx, by) = f[k], f[k + 1]
                if max(min(ax, bx), x0) + EPS < min(max(ax, bx), x1) and max(min(ay, by), y0) + EPS < min(max(ay, by), y1):
                    if ax == bx or ay == by:                # fio ortogonal entrando no retangulo do corpo
                        erros.append(f"fio {f[k]}-{f[k + 1]} atravessa o corpo de {des}")
    return sorted(set(erros))


MEGA1 = {f"D{22 + b}": f"N0_{b}" for b in range(10)}          # caixa desenhada da folha 1 (pinos com nome)
MEGA1.update({"D32": "B_0", "D33": "B_1", "A0": "A0_CURSOR", "A1": "A1_CURSOR", "5V": "VCC", "GND": "GND"})


def verificar(shapes, mega, ignorar=()):
    """Confere uma folha contra a netlist; `mega` mapeia pino do simbolo do Arduino -> net."""
    grupos, presentes = conectividade(shapes)
    esperado = {(des, num): net for des, pins in NET.items() for num, net in pins.items()}
    esperado.update({("M1", nome): net for nome, net in mega.items()})
    faltam = [p for p in esperado if p not in presentes]
    assert not faltam, f"pinos da netlist ausentes no esquema: {faltam}"
    for p in ignorar:
        esperado.pop(p)
    por_net = {}
    for pino, net in esperado.items():
        por_net.setdefault(net, set()).add(pino)
    erros = []
    for net, pins in por_net.items():
        raizes = {r for r, g in grupos.items() if g["pinos"] & pins}
        if len(raizes) != 1:
            ilhas = [sorted(grupos[r]["pinos"] & pins) for r in raizes]
            erros.append(f"{net}: pinos em {len(raizes)} ilhas: {sorted(ilhas, key=len)[:-1]} separados do resto")
            continue
        g = grupos[raizes.pop()]
        intrusos = {p for p in g["pinos"] if p in esperado and esperado[p] != net}
        if intrusos:
            erros.append(f"{net}: em curto com {sorted(intrusos)}")
        nomes = {n for n in g["nomes"]}
        if nomes and nomes != {NOME.get(net, net)}:
            erros.append(f"{net}: rotulos {sorted(nomes)}")
    assert not erros, "\n".join(erros)
    tps = [p for p in presentes if p[0].startswith("TP")]
    for tp in tps:                              # cada ponto de teste ligado a exatamente uma net com nome
        r = next(r for r, g in grupos.items() if tp in g["pinos"])
        assert len(grupos[r]["nomes"]) == 1 and grupos[r]["pinos"] & set(esperado), f"{tp} solto"
    return len(esperado), len(por_net), len(tps)


if __name__ == "__main__":
    folhas = json.loads((Path(__file__).parent / "conferencia_carga.json").read_text(encoding="utf-8"))["schematics"]
    # folha 1: terminais 2 e 4 dos botoes tateis sao ligados internamente a 1 e 3 e ficam sem fio no desenho
    n = verificar(folhas[0]["dataStr"]["shape"], MEGA1, [(sw, p) for sw in ("SW1", "SW2") for p in ("2", "4")])
    defeitos = lint(folhas[0]["dataStr"]["shape"])
    assert not defeitos, "folha 1:\n" + "\n".join(defeitos)
    print(f"teste_esquema: folha 1 OK ({n[0]} pinos, {n[1]} nets, {n[2]} pontos de teste, sem defeitos geometricos)")
    n = verificar(folhas[2]["dataStr"]["shape"], MEGA_PINO)
    defeitos = lint(folhas[2]["dataStr"]["shape"])
    assert not defeitos, "folha 3:\n" + "\n".join(defeitos)
    print(f"teste_esquema: folha 3 OK ({n[0]} pinos, {n[1]} nets, sem defeitos geometricos)")
