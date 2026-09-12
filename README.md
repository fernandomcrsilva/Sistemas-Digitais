# Trabalho AP1 — Sistemas Digitais 2026.2

Conferência de carga para inspeção · Arduino Mega 2560
Prof. Clayton J A Silva · Turma 6a · Entrega: **02/10/2026**

Enunciado: <https://claytonjasilva.github.io/sisdig_aulas/sistemas_digitais_trabalhoap1_26_2.html>
Repositório de entrega: <https://github.com/claytonjasilva/trabalhoAP1-2026.2>

---

## Sobre o projeto

Estação didática de conferência de carga para uma bancada de inspeção com **três
posições de fixação**. Dois alimentadores (A e B) preparam peças; dois
potenciômetros simulam os sensores de quantidade. O operador informa por
push-buttons a quantidade esperada de A, o circuito confere, soma A + B e decide
se a carga cabe nas três posições.

**Regra central do trabalho:** o Arduino apenas adquire os sinais e publica os
bits em pinos digitais. Toda comparação, habilitação, soma e lógica de alarme é
feita em circuito externo com portas lógicas e CI somador. Cálculo no Arduino
não substitui o circuito.

```
Dois sensores analógicos → Validação + conferência → Soma autorizada → Carga e alarme
```

## Estrutura

```
.
├── docs/
│   ├── 01-requisitos.md         # Resumo do enunciado
│   ├── 02-modelagem-logica.md   # Tabelas verdade, mapas K e equações
│   ├── 03-plano-de-testes.md    # Testes de bloco e casos de integração
│   └── 04-checklist.md          # Lista de tarefas até a entrega
├── esquema/                     # Projeto EasyEDA editável + exportação PDF
└── sketch/                      # Arquivo .ino usado no protótipo
```

## Equipe

| Nome | Matrícula | Representante |
| ---- | --------- | ------------- |
|      |           |               |

> Preencher antes da entrega. O mesmo cabeçalho deve constar no `.ino`.

## Status

- [ ] Modelagem lógica revisada
- [ ] Sketch escrito e testado
- [ ] Esquema no EasyEDA
- [ ] Protótipo montado
- [ ] Testes de integração registrados
- [ ] Arquivos publicados em `turma6a-<matricula>/` no repositório do professor
