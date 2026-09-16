# sketch/

`conferencia_carga.ino` — arquivo usado no protótipo. Entregável obrigatório
(item 07 do enunciado): copiar para `turma6a-<matricula>/sketch/` no
repositório do professor, **com nomes e matrículas preenchidos no cabeçalho**.

## O que o enunciado exige × onde está no sketch

| Enunciado | Sketch |
| --------- | ------ |
| 2.1 Ler A0 e A1 a cada ~100 ms, em sequência, formando o par N₀/N₁ | `loop()` com `millis()` e `PERIODO_MS = 100`; `adquirir()` lê A0 e depois A1 |
| 2.1 Decimal e binário de **dez dígitos** com zeros à esquerda | `relatar()` + `imprimirBinario10()` (bit a bit; `print(v, BIN)` não preenche) |
| 2.1 Dez bits de N₀ em dez pinos; dois bits inferiores de N₁ em dois pinos | `publicar()`: D22 = bit 0 … D31 = bit 9; D32 = bit 0, D33 = bit 1 (igual ao trecho 5.2) |
| 2.1 Mensagem serial = mesmo par que está nos pinos | `publicar(n0, n1)` e `relatar()` na mesma volta, com as mesmas variáveis |
| 4.3 `TESTE N0 N1` com inteiros de 0 a 1023; `ANALOGICO` retoma | `interpretar()`, `lerInteiro()`, `naFaixa()` |
| 4.3 Inválido é rejeitado **sem alterar o par vigente** | `rejeitar()`; `n0`/`n1` só mudam depois de toda a validação |
| 4.3 Modo visível no monitor serial | prefixo `[ANALOGICO]` / `[TESTE]` em cada linha e `Modo atual: …` |
| 4.3 / 5.1 Não simular botões, não calcular H, soma ou status | não há leitura de botões nem lógica; só aquisição, pinos e serial |
| 5.1 Funções separadas; iniciar com D22–D33 como saída e modo ANALOGICO | `setup()` e as funções `adquirir / publicar / relatar / lerSerial` |
| 5.3 Nomes, matrículas e representante no início | cabeçalho (preencher) |

Monitor serial: **9600 baud**, final de linha "Nova linha" ou "Ambos".
Exemplo de saída:

```
[ANALOGICO] N0 = 18 (0000010010)  N1 = 5 (0000000101)
Modo atual: TESTE
[TESTE]     N0 = 1023 (1111111111)  N1 = 0 (0000000000)
Comando invalido - par vigente mantido
```

## Teste no PC (sem Arduino)

`teste_host.cpp` simula `Serial`, `millis()` e `analogRead()`, inclui o `.ino`
e confere formato da saída, pinos e o parser (faixa, lixo, estouro, CR/LF,
minúsculas). Não faz parte da entrega.

```bash
g++ -std=gnu++11 -Isketch sketch/teste_host.cpp -o /tmp/teste_host && /tmp/teste_host
```

Compilado para o Mega 2560 com arduino-cli (core `arduino:avr` 1.8.8) em
15/09/2026: 4832 bytes de flash (1 %) e 250 bytes de RAM (3 %), sem avisos no
sketch. Para repetir, com a pasta copiada para `conferencia_carga/`:

```bash
arduino-cli compile --fqbn arduino:avr:mega:cpu=atmega2560 conferencia_carga
```
