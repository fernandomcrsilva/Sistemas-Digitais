# Montagem em protoboard — conferência de carga

Gerado por `gerar_protoboard.py` a partir da mesma fiação do esquema (`gerar_netlist.py`);
desenho em `conferencia_carga_protoboard.png`. Duas protoboards de 830 pontos (63 colunas;
linhas a–e acima do canal central, f–j abaixo) e o Arduino Mega fora das placas.

**Coordenadas:** `P1 c19` = placa 1, linha c, coluna 19. Os 5 furos de uma coluna do mesmo
lado do canal são um único nó, então qualquer furo livre da mesma tira serve. Os furos
indicados são os do desenho.

## 1. Alimentação

- Mega **5V** → P1 barramento + de cima (extremidade esquerda).
- Mega **GND** → P1 barramento - de cima (extremidade esquerda).
- Ponte: P1 barramento + de cima ↔ P1 barramento + de baixo (esquerda).
- Ponte: P1 barramento - de cima ↔ P1 barramento - de baixo (esquerda).
- Ponte: P1 barramento + de baixo ↔ P2 barramento + de cima (direita).
- Ponte: P1 barramento - de baixo ↔ P2 barramento - de cima (direita).
- Ponte: P2 barramento + de cima ↔ P2 barramento + de baixo (direita).
- Ponte: P2 barramento - de cima ↔ P2 barramento - de baixo (direita).
- Barramento **+** = 5 V, **−** = GND, nas duas placas. Se os barramentos forem partidos no meio (coluna 30/31), emende cada metade.

## 2. CIs na placa 2 (atravessando o canal, entalhe para a esquerda, pino 1 na linha f)

| CI | Tipo | Colunas | Pino 1 | VCC | GND |
| -- | ---- | ------- | ------ | --- | --- |
| U1 | 74HC04 | 2–8 | P2 f2 | pino 14 em P2 e2 | pino 7 em P2 f8 |
| U2 | 74HC32 | 11–17 | P2 f11 | pino 14 em P2 e11 | pino 7 em P2 f17 |
| U3 | 74HC86 | 20–26 | P2 f20 | pino 14 em P2 e20 | pino 7 em P2 f26 |
| U4 | 74HC08 | 29–35 | P2 f29 | pino 14 em P2 e29 | pino 7 em P2 f35 |
| U5 | 74HC08 | 38–44 | P2 f38 | pino 14 em P2 e38 | pino 7 em P2 f44 |
| U6 | 74HC283 | 47–54 | P2 f47 | pino 16 em P2 e47 | pino 8 em P2 f54 |

## 3. Jumpers curtos aos barramentos (+ = 5 V, − = GND)

| Furo | Barramento | Liga |
| ---- | ---------- | ---- |
| P1 j2 | − (GND) | D10 p2 |
| P1 j4 | − (GND) | D9 p2 |
| P1 j6 | − (GND) | D8 p2 |
| P1 j8 | − (GND) | D7 p2 |
| P1 j10 | − (GND) | D6 p2 |
| P1 j12 | − (GND) | D5 p2 |
| P1 j14 | − (GND) | D4 p2 |
| P1 j16 | − (GND) | D3 p2 |
| P1 j18 | − (GND) | D2 p2 |
| P1 j20 | − (GND) | D1 p2 |
| P1 j24 | − (GND) | D12 p2 |
| P1 j26 | − (GND) | D11 p2 |
| P1 a30 | − (GND) | D16 p2 |
| P1 a32 | − (GND) | D15 p2 |
| P1 a34 | − (GND) | D14 p2 |
| P1 a36 | − (GND) | D13 p2 |
| P1 a40 | − (GND) | D17 p2 |
| P1 a42 | − (GND) | D18 p2 |
| P1 a44 | − (GND) | D19 p2 |
| P1 a47 | + (5 V) | RV1 p1 |
| P1 a49 | − (GND) | RV1 p3 |
| P1 a51 | + (5 V) | RV2 p1 |
| P1 a53 | − (GND) | RV2 p3 |
| P1 a56 | + (5 V) | SW2 p1 |
| P1 a60 | + (5 V) | SW1 p1 |
| P2 j8 | − (GND) | U1 p7 |
| P2 j17 | − (GND) | U2 p7 |
| P2 j26 | − (GND) | U3 p7 |
| P2 j35 | − (GND) | U4 p7 |
| P2 j44 | − (GND) | U5 p7 |
| P2 j53 | − (GND) | U6 p7 |
| P2 j54 | − (GND) | U6 p8 |
| P2 a2 | + (5 V) | U1 p14, C1 p2 |
| P2 a3 | − (GND) | U1 p13 |
| P2 a5 | − (GND) | U1 p11 |
| P2 a7 | − (GND) | U1 p9 |
| P2 a11 | + (5 V) | U2 p14, C2 p2 |
| P2 a20 | + (5 V) | U3 p14, C3 p2 |
| P2 a21 | − (GND) | U3 p13 |
| P2 a22 | − (GND) | U3 p12 |
| P2 a24 | − (GND) | U3 p10 |
| P2 a25 | − (GND) | U3 p9 |
| P2 a29 | + (5 V) | U4 p14, C4 p2 |
| P2 a38 | + (5 V) | U5 p14, C5 p2 |
| P2 a39 | − (GND) | U5 p13 |
| P2 a40 | − (GND) | U5 p12 |
| P2 a47 | + (5 V) | U6 p16, C6 p2 |
| P2 a48 | − (GND) | U6 p15 |
| P2 a49 | − (GND) | U6 p14 |
| P2 a51 | − (GND) | U6 p12 |
| P2 a52 | − (GND) | U6 p11 |

