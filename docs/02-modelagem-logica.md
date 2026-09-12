# 02 — Modelagem lógica

Conteúdo exigido pela seção 3.3 do enunciado. Estas tabelas e equações devem ser
reproduzidas nas folhas ou notas do projeto EasyEDA.

---

## 1. Validação de X → FALHA

Entrada: os 4 bits inferiores de N₀. Saída FALHA = 0 para X ∈ [0, 3];
FALHA = 1 para X ∈ [4, 15].

| X | x₃ | x₂ | x₁ | x₀ | A = x₁x₀ | FALHA |
| -- | -- | -- | -- | -- | -------- | ----- |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 1 | 0 | 0 | 0 | 1 | 1 | 0 |
| 2 | 0 | 0 | 1 | 0 | 2 | 0 |
| 3 | 0 | 0 | 1 | 1 | 3 | 0 |
| 4 | 0 | 1 | 0 | 0 | 0 | 1 |
| 5 | 0 | 1 | 0 | 1 | 1 | 1 |
| 6 | 0 | 1 | 1 | 0 | 2 | 1 |
| 7 | 0 | 1 | 1 | 1 | 3 | 1 |
| 8 | 1 | 0 | 0 | 0 | 0 | 1 |
| 9 | 1 | 0 | 0 | 1 | 1 | 1 |
| 10 | 1 | 0 | 1 | 0 | 2 | 1 |
| 11 | 1 | 0 | 1 | 1 | 3 | 1 |
| 12 | 1 | 1 | 0 | 0 | 0 | 1 |
| 13 | 1 | 1 | 0 | 1 | 1 | 1 |
| 14 | 1 | 1 | 1 | 0 | 2 | 1 |
| 15 | 1 | 1 | 1 | 1 | 3 | 1 |

**Forma canônica:** FALHA = Σm(4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)

**Mapa K** (linhas x₃x₂, colunas x₁x₀):

| x₃x₂ \ x₁x₀ | 00 | 01 | 11 | 10 |
| ----------- | -- | -- | -- | -- |
| **00** | 0 | 0 | 0 | 0 |
| **01** | 1 | 1 | 1 | 1 |
| **11** | 1 | 1 | 1 | 1 |
| **10** | 1 | 1 | 1 | 1 |

Dois laços de 8 células: a linha inteira x₃ = 1 e a linha inteira x₂ = 1.

```
FALHA = x₃ + x₂
```

Uma única porta OR de 2 entradas. Note que x₁ e x₀ não aparecem na expressão —
é exatamente o efeito pedido no item 2.2: X = 6 tem A = 2, mas continua sendo
código inválido.

---

## 2. Comparador A × R → IGUAL / DIFERENTE

Entradas: A₁A₀ (sensor) e P₁P₀ (botões).

| # | A₁ | A₀ | P₁ | P₀ | A | R | IGUAL | DIFERENTE |
| -- | -- | -- | -- | -- | - | - | ----- | --------- |
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 |
| 2 | 0 | 0 | 1 | 0 | 0 | 2 | 0 | 1 |
| 3 | 0 | 0 | 1 | 1 | 0 | 3 | 0 | 1 |
| 4 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 1 |
| 5 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| 6 | 0 | 1 | 1 | 0 | 1 | 2 | 0 | 1 |
| 7 | 0 | 1 | 1 | 1 | 1 | 3 | 0 | 1 |
| 8 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 1 |
| 9 | 1 | 0 | 0 | 1 | 2 | 1 | 0 | 1 |
| 10 | 1 | 0 | 1 | 0 | 2 | 2 | 1 | 0 |
| 11 | 1 | 0 | 1 | 1 | 2 | 3 | 0 | 1 |
| 12 | 1 | 1 | 0 | 0 | 3 | 0 | 0 | 1 |
| 13 | 1 | 1 | 0 | 1 | 3 | 1 | 0 | 1 |
| 14 | 1 | 1 | 1 | 0 | 3 | 2 | 0 | 1 |
| 15 | 1 | 1 | 1 | 1 | 3 | 3 | 1 | 0 |

**Forma canônica:** IGUAL = Σm(0, 5, 10, 15)

**Mapa K** (linhas A₁A₀, colunas P₁P₀):

| A₁A₀ \ P₁P₀ | 00 | 01 | 11 | 10 |
| ----------- | -- | -- | -- | -- |
| **00** | **1** | 0 | 0 | 0 |
| **01** | 0 | **1** | 0 | 0 |
| **11** | 0 | 0 | **1** | 0 |
| **10** | 0 | 0 | 0 | **1** |

Os quatro mintermos ficam isolados na diagonal — não há laço possível. A
simplificação vem do **fatoramento**, não do mapa:

```
IGUAL = A₁'A₀'P₁'P₀' + A₁'A₀P₁'P₀ + A₁A₀P₁P₀ + A₁A₀'P₁P₀'
      = (A₁'P₁' + A₁P₁) · (A₀'P₀' + A₀P₀)
      = (A₁ ⊙ P₁) · (A₀ ⊙ P₀)
```

Dois XNOR e um AND de 2 entradas.

```
DIFERENTE = IGUAL'
```

Um único inversor, como o enunciado exige. Alternativa equivalente com XOR:
`DIFERENTE = (A₁ ⊕ P₁) + (A₀ ⊕ P₀)`, com IGUAL saindo da inversão. Escolher
**uma** das duas formas e manter a coerência com as notas do projeto.

---

## 3. Habilitação H

| FALHA | IGUAL | H |
| ----- | ----- | - |
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 0 |
| 1 | 1 | 0 |

```
H = FALHA' · IGUAL
```

Portas de habilitação dos operandos — quatro AND de 2 entradas, uma por bit
útil:

