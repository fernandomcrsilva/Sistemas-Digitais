# 01 — Resumo dos requisitos

## Modelo dos sensores

| Sinal | Origem | Definição |
| ----- | ------ | --------- |
| N₀ | `analogRead(A0)` | código de 10 bits, 0–1023 |
| X  | N₀ mod 16 | 4 bits inferiores de N₀ |
| A  | X mod 4 | 2 bits inferiores de X — quantidade do alimentador A |
| N₁ | `analogRead(A1)` | código de 10 bits, 0–1023 |
| B  | N₁ mod 4 | 2 bits inferiores de N₁ — quantidade do alimentador B |

Os potenciômetros selecionam **códigos cíclicos**, não uma escala proporcional.
N₀ = 16 dá X = 0; N₀ = 18 dá X = 2. É proibido reescalonar o valor ou usar os
bits mais significativos.

Somente X ∈ [0, 3] é código válido. X ∈ [4, 15] é código inválido do primeiro
sensor. Todos os quatro códigos de B são válidos.

## Funcionalidades

### F01 — Aquisição e representação digital

- Ler A0 e A1 a cada ~100 ms, formando um par de amostras N₀ e N₁.
- Imprimir ambos no monitor serial em decimal e em binário de **10 dígitos**
  com zeros à esquerda.
- Publicar os 10 bits de N₀ em D22–D31 (D22 = bit 0) com LED em cada pino.
- Publicar os 2 bits inferiores de N₁ em D32–D33 com LED em cada pino.
- Manter o par disponível até a próxima atualização; a mensagem serial deve
  corresponder ao mesmo par enviado aos pinos.

Passo ideal do ADC com referência nominal de 5 V: 5/1024 ≈ 4,88 mV.

### F02 — Validação de X

`FALHA = 0` para X ∈ [0, 3]; `FALHA = 1` para X ∈ [4, 15].

Entrada inválida impede a soma e acende o LED vermelho ALARME, **mesmo que os
dois bits inferiores coincidam com os botões**.

### F03 — Conferência por push-buttons

Dois botões normalmente abertos formam R = P₁P₀. Pressionado = 1, solto = 0.

| P₁ | P₀ | R |
| -- | -- | - |
| solto | solto | 0 |
| solto | pressionado | 1 |
| pressionado | solto | 2 |
| pressionado | pressionado | 3 |

- Comparador de 2 bits construído com portas lógicas. **Não** usar CI
  comparador pronto.
- Disponibilizar IGUAL e DIFERENTE em pontos de teste; DIFERENTE é a inversão
  de IGUAL.
- Habilitação: `H = 1` quando `FALHA = 0` **e** `A = R`.
- Os botões codificam um número, não armazenam confirmação — soltar ou
  pressionar refaz a conferência imediatamente.
- R = 0 com ambos soltos é seleção válida.

### F04 — Liberação dos operandos e soma

- Quatro portas AND habilitam os bits de A e B com H antes do somador.
  Com H = 0, o somador recebe 0 + 0.
- CI somador obrigatório: **74HC283** ou equivalente compatível.
- Bits superiores de cada operando e carry de entrada fixados em 0.
- S₃S₂S₁S₀ em quatro LEDs; carry final acessível em ponto de teste.
- Com H = 1, S varia de 0 a 6. S₂ precisa ser preservado (3 + 3 = 0110).

### F05 — Liberação da carga

| Situação | CONFERIR (amarelo) | ALARME (vermelho) | LIBERADO (verde) | S |
| -------- | ------------------ | ----------------- | ---------------- | - |
| X inválido | apagado | aceso | apagado | 0, bloqueada |
| X válido e A ≠ R | aceso | apagado | apagado | 0, bloqueada |
| X válido, A = R, total 0–3 | apagado | apagado | aceso | A + B |
| X válido, A = R, total 4–6 | apagado | aceso | apagado | A + B |

Dois pontos que o enunciado destaca:

- O excesso de peças **não zera a soma**. O valor excedente continua visível
  nos LEDs de S.
- **Não realimentar ALARME na habilitação.** H depende somente de FALHA e
  IGUAL.

## Não escopo

- Movimentação física de lotes, motores ou atuadores de potência.
- Contagem acumulada, armazenamento da leitura ou retenção da confirmação.
- Cálculo de comparação, soma ou alarme pelo Arduino.

## Pinagem e componentes

| Elemento | Ligação / requisito |
| -------- | ------------------- |
| Arduino Mega 2560 | 5 V e GND comuns aos circuitos externos |
| 2 potenciômetros lineares 10 kΩ | extremos em 5 V e GND; cursores em A0 e A1 |
| Código N₀ | D22 = bit 0 … D31 = bit 9; D22–D25 alimentam X₀–X₃ |
| Quantidade B | D32 = bit 0 de N₁; D33 = bit 1 de N₁ |
| Push-buttons P₁, P₀ | botão entre 5 V e o sinal; pull-down de 10 kΩ entre sinal e GND |
| Validação e comparador | portas lógicas externas |
| Habilitação | quatro portas AND, uma por bit útil |
| Somador | CI de 4 bits conforme datasheet |
| Indicadores | 10 LEDs (N₀) + 2 (B) + 4 (S) + 3 de status, cada um com resistor |

Requisitos elétricos: preferir CIs 74HC em 5 V; resistores de LED a partir de
2,2 kΩ; desacoplamento de 100 nF junto à alimentação de cada CI; entradas não
utilizadas em nível definido; não unir saídas.

Pontos de teste obrigatórios: **X, A, B, R, FALHA, IGUAL, DIFERENTE, H, S e
carry final**.

## Modo de teste do sketch

- `TESTE N0 N1` — dois inteiros de 0 a 1023, coloca um par conhecido nos mesmos
  pinos usados no modo analógico.
- `ANALOGICO` — retoma a leitura dos potenciômetros.
- Valores ou comandos inválidos são rejeitados **sem alterar o par vigente**.
- O modo atual deve ser visível no monitor serial.
- O modo de teste não pode simular os botões, calcular H nem substituir a soma
  e os alarmes.

## Avaliação

| Critério | Pontos |
| -------- | ------ |
| Aquisição dos dois canais e explicação da representação digital | 1,5 |
| Validação de X e modelagem booleana | 1,5 |
| Comparador, botões e habilitação dos operandos | 2,0 |
| Somador de 4 bits e liberação da carga | 2,0 |
| Esquema completo no EasyEDA | 1,5 |
| Integração, testes e explicação do protótipo | 1,5 |

Blocos isolados, sem conexão funcional, não atendem ao requisito de integração.

## Entregáveis

1. **Esquema no EasyEDA** — projeto editável e exportação em PDF, com notas de
   modelagem e de testes. Deve representar o protótipo efetivamente montado.
2. **Sketch .ino** — versão usada na demonstração, com integrantes e matrículas
   no cabeçalho, publicada em `sketch/`.
3. **Protótipo funcional** — circuito em protoboard apresentado em aula.

Não há relatório separado: a documentação vai nas folhas ou notas do próprio
projeto EasyEDA.
