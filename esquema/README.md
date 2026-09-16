# esquema/

Projeto EasyEDA editável e a exportação em PDF.

## 0. Arquivos prontos

| Arquivo | O que é |
| ------- | ------- |
| `conferencia_carga.json` | Projeto EasyEDA Std com **quatro folhas**: 1 = o circuito que será montado, com **símbolos da biblioteca LCSC** (footprint e código de peça em cada componente); 2 = notas de modelagem e registro de testes; 3 = **circuito completo ligado fio a fio**, no estilo das folhas de exemplo do EasyEDA (moldura com zonas e bloco de título; Arduino da biblioteca e peças da Commons Library; sem rótulos de net); 4 = montagem em protoboard |
| `conferencia_carga.pdf` | As quatro folhas exportadas, uma por página (entregável) |
| `conferencia_carga_pcb.json` | **Placa de circuito impresso** no EasyEDA Std: 2 camadas, THT, roteada |
| `conferencia_carga_pcb.svg` / `.png` | Prévia da placa (vermelho = topo, azul = fundo, amarelo = silk) |
| `gerar_pcb.py` | Gera a placa (footprints, posicionamento, nets e roteamento) da mesma netlist |
| `conferencia_carga.svg`, `conferencia_carga_notas.svg`, `conferencia_carga_montagem.svg` | Prévia de cada folha, para conferência rápida no navegador |
| `gerar_esquema.py` | Gera todos os arquivos acima a partir da netlist de `gerar_netlist.py` |
| `conferencia_carga_protoboard.png` / `.svg` | **Desenho da montagem em protoboard** (o mesmo da folha 4): 2 placas de 830 pontos + Mega, com cada peça e cada fio |
| `conferencia_carga_protoboard.md` | Lista de montagem furo a furo, na ordem de montar (alimentação, CIs, jumpers, LEDs, fios) |
| `gerar_protoboard.py` | Gera o desenho (nos formatos EasyEDA e SVG) e a lista da mesma netlist; aborta se alguma tira ficar sem furo ou com dois sinais |
| `teste_netlist.py` | **Simula o circuito porta a porta** a partir da netlist e confere o plano de testes inteiro (validação, comparador, somador, bloqueio, 12 casos de integração). Termina com `teste_netlist: OK` |
| `teste_esquema.py` | **Extrai a conectividade das folhas 1 e 3** com as regras do EasyEDA (fio liga em fio ou pino pelas pontas; encostar no meio de um fio só liga com ponto de junção; rótulos e bandeiras) e confere pino a pino contra a netlist; ainda acusa defeitos que enganam quem lê (ponta de fio no meio de outro sem junção, fios sobrepostos, fio atravessando símbolo, ponta solta). Termina com `teste_esquema: folha 1 OK` e `folha 3 OK` |
| `biblioteca.py` + `lib/*.json` | Símbolos das folhas 1 e 3, guardados em `lib/` para gerar offline: as peças LCSC e o Arduino da biblioteca de usuários vêm da API do EasyEDA (`/api/components/<uuid>`); os itens do painel **Commons Library** não passam pela API — estão embutidos no JS do editor (`main.min.js`) e `extrair_comuns()` os lê de lá. `python3 biblioteca.py` baixa o que faltar e lista os pinos |

**Abrir no EasyEDA:** <https://easyeda.com/editor> → Arquivo → Abrir →
EasyEDA... → escolha `conferencia_carga.json` (esquema) e repita para
`conferencia_carga_pcb.json` (placa). Depois Arquivo → Salvar em cada um para
guardar o projeto editável na sua conta. Para exportar o PDF pelo próprio
EasyEDA: Arquivo → Exportar → PDF; para fabricar: Fabricação → Gerber.

