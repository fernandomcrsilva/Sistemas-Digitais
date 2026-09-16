#!/usr/bin/env python3
"""Gera o netlist .json da extensao oficial eext-generate-schematic-from-netlist
(EasyEDA Pro) a partir da fiacao descrita em esquema/README.md.

Uso:  python3 gerar_netlist.py > netlist.json

A extensao localiza cada componente por 'Supplier Part' (codigo LCSC) e, se
vazio, cai para uma busca por DeviceName na biblioteca do sistema. Os CIs sao
encontrados pelo nome; para os passivos preencha LCSC abaixo com o codigo que
voce escolher na propria biblioteca do EasyEDA.
"""
import json

# Preencha com os codigos LCSC dos passivos que voce usar no protoboard.
LCSC = {
    "R2K2": "", "R10K": "", "C100N": "",
    "LED": "", "LED_AM": "", "LED_VM": "", "LED_VD": "",
    "POT10K": "", "BOTAO": "",
}

comps = []           # (Designator, DeviceName, value, lcsc_key, {pino: net})


def add(des, dev, val, lcsc, pins):
    comps.append((des, dev, val, lcsc, pins))


# ---------------------------------------------------------------- passivos
def led(des_led, des_res, entrada, lcsc_led="LED"):
    """entrada -> resistor -> anodo | catodo -> GND."""
    anodo = f"LA_{des_led}"
    add(des_res, "", "2.2k", "R2K2", {"1": entrada, "2": anodo})
    add(des_led, "", "", lcsc_led, {"1": anodo, "2": "GND"})


# potenciometros: 1 = 5V, 2 = cursor, 3 = GND
add("RV1", "", "10k", "POT10K", {"1": "VCC", "2": "A0_CURSOR", "3": "GND"})
add("RV2", "", "10k", "POT10K", {"1": "VCC", "2": "A1_CURSOR", "3": "GND"})

# push-buttons tateis 6x6 de 4 pinos (1-2 e 3-4 ligados internamente) entre 5 V e o
# sinal, com pull-down de 10k
for n, sinal in ((1, "P0"), (2, "P1")):
    add(f"SW{n}", "", "", "BOTAO", {"1": "VCC", "2": "VCC", "3": sinal, "4": sinal})
    add(f"Rpd{n}", "", "10k", "R10K", {"1": sinal, "2": "GND"})

# ------------------------------------------------------------------- CIs
# 74HC08/32/86 partilham a pinagem DIP-14: 1,2->3  4,5->6  9,10->8  12,13->11
def quad(des, dev, portas):
    """portas: lista de 4 tuplas (a, b, y); use None para porta nao usada."""
    mapa = [("1", "2", "3"), ("4", "5", "6"), ("9", "10", "8"), ("12", "13", "11")]
    pins = {"7": "GND", "14": "VCC"}
    for (pa, pb, py), porta in zip(mapa, portas):
        if porta is None:                       # entradas ociosas em nivel fixo
            pins[pa] = pins[pb] = "GND"
        else:
            a, b, y = porta
            pins[pa], pins[pb], pins[py] = a, b, y
    add(des, dev, "", "", pins)


# U1 74HC04 hex inversor: 1->2, 3->4, 5->6; 9/11/13 ociosas ao GND
add("U1", "74HC04", "", "", {
    "1": "FALHA", "2": "nFALHA",
    "3": "DIFERENTE", "4": "IGUAL",
    "5": "EXCESSO", "6": "nEXCESSO",
    "9": "GND", "11": "GND", "13": "GND",
    "7": "GND", "14": "VCC",
})

quad("U2", "74HC32", [
    ("N0_3", "N0_2", "FALHA"),   # x3 + x2
    ("d1", "d0", "DIFERENTE"),
    ("S3", "S2", "EXCESSO"),
    ("FALHA", "EXCESSO", "ALARME"),
])

quad("U3", "74HC86", [
    ("N0_1", "P1", "d1"),        # A1 XOR P1
    ("N0_0", "P0", "d0"),        # A0 XOR P0
    None, None,
])

quad("U4", "74HC08", [           # habilitacao dos operandos
    ("N0_1", "H", "Ae1"),
    ("N0_0", "H", "Ae0"),
    ("B_1", "H", "Be1"),
    ("B_0", "H", "Be0"),
])

quad("U5", "74HC08", [           # H e LEDs de status
    ("nFALHA", "IGUAL", "H"),
    ("nFALHA", "DIFERENTE", "CONFERIR"),
    ("H", "nEXCESSO", "LIBERADO"),
    None,
])

# U6 74HC283: indice 1 do datasheet e o LSB
add("U6", "74HC283", "", "", {
    "5": "Ae0", "6": "Be0", "4": "S0",       # estagio 0
    "3": "Ae1", "2": "Be1", "1": "S1",       # estagio 1
    "14": "GND", "15": "GND", "13": "S2",    # estagio 2: operandos em 0
    "12": "GND", "11": "GND", "10": "S3",    # estagio 3: operandos em 0
    "7": "GND",                              # C_in
    "9": "COUT",                             # carry final -> ponto de teste
    "8": "GND", "16": "VCC",
})

# ------------------------------------------------------------------ LEDs
for b in range(10):                                   # 10 LEDs de N0
    led(f"D{b + 1}", f"R{b + 1}", f"N0_{b}")
led("D11", "R11", "B_0")                              # 2 LEDs de B
led("D12", "R12", "B_1")
for b in range(4):                                    # 4 LEDs da soma
    led(f"D{13 + b}", f"R{13 + b}", f"S{b}")
led("D17", "R17", "CONFERIR", "LED_AM")               # 3 de status
led("D18", "R18", "ALARME", "LED_VM")
led("D19", "R19", "LIBERADO", "LED_VD")

# ------------------------------------------------------- desacoplamento
for n in range(1, 7):                                  # pino 2 em cima no simbolo LCSC: fica no VCC
    add(f"C{n}", "", "100nF", "C100N", {"1": "GND", "2": "VCC"})

# ------------------------------------------------------------- validacao
uso = {}
for des, _, _, _, pins in comps:
    for pino, net in pins.items():
        uso.setdefault(net, []).append(f"{des}.{pino}")

# Um ponto so: nets que o Arduino fecha depois da importacao, mais o carry
# final, que por especificacao vai apenas a um ponto de teste.
pontas_livres = ({f"N0_{b}" for b in range(4, 10)}
                 | {"A0_CURSOR", "A1_CURSOR", "COUT"})
for net, pontos in sorted(uso.items()):
    if len(pontos) < 2 and net not in pontas_livres:
        raise SystemExit(f"net solto: {net} -> {pontos}")

netlist = {
    f"gge{i}": {
        "props": {
            "Designator": des,
            "DeviceName": dev,
            "value": val,
            "Supplier Part": LCSC.get(lcsc, ""),
        },
        "pins": pins,
    }
    for i, (des, dev, val, lcsc, pins) in enumerate(comps, start=1)
}
if __name__ == "__main__":
    print(json.dumps(netlist, indent=2, ensure_ascii=False))
