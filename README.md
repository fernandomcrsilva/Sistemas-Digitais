# AP1 · Conferência de carga (Sistemas Digitais 2026.2, turma 6a)

Arduino Mega 2560 + circuito com 4 CIs 74LS. Prof. Clayton J A Silva.

## O que tem aqui

| Arquivo | O que é |
|---|---|
| `esquema/conferencia_carga.json` | Projeto EasyEDA Standard: folha 1 (esquema completo) e folha 2 (notas e tabela-verdade). Abrir em Arquivo → Abrir → EasyEDA. |
| `esquema/conferencia_carga.pdf` | As duas folhas do esquema em PDF |
| `sketch/conferencia_carga/conferencia_carga.ino` | Sketch do Arduino Mega 2560 |

## Funcionamento

- Cada potenciômetro vira 2 bits (0–25% = 00, 25–50% = 01, 50–75% = 10, 75–100% = 11), com média de 16 leituras e histerese de ~3%.
- Potenciômetro 1 (A0) → X1 X0 em D23 D22 · potenciômetro 2 (A1) → B1 B0 em D33 D32.
- A lógica fica nos CIs, não no Arduino:
  - 74LS86 (XOR): compara X com os botões P1 P0, gera H = DIFERENTE ⊕ 1 e LIBERADO = H ⊕ S2
  - 74LS32 (OR): DIFERENTE = (X1 ⊕ P1) + (X0 ⊕ P0) → LED CONFERIR
  - 74LS08 (AND): só deixa a soma passar com H = 1
  - 74LS283 (somador): S = X + B → LEDs S3–S0; ALARME = S2
- 11 LEDs (X1, X0, B1, B0, S3–S0, CONFERIR, ALARME, LIBERADO), cada um com resistor de 1,5 kΩ no catodo. Pull-down dos botões também de 1,5 kΩ. O LED S3 nunca acende (soma máxima 3 + 3 = 6).

## Uso

Monitor Serial em 9600 baud, final de linha "Nova linha":

- `TESTE <N0> <N1>` fixa os dois valores (0 a 1023), sem os potenciômetros
- `ANALOGICO` volta a ler os potenciômetros