**Placa (verificada no editor):** 74 componentes, 58 nets, 0 erros de DRC.
157 × 91 mm, 2 camadas, trilhas de 10 mil, furos de 0,8 mm nos CIs/LEDs/
resistores e 1,0 mm nos potenciômetros, botões e J1. O Arduino Mega fica fora
da placa: liga-se por jumpers no conector **J1** (1 = 5V, 2 = GND, 3 = A0,
4 = A1, 5–14 = D22–D31, 15 = D32, 16 = D33). Push-buttons táteis 6×6 mm de 4
pinos, potenciômetros de 3 pinos em linha (2,54 mm), LEDs 5 mm, resistores
axiais 1/4 W, 100 nF cerâmico. O roteamento é automático e simples (grade de
50 mil); quem preferir pode apagar as trilhas e usar Rota → Auto Router.

Verificado no editor (v6.5.57): as 58 nets do gerenciador de design batem com
a netlist de referência; as 6 nets extras de 1 pino são as saídas das portas
não usadas (U1D–F, U3C–D, U5D). 17 pontos de teste e 16 pinos do Mega ligados.
O projeto foi reaberto no editor (Arquivo → Abrir → EasyEDA...) em 15/09/2026 e a
folha 3 foi importada à parte no mesmo dia: o Gerente de Design listou 57
componentes e 57 redes ligadas — as mesmas da netlist, menos C_OUT, que nessa
folha fica só no pino do somador — e avisos apenas nos pinos livres do Mega, nas
saídas não usadas dos CIs e em C_OUT; cada peça mostra "Adicionar à BOM: Não" e
"Converter para PCB: Não". Lição que o editor deu: fio que termina no meio de
outro só liga com ponto de junção (três entradas ociosas ficaram soltas até isso
ser corrigido; `teste_esquema.py` agora aplica a regra). Como visitante o editor
não exporta BOM nem salva; faça isso na sua conta.

**Símbolos da folha 1.** Cada peça é um símbolo da biblioteca LCSC do EasyEDA
(THT), com footprint e código de peça: SN74HC04N (C2886), SN74HC32N (C2894),
SN74HC86N (C2903), 74HC08N (C5116331), CD74HC283E (C139343), trimpot 3386P 10 k
(C48601064), botão tátil 6×6 de 4 pinos (C71843), resistores CF 1/4 W 2,2 k
(C120063) e MF 1/4 W 10 k (C2903233), cerâmico 100 nF (C254089), LEDs de 5 mm
EAILP05RDMA1 vermelho (C7178079), LTL2R3KYD-EM amarelo (C5349085) e L-53GD verde
(C19634105) e ponto de teste Keystone 5011 (C9900014807). Os CIs aparecem como
caixa DIP (a LCSC não tem símbolo por porta); a alocação de cada porta está
escrita abaixo de cada CI e no bloco de notas. O Arduino Mega continua como caixa
desenhada, por ser um módulo e não uma peça de BOM. Três detalhes de pinagem que
a netlist segue: o botão tátil tem 4 pinos (1-2 e 3-4 ligados internamente; 5 V
em 1, sinal em 3); nos capacitores o pino 2 é o VCC (fica em cima no símbolo);
nos três LEDs o pino 1 é o ânodo.

