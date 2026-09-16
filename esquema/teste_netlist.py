#!/usr/bin/env python3
"""Simula o circuito da netlist (gerar_netlist.py) porta a porta - 74HC04, 74HC08,
74HC32, 74HC86 e o somador 74HC283 - e confere contra o plano de testes
(docs/03-plano-de-testes.md): FALHA para os 16 codigos de X, IGUAL/DIFERENTE
para os 16 pares A/R, as 16 somas com H = 1, o bloqueio com H = 0 e os 12
casos de integracao. Testa a fiacao desenhada, nao so as equacoes.

Uso:  python3 esquema/teste_netlist.py     ->  termina com "teste_netlist: OK"
"""
from gerar_netlist import comps

NET = {des: pins for des, _, _, _, pins in comps}
DEV = {des: dev for des, dev, _, _, _ in comps}
QUAD = [("1", "2", "3"), ("4", "5", "6"), ("9", "10", "8"), ("12", "13", "11")]   # DIP-14 de 2 entradas
HEX = [("1", "2"), ("3", "4"), ("5", "6"), ("9", "8"), ("11", "10"), ("13", "12")]  # 74HC04
FUNC = {"74HC08": lambda a, b: a & b, "74HC32": lambda a, b: a | b, "74HC86": lambda a, b: a ^ b}


def simular(n0, n1, p1, p0):
    """Devolve o estado dos sinais e dos LEDs para um par N0/N1 e os botoes P1 P0."""
    v = {"VCC": 1, "GND": 0, "P1": p1, "P0": p0}          # o que o Mega e os botoes impoem
    for b in range(10):
        v[f"N0_{b}"] = (n0 >> b) & 1
    v["B_0"], v["B_1"] = n1 & 1, (n1 >> 1) & 1
    g = lambda net: v.get(net, 0)
    for _ in range(20):                                    # combinacional: converge em poucas voltas
        antes = dict(v)
        for des, pins in NET.items():
            dev = DEV[des]
            if dev in FUNC:
                for a, b, y in QUAD:
                    if y in pins:
                        v[pins[y]] = FUNC[dev](g(pins[a]), g(pins[b]))
            elif dev == "74HC04":
                for a, y in HEX:
                    if y in pins:
                        v[pins[y]] = 1 - g(pins[a])
            elif dev == "74HC283":                         # indice 1 do datasheet = LSB
                A = sum(g(pins[p]) << i for i, p in enumerate(("5", "3", "14", "12")))
                B = sum(g(pins[p]) << i for i, p in enumerate(("6", "2", "15", "11")))
                s = A + B + g(pins["7"])
                for i, p in enumerate(("4", "1", "13", "10")):
                    v[pins[p]] = (s >> i) & 1
                v[pins["9"]] = (s >> 4) & 1
        if v == antes:
            break
    else:
        raise SystemExit("o circuito nao estabilizou (realimentacao?)")
    led = lambda d: g(NET["R" + d[1:]]["1"])              # LED aceso = nivel alto na entrada do seu resistor
    return dict(FALHA=g("FALHA"), IGUAL=g("IGUAL"), DIFERENTE=g("DIFERENTE"), H=g("H"), COUT=g("COUT"),
                S=sum(led(f"D{13 + i}") << i for i in range(4)),
                CON=led("D17"), AL=led("D18"), LIB=led("D19"),
                N0=sum(led(f"D{b + 1}") << b for b in range(10)), B=led("D11") | led("D12") << 1)


def esperado(n0, n1, r):
    """Modelo do enunciado, independente da fiacao."""
    X, A, B = n0 % 16, n0 % 4, n1 % 4
    falha, igual = int(X >= 4), int(A == r)
    h = int(not falha and igual)
    s = (A + B) * h
    exc = int(s >= 4)
    return dict(FALHA=falha, IGUAL=igual, DIFERENTE=1 - igual, H=h, S=s, COUT=0,
                CON=int(not falha and not igual), AL=int(falha or exc), LIB=int(h and not exc))


def confere(n0, n1, r, extra=None):
    obtido = simular(n0, n1, r >> 1, r & 1)
    esp = esperado(n0, n1, r)
    esp.update(extra or {})
    erros = {k: (obtido[k], e) for k, e in esp.items() if obtido[k] != e}
    assert not erros, f"N0={n0} N1={n1} R={r:02b}: obtido != esperado em {erros}"
    return obtido


if __name__ == "__main__":
    for X in range(16):                                    # 2.2 validacao: FALHA = 1 para X >= 4
        assert confere(X, 0, 0)["FALHA"] == int(X >= 4)
    for A in range(4):                                     # 2.3 comparador: 16 pares A/R, saidas complementares
        for r in range(4):
            o = confere(A, 0, r)
            assert o["IGUAL"] == int(A == r) and o["DIFERENTE"] == 1 - o["IGUAL"]
    for A in range(4):                                     # 2.4 somador: 16 somas com R = A (H = 1)
        for B in range(4):
            o = confere(A, B, A)
            assert o["H"] == 1 and o["S"] == A + B and o["COUT"] == 0
    for A in range(4):                                     # 2.5 bloqueio: H = 0 -> S = 0 seja qual for B
        for B in range(4):
            assert confere(A, B, (A + 1) % 4)["S"] == 0 and confere(A + 4, B, A)["S"] == 0
    casos = [(0, 0, 0b00), (1, 1, 0b00), (2, 1, 0b10), (2, 2, 0b10), (2, 3, 0b10), (3, 3, 0b11),   # 3. integracao
             (2, 1, 0b00), (6, 1, 0b10), (15, 3, 0b11), (16, 1, 0b00), (18, 5, 0b10), (2, 6, 0b10)]
    tabela = [(1, 0, 0, 0, 1), (0, 0, 1, 0, 0), (1, 3, 0, 0, 1), (1, 4, 0, 1, 0), (1, 5, 0, 1, 0), (1, 6, 0, 1, 0),
              (0, 0, 1, 0, 0), (0, 0, 0, 1, 0), (0, 0, 0, 1, 0), (1, 1, 0, 0, 1), (1, 3, 0, 0, 1), (1, 4, 0, 1, 0)]
    for (n0, n1, r), (h, s, con, al, lib) in zip(casos, tabela):
        confere(n0, n1, r, dict(H=h, S=s, CON=con, AL=al, LIB=lib))
    for n0 in range(0, 1024, 37):                          # varredura: LEDs de N0/B espelham o par; um so LED de status
        for n1 in range(0, 1024, 41):
            for r in range(4):
                o = confere(n0, n1, r)
                assert o["N0"] == n0 and o["B"] == n1 % 4 and o["CON"] + o["AL"] + o["LIB"] == 1
    print("teste_netlist: OK")
