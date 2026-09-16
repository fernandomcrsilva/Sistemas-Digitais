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
- [x] `setup()`: D22–D33 como `OUTPUT`, modo inicial ANALOGICO
- [x] Aquisição dos dois canais a cada ~100 ms
- [x] Publicação dos bits em D22–D31 e D32–D33
- [x] Impressão serial em decimal e binário de 10 dígitos com zeros à esquerda
- [x] Parser de `TESTE N0 N1` e `ANALOGICO`
- [x] Validação de faixa 0–1023 e rejeição sem alterar o par vigente
- [x] Modo atual visível no monitor serial
- [x] Conferir que o Arduino não lê botões nem calcula H, soma ou status

## Esquema no EasyEDA

> Gerado por [`../esquema/gerar_esquema.py`](../esquema/gerar_esquema.py):
> `conferencia_carga.json` (4 folhas: circuito com símbolos da biblioteca LCSC, notas,
> montagem no estilo dos exemplos do EasyEDA — Arduino da biblioteca e peças da Commons
> Library — e protoboard) e `conferencia_carga.pdf` (4 páginas). Falta só preencher
> `INTEGRANTES` no início do gerador.

- [x] Arduino Mega com 5 V e GND comuns
- [x] Dois potenciômetros de 10 kΩ com cursores em A0 e A1
- [x] Barramento N₀ em D22–D31 e B em D32–D33
- [x] Dois push-buttons com pull-down de 10 kΩ
- [x] Bloco de validação de X
- [x] Comparador de igualdade + inversor para DIFERENTE
- [x] Quatro portas AND de habilitação
- [x] 74HC283 com bits superiores e C_in aterrados
- [x] Lógica dos três LEDs de status
- [x] 19 LEDs no total, cada um com resistor (~2,2 kΩ)
- [x] 100 nF em cada CI; entradas não usadas em nível fixo
- [x] Pontos de teste identificados
- [x] Notas com a modelagem na folha 2 do projeto
- [ ] Registro de testes: preencher os campos "obtido" da folha 2 após a montagem
- [x] Exportar em PDF
- [x] Placa de circuito impresso (`conferencia_carga_pcb.json`, 2 camadas, roteada, DRC ok)

## Montagem e testes

- [ ] Montar seguindo [`../esquema/conferencia_carga_protoboard.md`](../esquema/conferencia_carga_protoboard.md)
      (desenho em `conferencia_carga_protoboard.png`)
- [ ] Conferir alimentação e orientação dos CIs antes de energizar
- [x] Plano de testes conferido em simulação da netlist (`esquema/teste_netlist.py`)
- [ ] Rodar os testes de bloco no protótipo (ver [`03-plano-de-testes.md`](03-plano-de-testes.md))
- [ ] Rodar os 12 casos de integração e registrar obtido vs. esperado
- [ ] Confirmar que com S ∈ [4, 6] o ALARME acende e S continua visível
- [ ] Confirmar que ALARME não realimenta H

## Entrega

- [ ] Subir `conferencia_carga.json` + `conferencia_carga.pdf` em `esquema/`
- [ ] Subir o `.ino` efetivamente usado no protótipo em `sketch/`
- [ ] Ensaiar a apresentação: operação liberada, divergência de conferência,
      código inválido e excesso de peças
- [ ] Todos os integrantes preparados para explicar as decisões de projeto