**Folha 3 (circuito completo, fio a fio).** A mesma fiação redesenhada como nas
folhas de exemplo do EasyEDA: moldura com zonas 1–8 / A–E e bloco de título
(TITLE, REV, Company, Sheet, Date, Drawn By), Arduino à esquerda, peças em volta e
**nenhum rótulo de net** — só fios e bandeiras VCC/GND. O Mega é o símbolo
`ARDUINOMEGA2560` da biblioteca de usuários (caixa com D0–D53, A0–A15, 5V e GND
nas bordas) — o painel Commons Library não tem Arduino, e o `MEGA_DEVICE` da
biblioteca Sistema desenha a placa com os pinos dentro do contorno, sem como
ligar fio. As demais peças são do painel Commons Library: `R_AXIAL-0.4_EU`,
`R_3386P_EU` (trimpot), `C_RAD-0.2_EU`, `LED-TH-5mm_R`/`_G` e `K4-6×6_TH`
(botão de 4 pinos, 1-2 de um lado e 3-4 do outro). Os CIs continuam DIP da LCSC,
porque o painel não tem portas lógicas. Os sinais correm num barramento de
trilhas horizontais (uma trilha por net, reaproveitada entre nets cujos vãos em x
não se sobrepõem) com descidas até cada pino: X0–X3 passam por cima dos CIs, o
resto por baixo do banco de LEDs; entradas ociosas vão ao GND por trilhas curtas
com bandeira. Os tocos de cada lado de CI têm comprimentos distintos (quem sobe é
mais longo quanto mais baixo, quem desce quanto mais alto), de modo que nenhuma
descida cruza o toco de um vizinho e nenhuma ponta de fio cai em cima de outro
fio; há ponto de junção só onde liga — fio que cruza outro sem ponto não liga.
Todas as peças da folha 3 ficam **fora da BOM e da PCB** (`add_into_bom` /
`convert_to_pcb = none`): a BOM e a placa vêm da folha 1, senão os designadores
apareceriam em dobro.

**Protoboard:** placa 1 recebe o Mega (D22–D33, A0, A1, 5 V, GND), os 19 LEDs
com resistor atravessando o canal, os potenciômetros e os botões; placa 2 tem
os seis CIs em linha (U1 na coluna 2 … U6 na 47), 100 nF em cada um e os
pontos de teste em furos livres das tiras. 113 fios no total, 15 entre as
placas. Montar na ordem de `conferencia_carga_protoboard.md`.

**Regenerar e conferir** (após mudar fiação ou layout; `gerar_esquema.py` já chama `gerar_protoboard.py`):

```bash
python3 esquema/gerar_esquema.py && python3 esquema/gerar_pcb.py && python3 esquema/teste_netlist.py && python3 esquema/teste_esquema.py
```

Precisa de `rsvg-convert` (pacote librsvg) para o PDF. Antes de entregar,
preencha a constante `INTEGRANTES` no início de `gerar_esquema.py` (vale para
as quatro folhas) e regenere.

A folha 2 leva a modelagem da etapa 1 (tabelas, mapas K, equações) e a tabela
de registro de testes com os campos "obtido" em branco: depois de rodar os
testes no protótipo, preencha-os no próprio EasyEDA (são textos editáveis) ou
em `notas()` de `gerar_esquema.py` e regenere.

O restante deste arquivo é a **especificação de fiação**: lista de CIs,
alocação de cada porta e netlist completa — é o que o gerador desenha.

---

## 1. Lista de CIs

Todas as equações de [`../docs/02-modelagem-logica.md`](../docs/02-modelagem-logica.md)
cabem em cinco CIs de porta + o somador.

| Ref | CI | Função | Portas usadas |
| --- | -- | ------ | ------------- |
| U1 | 74HC04 | hex inversor | 3 de 6 |
| U2 | 74HC32 | quad OR de 2 entradas | 4 de 4 |
| U3 | 74HC86 | quad XOR de 2 entradas | 2 de 4 |
| U4 | 74HC08 | quad AND — habilitação dos operandos | 4 de 4 |
| U5 | 74HC08 | quad AND — H e LEDs de status | 3 de 4 |
| U6 | 74HC283 | somador de 4 bits | — |

**Por que XOR e não XNOR.** A modelagem oferece duas formas do comparador. A
forma XNOR exigiria o 74HC266, cujas saídas são **dreno aberto** e precisariam
de resistores de pull-up. A forma equivalente já registrada na modelagem evita
isso com saídas totem-pole comuns:

```
DIFERENTE = (A₁ ⊕ P₁) + (A₀ ⊕ P₀)
IGUAL     = DIFERENTE'
```

Mantenha essa forma nas notas do projeto — a outra não deve aparecer.

---

## 2. Alocação das portas

Pinagem DIP-14 idêntica para 74HC08, 74HC32 e 74HC86:
entradas `1,2→3`, `4,5→6`, `9,10→8`, `12,13→11`; GND = 7, VCC = 14.