## 4. Capacitores de 100 nF e pull-downs de 10 k (de um furo direto ao barramento −)

| Peça | Valor | De | Para |
| ---- | ----- | -- | ---- |
| C1 | 100nF | P2 b2 | P2 barramento - de cima |
| C2 | 100nF | P2 b11 | P2 barramento - de cima |
| C3 | 100nF | P2 b20 | P2 barramento - de cima |
| C4 | 100nF | P2 b29 | P2 barramento - de cima |
| C5 | 100nF | P2 b38 | P2 barramento - de cima |
| C6 | 100nF | P2 b47 | P2 barramento - de cima |
| Rpd2 | 10k | P1 j58 | P1 barramento - de baixo |
| Rpd1 | 10k | P1 j62 | P1 barramento - de baixo |

## 5. LEDs na placa 1 (resistor de 2,2 k atravessa o canal; catodo na coluna seguinte, com jumper ao −)

| LED | Sinal | Cor | Resistor | Anodo (perna longa) | Catodo (lado chato) |
| --- | ----- | --- | -------- | ------------------- | ------------------- |
| D1 | X0 | qualquer | R1: P1 e19 ↔ P1 f19 | P1 g19 | P1 g20 |
| D2 | X1 | qualquer | R2: P1 e17 ↔ P1 f17 | P1 g17 | P1 g18 |
| D3 | X2 | qualquer | R3: P1 e15 ↔ P1 f15 | P1 g15 | P1 g16 |
| D4 | X3 | qualquer | R4: P1 e13 ↔ P1 f13 | P1 g13 | P1 g14 |
| D5 | N0_4 | qualquer | R5: P1 e11 ↔ P1 f11 | P1 g11 | P1 g12 |
| D6 | N0_5 | qualquer | R6: P1 e9 ↔ P1 f9 | P1 g9 | P1 g10 |
| D7 | N0_6 | qualquer | R7: P1 e7 ↔ P1 f7 | P1 g7 | P1 g8 |
| D8 | N0_7 | qualquer | R8: P1 e5 ↔ P1 f5 | P1 g5 | P1 g6 |
| D9 | N0_8 | qualquer | R9: P1 e3 ↔ P1 f3 | P1 g3 | P1 g4 |
| D10 | N0_9 | qualquer | R10: P1 e1 ↔ P1 f1 | P1 g1 | P1 g2 |
| D12 | B1 | qualquer | R12: P1 e23 ↔ P1 f23 | P1 g23 | P1 g24 |
| D11 | B0 | qualquer | R11: P1 e25 ↔ P1 f25 | P1 g25 | P1 g26 |
| D16 | S3 | qualquer | R16: P1 f29 ↔ P1 e29 | P1 d29 | P1 d30 |
| D15 | S2 | qualquer | R15: P1 f31 ↔ P1 e31 | P1 d31 | P1 d32 |
| D14 | S1 | qualquer | R14: P1 f33 ↔ P1 e33 | P1 d33 | P1 d34 |
| D13 | S0 | qualquer | R13: P1 f35 ↔ P1 e35 | P1 d35 | P1 d36 |
| D17 | CONFERIR | amarelo | R17: P1 f39 ↔ P1 e39 | P1 d39 | P1 d40 |
| D18 | ALARME | vermelho | R18: P1 f41 ↔ P1 e41 | P1 d41 | P1 d42 |
| D19 | LIBERADO | verde | R19: P1 f43 ↔ P1 e43 | P1 d43 | P1 d44 |

## 6. Potenciômetros e botões (placa 1)

