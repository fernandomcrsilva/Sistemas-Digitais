# 03 — Plano de testes

## 1. Preparação

- [ ] Conferir alimentação, GND e orientação de todos os CIs antes de energizar.
- [ ] Identificar os barramentos e os pontos de teste: X, A, B, R, FALHA,
      IGUAL, DIFERENTE, H, S, carry final.

## 2. Testes de bloco

### 2.1 Aquisição

- [ ] Demonstrar leitura real dos dois potenciômetros: extremo mínimo, posição
      intermediária e extremo máximo.
- [ ] Comparar os LEDs de N₀ e de B com o que aparece no monitor serial.
- [ ] Verificar os 10 dígitos binários com zeros à esquerda.

### 2.2 Validação

- [ ] Testar os 16 códigos de X e registrar FALHA em cada um.

| X | FALHA esperada | FALHA obtida | OK |
| -- | -------------- | ------------ | -- |
| 0 | 0 | | |
| 1 | 0 | | |
| 2 | 0 | | |
| 3 | 0 | | |
| 4 | 1 | | |
| 5 | 1 | | |
| 6 | 1 | | |
| 7 | 1 | | |
| 8 | 1 | | |
| 9 | 1 | | |
| 10 | 1 | | |
| 11 | 1 | | |
| 12 | 1 | | |
| 13 | 1 | | |
| 14 | 1 | | |
| 15 | 1 | | |

### 2.3 Comparador

- [ ] Testar os 16 pares A/R.
- [ ] Verificar que IGUAL e DIFERENTE são complementares: exatamente uma das
      duas saídas ativa em cada par.

### 2.4 Somador

- [ ] Com X válido e R = A, testar as 16 combinações de A e B.
- [ ] Conferir S₃S₂S₁S₀ e o carry final contra a tabela da modelagem.

### 2.5 Bloqueio

- [ ] Com H = 0, variar os dois sensores e verificar que os operandos efetivos
      e S permanecem zerados enquanto H continuar em 0.

## 3. Casos de integração

Um caso de integração verifica vários blocos conectados, das entradas até os
LEDs finais.

**Como executar cada linha:** fornecer N₀ e N₁ pelo modo de teste, ajustar
fisicamente os botões para R, aguardar a estabilização e comparar H, S e os três
LEDs com os resultados esperados.

CON = CONFERIR, AL = ALARME, LIB = LIBERADO. Nas saídas, 1 significa ativo. N₀ e
N₁ são os códigos completos; os demais valores em decimal, exceto R, em binário.

| # | N₀ | N₁ | X | A | B | R | H | S | CON | AL | LIB | Obtido | OK |
| - | -- | -- | - | - | - | - | - | - | --- | -- | --- | ------ | -- |
| 1 | 0 | 0 | 0 | 0 | 0 | 00 | 1 | 0 | 0 | 0 | 1 | | |
| 2 | 1 | 1 | 1 | 1 | 1 | 00 | 0 | 0 | 1 | 0 | 0 | | |
| 3 | 2 | 1 | 2 | 2 | 1 | 10 | 1 | 3 | 0 | 0 | 1 | | |
| 4 | 2 | 2 | 2 | 2 | 2 | 10 | 1 | 4 | 0 | 1 | 0 | | |
| 5 | 2 | 3 | 2 | 2 | 3 | 10 | 1 | 5 | 0 | 1 | 0 | | |
| 6 | 3 | 3 | 3 | 3 | 3 | 11 | 1 | 6 | 0 | 1 | 0 | | |
| 7 | 2 | 1 | 2 | 2 | 1 | 00 | 0 | 0 | 1 | 0 | 0 | | |
| 8 | 6 | 1 | 6 | 2 | 1 | 10 | 0 | 0 | 0 | 1 | 0 | | |
| 9 | 15 | 3 | 15 | 3 | 3 | 11 | 0 | 0 | 0 | 1 | 0 | | |
| 10 | 16 | 1 | 0 | 0 | 1 | 00 | 1 | 1 | 0 | 0 | 1 | | |
| 11 | 18 | 5 | 2 | 2 | 1 | 10 | 1 | 3 | 0 | 0 | 1 | | |
| 12 | 2 | 6 | 2 | 2 | 2 | 10 | 1 | 4 | 0 | 1 | 0 | | |

O que cada grupo de casos prova:

- **1 a 6** — caminho completo com conferência aprovada, incluindo a transição
  de liberado (S ≤ 3) para excesso (S ≥ 4).
- **7** — divergência de conferência: DIFERENTE ativa, H cai, S zera, CONFERIR
  acende.
- **8 e 9** — código inválido prevalece mesmo com os bits inferiores batendo
  com os botões (caso 8) ou com A = R (caso 9).
- **10 a 12** — extração dos bits inferiores. N₀ = 16 e 18, N₁ = 5 e 6 mostram
  que leitura alta não implica quantidade alta neste modelo cíclico.

## 4. Demonstração com potenciômetros

Além da tabela acima, executar a sequência do item 2.6 do enunciado usando os
potenciômetros no modo analógico e os códigos efetivamente observados:

1. Selecionar X = 2 no primeiro potenciômetro → A = 10.
2. Manter P₁ pressionado e P₀ solto → R = 10. A conferência habilita a soma.
3. Selecionar B = 1 → S = 3, LIBERADO acende.
4. Alterar B para 2 → S = 4, LIBERADO apaga, ALARME acende. **S continua
   visível nos LEDs.**
5. Soltar P₁ → R = 0, conferência falha, S vai a 0, CONFERIR acende.
6. Selecionar X = 6 → apesar de A = 2, o código é inválido: ALARME acende e a
   soma permanece bloqueada.

## 5. Observações sobre transições

A avaliação considera as saídas estabilizadas. Preparar explicação para:

- pequenas oscilações dos bits inferiores do ADC;
- transições breves causadas pela atualização sequencial dos pinos;
- transições breves causadas pelo contato dos botões.

Não se exige memória, debounce com retenção nem amostragem simultânea dos dois
canais.

## 6. Registro

Transcrever esta tabela preenchida para as notas do projeto EasyEDA. A simulação
pode apoiar a conferência exaustiva, mas os casos de integração escolhidos pelo
professor serão demonstrados no protótipo físico.
