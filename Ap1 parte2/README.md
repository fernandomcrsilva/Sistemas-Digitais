# AP1 · Conferência de carga (Sistemas Digitais 2026.2, turma 6a)

Arduino Mega 2560 + lógica com CIs 74HC. Versão de **2 bits por potenciômetro** e **4 CIs**.

- Cada potenciômetro vira 2 bits (0–25% = 00, 25–50% = 01, 50–75% = 10, 75–100% = 11), com média de 16 leituras e histerese de ~3%.
- Pot. 1 → X1 X0 em D23 D22 · Pot. 2 → B1 B0 em D33 D32.
- Lógica: U3 74HC86, U2 74HC32 (só a porta 2), U4 74HC08, U6 74HC283.
  - DIFERENTE = (X1 ⊕ P1) + (X0 ⊕ P0) = LED CONFERIR
  - H = DIFERENTE ⊕ 1
  - S = (A + B) com H = 1, senão 0
  - ALARME = S2 · LIBERADO = H ⊕ S2
- 11 LEDs: X1, X0, B1, B0, S3–S0, CONFERIR, ALARME, LIBERADO. O LED S3 nunca acende (soma máxima 3 + 3 = 6).

## Pastas

| Arquivo | O que é |
|---|---|
| `esquema/conferencia_carga.json` | Projeto EasyEDA Standard (4 folhas: esquema, notas, placa perfurada vista de cima e de baixo). Abrir em Arquivo → Abrir → EasyEDA. |
| `esquema/conferencia_carga.pdf` | Prévia das 4 folhas do projeto EasyEDA |
| `esquema/esquema_logico_2bits.pdf` | Desenho da lógica com chip e pinos de cada porta |
| `sketch/conferencia_carga.ino` | Sketch principal (o da entrega) |
| `sketch/extras/…_monitor` | Versão de teste que lê as saídas do circuito pelos pinos A2–A10 e confere |
| `sketch/extras/…_autoteste` | Roteiro guiado para achar defeitos com uma ponta de prova no A2 (não entregar) |
| `docs/AP1_desenho_protoboard_2bits.pdf` | Montagem em 2 protoboards, fio a fio |
| `docs/AP1_placa_perfurada_fios_por_cima.pdf` | Placa perfurada 30 × 26 furos, fios de sinal por cima |
| `docs/AP1_bateria_de_testes_2bits.pdf` | Testes com resultado esperado e coluna para anotar |
| `docs/AP1_conferencia_carga_referencia_2bits.pdf` | Referência: LEDs, componentes, pinagem, pinos do Mega, testes e diagnóstico |
| `paginas/*.html` | Páginas interativas (abrem direto no navegador, sem internet) |
| `testes/teste_sketch.cpp` | Roda o sketch no computador com um Arduino simulado |

## Teste do sketch no computador

```
cd testes
g++ -std=c++17 teste_sketch.cpp -o teste_sketch && ./teste_sketch
```

Confere as trocas de faixa com histerese, o potenciômetro parado na fronteira com ruído, o comando `TESTE` de 0 a 1023 e a recusa de comandos inválidos.