| Peça | Ligação |
| ---- | ------- |
| RV1 10k | pino 1 em P1 c47 (5 V pelo jumper) · cursor em P1 c48 → Mega A0 · pino 3 em P1 c49 (GND pelo jumper) |
| RV2 10k | pino 1 em P1 c51 (5 V pelo jumper) · cursor em P1 c52 → Mega A1 · pino 3 em P1 c53 (GND pelo jumper) |
| SW2 (tátil 4 pinos) | atravessa o canal nas colunas 56 e 58; 5 V no terminal P1 e56; sinal P1 no terminal em diagonal P1 f58; as tiras P1 t58/b56 ficam só para o botão |
| SW1 (tátil 4 pinos) | atravessa o canal nas colunas 60 e 62; 5 V no terminal P1 e60; sinal P0 no terminal em diagonal P1 f62; as tiras P1 t62/b60 ficam só para o botão |

## 7. Fios do Arduino Mega para a placa 1

| Pino do Mega | Sinal | Furo |
| ------------ | ----- | ---- |
| A0 | A0_CURSOR | P1 a48 |
| A1 | A1_CURSOR | P1 a52 |
| D32 | B0 | P1 a25 |
| D33 | B1 | P1 a23 |
| D22 | X0 | P1 a19 |
| D23 | X1 | P1 a17 |
| D24 | X2 | P1 a15 |
| D25 | X3 | P1 a13 |
| D26 | N0_4 | P1 a11 |
| D27 | N0_5 | P1 a9 |
| D28 | N0_6 | P1 a7 |
| D29 | N0_7 | P1 a5 |
| D30 | N0_8 | P1 a3 |
| D31 | N0_9 | P1 a1 |

## 8. Fios entre as placas

| Sinal | De | Para |
| ----- | -- | ---- |
| B0 | P1 b25 | P2 a31 |
| B1 | P1 b23 | P2 a34 |
| X0 | P1 b19 | P2 j23 |
| X1 | P1 b17 | P2 j20 |
| X2 | P1 b15 | P2 j12 |
| X3 | P1 b13 | P2 j11 |
| ALARME | P1 j41 | P2 a14 |
| CONFERIR | P1 j39 | P2 j43 |
| LIBERADO | P1 j43 | P2 a44 |
| P0 | P1 i62 | P2 j24 |
| P1 | P1 i58 | P2 j21 |
| S0 | P1 j35 | P2 j50 |
| S1 | P1 j33 | P2 j47 |
| S2 | P1 j31 | P2 a15 |
| S3 | P1 j29 | P2 a16 |

## 9. Fios internos da placa 2

| Sinal | De | Para |
| ----- | -- | ---- |
| A0e | P2 j34 | P2 j51 |
| A1e | P2 j31 | P2 j49 |
| B0e | P2 a32 | P2 j52 |
| B1e | P2 a35 | P2 j48 |
| DIFERENTE | P2 j4 | P2 j16 |
| DIFERENTE | P2 i16 | P2 j42 |
| EXCESSO | P2 a12 | P2 a17 |
| EXCESSO | P2 b17 | P2 j6 |
| FALHA | P2 a13 | P2 j2 |
| FALHA | P2 i2 | P2 j13 |
| H | P2 a30 | P2 a33 |
| H | P2 b33 | P2 a43 |
| H | P2 b43 | P2 j30 |
| H | P2 i30 | P2 j33 |
| H | P2 i33 | P2 j40 |
| IGUAL | P2 j5 | P2 j39 |
| S2 | P2 b15 | P2 a50 |
| S3 | P2 b16 | P2 a53 |
| X0 | P2 i23 | P2 j32 |
| X1 | P2 i20 | P2 j29 |
| d0 | P2 j15 | P2 j25 |
| d1 | P2 j14 | P2 j22 |
| nEXCESSO | P2 a42 | P2 j7 |
| nFALHA | P2 j3 | P2 j38 |
| nFALHA | P2 i38 | P2 j41 |

## 10. Pontos de teste (furo livre na tira do sinal)

| TP | Furo |
| -- | ---- |
| X3 | P1 c13 |
| X2 | P1 c15 |
| X1 | P1 c17 |
| X0 | P1 c19 |
| B1 | P1 c23 |
| B0 | P1 c25 |
| P1 | P1 h58 |
| P0 | P1 h62 |
| FALHA | P2 i13 |
| DIFERENTE | P2 h16 |
| IGUAL | P2 i5 |
| H | P2 i40 |
| S0 | P2 i50 |
| S1 | P2 i47 |
| S2 | P2 b50 |
| S3 | P2 b53 |
| C_OUT | P2 a54 |

Total: 113 fios (51 jumpers a barramento, 6 pontes, 16 do Mega, 15 entre placas, 25 internos), 56 peças, 17 pontos de teste.
