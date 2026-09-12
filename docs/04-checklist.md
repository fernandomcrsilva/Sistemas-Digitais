# 04 — Checklist até a entrega

Entrega e apresentação: **02/10/2026**, turma 6a.

## Organização

- [ ] Formar o grupo e definir o representante
- [ ] Representante cria a pasta `turma6a-<matricula>` em
      [claytonjasilva/trabalhoAP1-2026.2](https://github.com/claytonjasilva/trabalhoAP1-2026.2)
- [ ] Criar as subpastas `esquema/` e `sketch/` lá
- [ ] Solicitar acesso de escrita ao professor, se necessário
- [ ] Preencher a tabela da equipe no README

## Modelagem (fazer antes de montar)

- [ ] Tabela de 16 linhas de X → FALHA, canônica, mapa K e simplificação
- [ ] Tabela de 16 pares A/R → IGUAL, expressão e simplificação
- [ ] Registrar DIFERENTE como complemento de IGUAL
- [ ] Equação de H e das quatro portas de habilitação
- [ ] Tabela das 16 somas de A e B e explicação da propagação de carry
- [ ] Tabelas e equações dos três LEDs de status

> Rascunho pronto em [`02-modelagem-logica.md`](02-modelagem-logica.md) —
> revisar e transcrever para as notas do EasyEDA.

## Sketch

- [ ] Cabeçalho com nomes, matrículas e identificação do representante
- [ ] `setup()`: D22–D33 como `OUTPUT`, modo inicial ANALOGICO
- [ ] Aquisição dos dois canais a cada ~100 ms
- [ ] Publicação dos bits em D22–D31 e D32–D33
- [ ] Impressão serial em decimal e binário de 10 dígitos com zeros à esquerda
- [ ] Parser de `TESTE N0 N1` e `ANALOGICO`
- [ ] Validação de faixa 0–1023 e rejeição sem alterar o par vigente
- [ ] Modo atual visível no monitor serial
- [ ] Conferir que o Arduino não lê botões nem calcula H, soma ou status

## Esquema no EasyEDA

- [ ] Arduino Mega com 5 V e GND comuns
- [ ] Dois potenciômetros de 10 kΩ com cursores em A0 e A1
- [ ] Barramento N₀ em D22–D31 e B em D32–D33
- [ ] Dois push-buttons com pull-down de 10 kΩ
- [ ] Bloco de validação de X
- [ ] Comparador de igualdade + inversor para DIFERENTE
- [ ] Quatro portas AND de habilitação
- [ ] 74HC283 com bits superiores e C_in aterrados
- [ ] Lógica dos três LEDs de status
- [ ] 19 LEDs no total, cada um com resistor (~2,2 kΩ)
- [ ] 100 nF em cada CI; entradas não usadas em nível fixo
- [ ] Pontos de teste identificados
- [ ] Notas com a modelagem e os registros de teste
- [ ] Exportar em PDF

## Montagem e testes

- [ ] Conferir alimentação e orientação dos CIs antes de energizar
- [ ] Rodar os testes de bloco (ver [`03-plano-de-testes.md`](03-plano-de-testes.md))
- [ ] Rodar os 12 casos de integração e registrar obtido vs. esperado
- [ ] Confirmar que com S ∈ [4, 6] o ALARME acende e S continua visível
- [ ] Confirmar que ALARME não realimenta H

## Entrega

- [ ] Subir projeto EasyEDA editável + PDF em `esquema/`
- [ ] Subir o `.ino` efetivamente usado no protótipo em `sketch/`
- [ ] Ensaiar a apresentação: operação liberada, divergência de conferência,
      código inválido e excesso de peças
- [ ] Todos os integrantes preparados para explicar as decisões de projeto