### U1 — 74HC04 (in → out)

| Porta | Pinos | Entrada | Saída |
| ----- | ----- | ------- | ----- |
| U1A | 1 → 2 | FALHA | **nFALHA** |
| U1B | 3 → 4 | DIFERENTE | **IGUAL** |
| U1C | 5 → 6 | EXCESSO | **nEXCESSO** |
| U1D, U1E, U1F | 9, 11, 13 | — | não usadas, entradas ao GND |

### U2 — 74HC32 (OR)

| Porta | Pinos | Entradas | Saída |
| ----- | ----- | -------- | ----- |
| U2A | 1, 2 → 3 | x₃, x₂ | **FALHA** |
| U2B | 4, 5 → 6 | d₁ (U3A), d₀ (U3B) | **DIFERENTE** |
| U2C | 9, 10 → 8 | S₃, S₂ | **EXCESSO** |
| U2D | 12, 13 → 11 | FALHA, EXCESSO | **ALARME** |

### U3 — 74HC86 (XOR)

| Porta | Pinos | Entradas | Saída |
| ----- | ----- | -------- | ----- |
| U3A | 1, 2 → 3 | A₁, P₁ | **d₁** |
| U3B | 4, 5 → 6 | A₀, P₀ | **d₀** |
| U3C, U3D | 9, 10, 12, 13 | — | não usadas, entradas ao GND |

### U4 — 74HC08, habilitação

| Porta | Pinos | Entradas | Saída |
| ----- | ----- | -------- | ----- |
| U4A | 1, 2 → 3 | A₁, H | **A₁ᵉ** |
| U4B | 4, 5 → 6 | A₀, H | **A₀ᵉ** |
| U4C | 9, 10 → 8 | B₁, H | **B₁ᵉ** |
| U4D | 12, 13 → 11 | B₀, H | **B₀ᵉ** |

### U5 — 74HC08, habilitação e status

| Porta | Pinos | Entradas | Saída |
| ----- | ----- | -------- | ----- |
| U5A | 1, 2 → 3 | nFALHA, IGUAL | **H** |
| U5B | 4, 5 → 6 | nFALHA, DIFERENTE | **CONFERIR** |
| U5C | 9, 10 → 8 | H, nEXCESSO | **LIBERADO** |
| U5D | 12, 13 → 11 | — | não usada, entradas ao GND |

### U6 — 74HC283 (DIP-16)

O índice 1 do datasheet é o bit menos significativo.

| Pino | Nome no datasheet | Liga em |
| ---- | ----------------- | ------- |
| 5 | A1 | A₀ᵉ (U4B pino 6) |
| 6 | B1 | B₀ᵉ (U4D pino 11) |
| 4 | Σ1 | **S₀** → LED + TP |
| 3 | A2 | A₁ᵉ (U4A pino 3) |
| 2 | B2 | B₁ᵉ (U4C pino 8) |
| 1 | Σ2 | **S₁** → LED + TP |
| 14 | A3 | **GND** |
| 15 | B3 | **GND** |
| 13 | Σ3 | **S₂** → LED + TP + U2C pino 10 |
| 12 | A4 | **GND** |
| 11 | B4 | **GND** |
| 10 | Σ4 | **S₃** → LED + TP + U2C pino 9 |
| 7 | C0 (C_in) | **GND** |
| 9 | C4 (C_out) | TP carry final |
| 8 / 16 | GND / VCC | GND / 5 V |

S₂ e S₃ vão ao LED **e** à porta OR do EXCESSO — o excedente continua visível,
como o enunciado exige.

---

## 3. Netlist

### Arduino → barramentos