```
A₁ᵉ = A₁ · H        B₁ᵉ = B₁ · H
A₀ᵉ = A₀ · H        B₀ᵉ = B₀ · H
```

Com H = 0 os quatro operandos efetivos vão a zero e o somador recebe 0 + 0.

---

## 4. Somador — 16 combinações de A e B

No 74HC283: A₃ = A₂ = B₃ = B₂ = 0 e C_in = 0.

| A | B | A₁A₀ | B₁B₀ | S₃ | S₂ | S₁ | S₀ | S | C_out |
| - | - | ---- | ---- | -- | -- | -- | -- | - | ----- |
| 0 | 0 | 00 | 00 | 0 | 0 | 0 | 0 | 0 | 0 |
| 0 | 1 | 00 | 01 | 0 | 0 | 0 | 1 | 1 | 0 |
| 0 | 2 | 00 | 10 | 0 | 0 | 1 | 0 | 2 | 0 |
| 0 | 3 | 00 | 11 | 0 | 0 | 1 | 1 | 3 | 0 |
| 1 | 0 | 01 | 00 | 0 | 0 | 0 | 1 | 1 | 0 |
| 1 | 1 | 01 | 01 | 0 | 0 | 1 | 0 | 2 | 0 |
| 1 | 2 | 01 | 10 | 0 | 0 | 1 | 1 | 3 | 0 |
| 1 | 3 | 01 | 11 | 0 | 1 | 0 | 0 | 4 | 0 |
| 2 | 0 | 10 | 00 | 0 | 0 | 1 | 0 | 2 | 0 |
| 2 | 1 | 10 | 01 | 0 | 0 | 1 | 1 | 3 | 0 |
| 2 | 2 | 10 | 10 | 0 | 1 | 0 | 0 | 4 | 0 |
| 2 | 3 | 10 | 11 | 0 | 1 | 0 | 1 | 5 | 0 |
| 3 | 0 | 11 | 00 | 0 | 0 | 1 | 1 | 3 | 0 |
| 3 | 1 | 11 | 01 | 0 | 1 | 0 | 0 | 4 | 0 |
| 3 | 2 | 11 | 10 | 0 | 1 | 0 | 1 | 5 | 0 |
| 3 | 3 | 11 | 11 | 0 | 1 | 1 | 0 | 6 | 0 |

**Propagação de carry.** O carry gerado no estágio 0 (quando A₀ = B₀ = 1) entra
no estágio 1; o carry do estágio 1 entra no estágio 2 e aparece em S₂ — é o que
ocorre em 3 + 3 = 0110. Como os estágios 2 e 3 recebem 0 + 0, o carry morre em
S₂: **S₃ e C_out permanecem sempre em 0** nesta faixa de operandos. Daí a
exigência de preservar S₂.

---

## 5. LEDs de status

Entradas: FALHA, IGUAL e EXCESSO, com

```
EXCESSO = S₃ + S₂
```

(total maior que 3, ou seja, mais peças do que posições de fixação; com os
operandos previstos S₃ = 0, então reduz-se a S₂).

| FALHA | IGUAL | EXCESSO | CONFERIR | ALARME | LIBERADO | Observação |
| ----- | ----- | ------- | -------- | ------ | -------- | ---------- |
| 0 | 0 | 0 | 1 | 0 | 0 | conferência divergente, S = 0 |
| 0 | 0 | 1 | × | × | × | impossível: H = 0 ⇒ S = 0 |
| 0 | 1 | 0 | 0 | 0 | 1 | carga de 0 a 3 peças |
| 0 | 1 | 1 | 0 | 1 | 0 | 4 a 6 peças, dividir ciclo |
| 1 | 0 | 0 | 0 | 1 | 0 | código inválido |
| 1 | 0 | 1 | × | × | × | impossível |
| 1 | 1 | 0 | 0 | 1 | 0 | inválido prevalece sobre a conferência |
| 1 | 1 | 1 | × | × | × | impossível |

As linhas com EXCESSO = 1 e H = 0 não são produzidas pelo circuito (com H = 0 o
somador recebe 0 + 0) e entram como condições irrelevantes.

**Equações:**

```
CONFERIR = FALHA' · IGUAL'  =  FALHA' · DIFERENTE
ALARME   = FALHA + EXCESSO
LIBERADO = H · EXCESSO'     =  FALHA' · IGUAL · EXCESSO'
```

Três exigências do enunciado atendidas por essas equações:

- **ALARME não entra em H.** A realimentação fica proibida; H depende só de
  FALHA e IGUAL. Por isso, com S ∈ [4, 6] o somador continua habilitado e S
  permanece visível nos LEDs.
- **CONFERIR só acende com entrada válida.** Com FALHA = 1 o termo FALHA' zera
  CONFERIR e o alarme vermelho prevalece.
- Exatamente um dos três LEDs fica aceso em qualquer combinação possível.

---

## Resumo das equações

```
FALHA     = x₃ + x₂
A         = x₁x₀
B         = bits 1 e 0 de N₁
R         = P₁P₀
IGUAL     = (A₁ ⊙ P₁) · (A₀ ⊙ P₀)
DIFERENTE = IGUAL'
H         = FALHA' · IGUAL
A₁ᵉ A₀ᵉ   = A₁·H , A₀·H
B₁ᵉ B₀ᵉ   = B₁·H , B₀·H
S         = (00A₁ᵉA₀ᵉ) + (00B₁ᵉB₀ᵉ)   [74HC283, C_in = 0]
EXCESSO   = S₃ + S₂
CONFERIR  = FALHA' · DIFERENTE
ALARME    = FALHA + EXCESSO
LIBERADO  = FALHA' · IGUAL · EXCESSO'
```