| Pino | Net | Vai para |
| ---- | --- | -------- |
| A0 | — | cursor do potenciômetro RV1 |
| A1 | — | cursor do potenciômetro RV2 |
| D22 | **x₀ = A₀** | LED N₀ bit 0 · U3B pino 4 · U4B pino 4 · TP A₀ |
| D23 | **x₁ = A₁** | LED N₀ bit 1 · U3A pino 1 · U4A pino 1 · TP A₁ |
| D24 | **x₂** | LED N₀ bit 2 · U2A pino 2 · TP x₂ |
| D25 | **x₃** | LED N₀ bit 3 · U2A pino 1 · TP x₃ |
| D26–D31 | N₀ bits 4–9 | apenas LED (não entram na lógica) |
| D32 | **B₀** | LED B bit 0 · U4D pino 12 · TP B₀ |
| D33 | **B₁** | LED B bit 1 · U4C pino 9 · TP B₁ |

A e X compartilham nets: A₁A₀ **são** x₁x₀. Os pontos de teste de A e de X
podem ser marcadores distintos sobre o mesmo nó.

### Push-buttons

Botão entre 5 V e o sinal; resistor de 10 kΩ do sinal ao GND.

| Sinal | Botão | Pull-down | Vai para |
| ----- | ----- | --------- | -------- |
| **P₀** | SW1 | R_pd1 10 kΩ | U3B pino 5 · TP P₀ |
| **P₁** | SW2 | R_pd2 10 kΩ | U3A pino 2 · TP P₁ |

Solto = 0 pelo pull-down; pressionado = 1. R = 0 com ambos soltos é seleção
válida, não é ausência de comando.

### Nets internos

| Net | Origem | Destinos |
| --- | ------ | -------- |
| FALHA | U2A p3 | U1A p1 · U2D p12 · TP FALHA |
| nFALHA | U1A p2 | U5A p1 · U5B p4 |
| d₁ | U3A p3 | U2B p4 |
| d₀ | U3B p6 | U2B p5 |
| DIFERENTE | U2B p6 | U1B p3 · U5B p5 · TP DIFERENTE |
| IGUAL | U1B p4 | U5A p2 · TP IGUAL |
| H | U5A p3 | U4A p2 · U4B p5 · U4C p10 · U4D p13 · U5C p9 · TP H |
| A₁ᵉ / A₀ᵉ | U4A p3 / U4B p6 | U6 p3 / U6 p5 |
| B₁ᵉ / B₀ᵉ | U4C p8 / U4D p11 | U6 p2 / U6 p6 |
| EXCESSO | U2C p8 | U1C p5 · U2D p13 |
| nEXCESSO | U1C p6 | U5C p10 |
| CONFERIR | U5B p6 | LED amarelo |
| ALARME | U2D p11 | LED vermelho |
| LIBERADO | U5C p8 | LED verde |

**ALARME não realimenta H.** Confira no desenho: nada sai de U2D p11 além do
LED. H depende só de FALHA e IGUAL.

### Alimentação

- 5 V e GND do Arduino são o barramento comum de todos os CIs.
- VCC: U1–U5 pino 14, U6 pino 16. GND: U1–U5 pino 7, U6 pino 8.
- **100 nF** entre VCC e GND de cada CI, junto ao pino — 6 capacitores.
- Entradas não usadas ao GND: U1 p9, p11, p13 · U3 p9, p10, p12, p13 ·
  U5 p12, p13.

---

## 4. LEDs — 19 no total

Cada LED com resistor em série de 2,2 kΩ; saída → resistor → anodo, catodo ao
GND. Com Vf ≈ 2 V a corrente fica em ~1,4 mA, dentro do que uma saída 74HC ou
um pino do Mega fornece com folga.

| Grupo | Qtd | Acionado por |
| ----- | --- | ------------ |
| N₀ bits 0–9 | 10 | D22–D31 |
| B bits 0–1 | 2 | D32–D33 |
| S₀–S₃ | 4 | U6 p4, p1, p13, p10 |
| CONFERIR (amarelo) | 1 | U5B p6 |
| ALARME (vermelho) | 1 | U2D p11 |
| LIBERADO (verde) | 1 | U5C p8 |

## 5. Pontos de teste obrigatórios

X (x₃x₂x₁x₀) · A (A₁A₀) · B (B₁B₀) · R (P₁P₀) · FALHA · IGUAL · DIFERENTE ·
H · S (S₃S₂S₁S₀) · carry final (U6 p9).

## 6. Lista de materiais

| Item | Qtd |
| ---- | --- |
| Arduino Mega 2560 | 1 |
| Potenciômetro linear 10 kΩ | 2 |
| Push-button normalmente aberto | 2 |
| Resistor 10 kΩ (pull-down) | 2 |
| Resistor 2,2 kΩ (LED) | 19 |
| LED 5 mm (N₀, B, S) | 16 |
| LED amarelo / vermelho / verde (status) | 3 |
| 74HC04, 74HC32, 74HC86, 74HC283 | 1 de cada |
| 74HC08 | 2 |
| Capacitor cerâmico 100 nF | 6 |

## 7. Antes de exportar

- [ ] Identificação do grupo na folha (mesmos nomes e matrículas do `.ino`)
- [ ] Notas com a modelagem da etapa 1 — tabelas, mapas K e equações de
      [`../docs/02-modelagem-logica.md`](../docs/02-modelagem-logica.md)
- [ ] Notas com os registros de teste de
      [`../docs/03-plano-de-testes.md`](../docs/03-plano-de-testes.md), obtido
      vs. esperado
- [ ] O desenho representa o protótipo efetivamente montado
- [ ] Exportar em PDF e subir junto com o projeto editável

---

## 8. Importar a fiação automaticamente

A EasyEDA publica uma extensão oficial que monta o esquema a partir de um
netlist: [easyeda/eext-generate-schematic-from-netlist](https://github.com/easyeda/eext-generate-schematic-from-netlist).
Ela só existe para a **versão Pro** — na Std não há equivalente.

Lendo o código da extensão ([`src/enetImporter.ts`](https://github.com/easyeda/eext-generate-schematic-from-netlist/blob/main/src/enetImporter.ts)),
cada componente é localizado primeiro pelo código LCSC em `Supplier Part` e,
se vazio, por busca de `DeviceName` na biblioteca do sistema. Quem não for
encontrado é apenas registrado no log e pulado.

`netlist.json` neste diretório já está pronto: **56 componentes e 58 nets**,
gerados por [`gerar_netlist.py`](gerar_netlist.py) a partir das tabelas das
seções 2 e 3.

### Passos

1. Abra a biblioteca do EasyEDA Pro e anote o código LCSC dos passivos que vai
   usar (2,2 kΩ, 10 kΩ, 100 nF, LEDs, potenciômetro, push-button).
2. Preencha o dicionário `LCSC` no topo de `gerar_netlist.py`.
3. `python3 gerar_netlist.py > netlist.json`
4. Instale a extensão e use **Importar arquivo de netlist**, apontando para
   `netlist.json`.
5. Reorganize o desenho: a extensão coloca os componentes em grade, sem
   preocupação com leitura.

### O que a importação não resolve

- **O Arduino Mega não está no netlist.** A numeração de pinos do símbolo do
  módulo não corresponde aos nomes `D22`–`D33`, e um palpite erraria a fiação.
  Depois de importar, coloque o Mega e ligue-o a 12 nets nomeados: `N0_0` a
  `N0_9`, `B_0`, `B_1`, mais `A0_CURSOR` e `A1_CURSOR` nas entradas analógicas.
- **Pinos de LED, botão e potenciômetro** são assumidos como 1 = anodo /
  2 = catodo, 1–2 no botão e 1 / 2 = cursor / 3 no potenciômetro. Confira
  contra o símbolo que a busca trouxer; num tactile de 4 pinos, ligue 1–2 e
  3–4 em par.
- Pontos de teste, notas de modelagem, identificação do grupo e o PDF
  continuam sendo trabalho manual no editor.

`gerar_netlist.py` valida a coerência antes de emitir: qualquer net com um
único ponto de conexão aborta a geração, exceto as pontas que o Arduino fecha
e o carry final, que por especificação vai só ao ponto de teste.
