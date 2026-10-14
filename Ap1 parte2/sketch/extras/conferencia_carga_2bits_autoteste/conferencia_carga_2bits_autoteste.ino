/*
 * Trabalho AP1 - Sistemas Digitais 2026.2 - Turma 6a
 * Conferencia de carga para inspecao - Arduino Mega 2560
 * Prof. Clayton J A Silva
 *
 * Integrantes:
 *   <NOME COMPLETO> - <MATRICULA>   (representante)
 *   <NOME COMPLETO> - <MATRICULA>
 *   <NOME COMPLETO> - <MATRICULA>
 *
 * >>> VERSAO DE AUTOTESTE - SO PARA ACHAR DEFEITOS NA MONTAGEM, NAO ENTREGAR <<<
 * Faz tudo o que o sketch principal faz e acrescenta dois roteiros guiados:
 *   DIAG S   caminho da soma: U4 (08) -> U6 (283) -> LEDs S1 e S0
 *   DIAG H   caminho da habilitacao H e do status: U3 (86) -> U2 (32) -> U3 -> LEDs
 * Ligue um jumper no pino A2 do Mega e use a outra ponta como ponta de prova.
 * O sketch fixa o pot. 1 em 00 e o pot. 2 em 11 (TESTE 0 1023), pede um ponto
 * por vez, mede a tensao e diz se esta certa; quando nao esta, diz qual fio ou
 * CI conferir.
 *
 * Versao 2 bits: cada potenciometro vira um valor de 0 a 3 (4 faixas de 25%).
 *   0% a 25%    (0 a 255)    -> 00
 *   25% a 50%   (256 a 511)  -> 01
 *   50% a 75%   (512 a 767)  -> 10
 *   75% a 100%  (768 a 1023) -> 11      (valor = leitura >> 8)
 *
 * Para nao piscar: media de 16 leituras + histerese de 30 contagens (~3%)
 * em cada fronteira.
 *
 * Pinos (os mesmos da placa atual):
 *   RV1 -> A0 -> A = A1 A0 -> D23 (A1), D22 (A0)
 *   RV2 -> A1 -> B = B1 B0 -> D33 (B1), D32 (B0)
 *   D24, D25, D34, D35 ficam em LOW (eram os bits 2 e 3 da versao de 4 bits).
 *
 * Comparacao com os botoes, habilitacao, soma e LEDs de status sao feitos
 * pelo circuito externo de CIs 74HC. Este sketch NAO le os botoes.
 *
 * Monitor serial: 9600 baud, final de linha "Nova linha" (ou "Ambos").
 *   TESTE <N0> <N1>   par fixo, dois inteiros de 0 a 1023
 *   ANALOGICO         volta a ler os potenciometros
 */

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

const uint8_t PINO_A0 = 22, PINO_A1 = 23;      // bits do potenciometro 1
const uint8_t PINO_B0 = 32, PINO_B1 = 33;      // bits do potenciometro 2
const uint8_t PINOS_LIVRES[] = {24, 25, 34, 35};

const uint8_t AMOSTRAS = 16;                   // media de 16 leituras
const int HISTERESE = 30;                      // ~3% de 1023
const long CODIGO_MAX = 1023;
const unsigned long PERIODO_MS = 100;          // atualiza os LEDs a cada 100 ms
const unsigned long RELATO_MS = 500;           // imprime no serial a cada 500 ms

bool modoAnalogico = true;
int n0 = 0, n1 = 0;                            // leituras (media) de 0 a 1023
uint8_t a = 0, b = 0;                          // valores de 2 bits (0 a 3)
unsigned long ultimaAmostra = 0, ultimoRelato = 0;

// ---------------- autoteste (sonda no A2) ----------------
const uint8_t PINO_SONDA = A2;
struct Passo { const char *onde; char esperado; const char *dica; };
const char S0o[] PROGMEM = "U6 pino 16 (perna do CI ou furo livre d32)";
const char S0d[] PROGMEM = "U6 sem 5 V: confira o fio vermelho da coluna 32 ao + de cima.";
const char S1o[] PROGMEM = "U6 pino 8 (perna do CI ou furo livre g39)";
const char S1d[] PROGMEM = "U6 sem GND: confira o fio preto da coluna 39 ao - de baixo.";
const char S2o[] PROGMEM = "U6 pino 7 (perna do CI ou furo livre g38)";
const char S2d[] PROGMEM = "Entrada C_in solta: entrada de CI sem fio pode ler 1 e estraga a soma. Ligue o pino 7 do U6 ao GND.";
const char S3o[] PROGMEM = "U6 pino 15 (perna do CI ou furo livre d33)";
const char S3d[] PROGMEM = "Entrada B2 solta: entrada de CI sem fio pode ler 1 e estraga a soma. Ligue o pino 15 do U6 ao GND.";
const char S4o[] PROGMEM = "U6 pino 14 (perna do CI ou furo livre d34)";
const char S4d[] PROGMEM = "Entrada A2 solta: entrada de CI sem fio pode ler 1 e estraga a soma. Ligue o pino 14 do U6 ao GND.";
const char S5o[] PROGMEM = "U6 pino 12 (perna do CI ou furo livre d36)";
const char S5d[] PROGMEM = "Entrada A3 solta: entrada de CI sem fio pode ler 1 e estraga a soma. Ligue o pino 12 do U6 ao GND.";
const char S6o[] PROGMEM = "U6 pino 11 (perna do CI ou furo livre d37)";
const char S6d[] PROGMEM = "Entrada B3 solta: entrada de CI sem fio pode ler 1 e estraga a soma. Ligue o pino 11 do U6 ao GND.";
const char S7o[] PROGMEM = "U4 pino 14 (perna do CI ou furo livre d22)";
const char S7d[] PROGMEM = "U4 sem 5 V: confira o fio vermelho da coluna 22 ao + de cima.";
const char S8o[] PROGMEM = "U4 pino 7 (perna do CI ou furo livre g28)";
const char S8d[] PROGMEM = "U4 sem GND: confira o fio preto da coluna 28 ao - de baixo.";
const char S9o[] PROGMEM = "U3 pino 8 (perna do CI ou furo livre b8) - saida H";
const char S9d[] PROGMEM = "H deveria ser 1 com o pot. 1 em 00 e botoes soltos. Rode o DIAG H.";
const char S10o[] PROGMEM = "U4 pino 2 (perna do CI ou furo livre j23) - H chega";
const char S10d[] PROGMEM = "H nao chega no U4 pino 2. Confira os fios que distribuem o H (U3 pino 8 -> U4 pinos 2, 5, 10 e 13).";
const char S11o[] PROGMEM = "U4 pino 5 (perna do CI ou furo livre i26) - H chega";
const char S11d[] PROGMEM = "H nao chega no U4 pino 5. Confira os fios que distribuem o H (U3 pino 8 -> U4 pinos 2, 5, 10 e 13).";
const char S12o[] PROGMEM = "U4 pino 10 (perna do CI ou furo livre c26) - H chega";
const char S12d[] PROGMEM = "H nao chega no U4 pino 10. Confira os fios que distribuem o H (U3 pino 8 -> U4 pinos 2, 5, 10 e 13).";
const char S13o[] PROGMEM = "U4 pino 13 (perna do CI ou furo livre c23) - H chega";
const char S13d[] PROGMEM = "H nao chega no U4 pino 13. Confira os fios que distribuem o H (U3 pino 8 -> U4 pinos 2, 5, 10 e 13).";
const char S14o[] PROGMEM = "U4 pino 12 (perna do CI ou furo livre c24) - B0 chega do Mega";
const char S14d[] PROGMEM = "B0 nao chega no U4. Confira o fio de b10 da placa 1 ate U4 pino 12.";
const char S15o[] PROGMEM = "U4 pino 9 (perna do CI ou furo livre c27) - B1 chega do Mega";
const char S15d[] PROGMEM = "B1 nao chega no U4. Confira o fio de b8 da placa 1 ate U4 pino 9.";
const char S16o[] PROGMEM = "U4 pino 11 (perna do CI ou furo livre c25) - saida B0e";
const char S16d[] PROGMEM = "As entradas estao em 1 mas a saida B0e nao: o U4 esta invertido, com defeito ou nao e um 08.";
const char S17o[] PROGMEM = "U4 pino 8 (perna do CI ou furo livre c28) - saida B1e";
const char S17d[] PROGMEM = "As entradas estao em 1 mas a saida B1e nao: o U4 esta invertido, com defeito ou nao e um 08.";
const char S18o[] PROGMEM = "U6 pino 6 (perna do CI ou furo livre h37) - B0e chega";
const char S18d[] PROGMEM = "B0e nao chega no U6. Confira o fio de U4 pino 11 ate U6 pino 6.";
const char S19o[] PROGMEM = "U6 pino 2 (perna do CI ou furo livre h33) - B1e chega";
const char S19d[] PROGMEM = "B1e nao chega no U6. Confira o fio de U4 pino 8 ate U6 pino 2.";
const char S20o[] PROGMEM = "U6 pino 5 (perna do CI ou furo livre h36) - A0e";
const char S20d[] PROGMEM = "A0e deveria ser 0 (pot. 1 em 00). Confira o fio de c20 da placa 1 ate U4 pino 4.";
const char S21o[] PROGMEM = "U6 pino 3 (perna do CI ou furo livre h34) - A1e";
const char S21d[] PROGMEM = "A1e deveria ser 0 (pot. 1 em 00). Confira o fio de c18 da placa 1 ate U4 pino 1.";
const char S22o[] PROGMEM = "U6 pino 4 (perna do CI ou furo livre h35) - saida S0";
const char S22d[] PROGMEM = "As entradas do U6 estao certas mas S0 nao: o U6 esta invertido, com defeito ou nao e um 283.";
const char S23o[] PROGMEM = "U6 pino 1 (perna do CI ou furo livre h32) - saida S1";
const char S23d[] PROGMEM = "As entradas do U6 estao certas mas S1 nao: o U6 esta invertido, com defeito ou nao e um 283.";
const char S24o[] PROGMEM = "U6 pino 13 (perna do CI ou furo livre c35) - saida S2";
const char S24d[] PROGMEM = "As entradas do U6 estao certas mas S2 nao: o U6 esta invertido, com defeito ou nao e um 283.";
const char S25o[] PROGMEM = "U6 pino 10 (perna do CI ou furo livre c38) - saida S3";
const char S25d[] PROGMEM = "As entradas do U6 estao certas mas S3 nao: o U6 esta invertido, com defeito ou nao e um 283.";
const char S26o[] PROGMEM = "Placa 1, furo livre g44 - S0 chega na coluna do LED";
const char S26d[] PROGMEM = "S0 sai do U6 mas nao chega na placa 1. Confira o fio do U6 ate j44 da placa 1.";
const char S27o[] PROGMEM = "Placa 1, furo livre b44 - perna longa do LED S0";
const char S27d[] PROGMEM = "Perto de 0 V: o resistor nao atravessa o canal (e44 a f44). Acima de 2,6 V: LED invertido (lado chato no - de cima) ou o - de cima sem GND.";
const char S28o[] PROGMEM = "Placa 1, furo livre g42 - S1 chega na coluna do LED";
const char S28d[] PROGMEM = "S1 sai do U6 mas nao chega na placa 1. Confira o fio do U6 ate j42 da placa 1.";
const char S29o[] PROGMEM = "Placa 1, furo livre b42 - perna longa do LED S1";
const char S29d[] PROGMEM = "Perto de 0 V: o resistor nao atravessa o canal (e42 a f42). Acima de 2,6 V: LED invertido (lado chato no - de cima) ou o - de cima sem GND.";
const char S30o[] PROGMEM = "Placa 1, barramento - de cima (qualquer furo)";
const char S30d[] PROGMEM = "O - de cima da placa 1 nao esta no GND: confira o fio GND do Mega (col 59) e emende o barramento se ele for cortado no meio.";
const Passo PASSOS_S[] PROGMEM = {
  {S0o, '1', S0d},
  {S1o, '0', S1d},
  {S2o, '0', S2d},
  {S3o, '0', S3d},
  {S4o, '0', S4d},
  {S5o, '0', S5d},
  {S6o, '0', S6d},
  {S7o, '1', S7d},
  {S8o, '0', S8d},
  {S9o, '1', S9d},
  {S10o, '1', S10d},
  {S11o, '1', S11d},
  {S12o, '1', S12d},
  {S13o, '1', S13d},
  {S14o, '1', S14d},
  {S15o, '1', S15d},
  {S16o, '1', S16d},
  {S17o, '1', S17d},
  {S18o, '1', S18d},
  {S19o, '1', S19d},
  {S20o, '0', S20d},
  {S21o, '0', S21d},
  {S22o, '1', S22d},
  {S23o, '1', S23d},
  {S24o, '0', S24d},
  {S25o, '0', S25d},
  {S26o, '1', S26d},
  {S27o, 'L', S27d},
  {S28o, '1', S28d},
  {S29o, 'L', S29d},
  {S30o, '0', S30d},
};
const uint8_t N_PASSOS_S = sizeof(PASSOS_S) / sizeof(Passo);
const char H0o[] PROGMEM = "U3 pino 14 (perna do CI ou furo livre d2)";
const char H0d[] PROGMEM = "U3 sem 5 V: confira o fio vermelho da coluna 2 ao + de cima.";
const char H1o[] PROGMEM = "U3 pino 7 (perna do CI ou furo livre g8)";
const char H1d[] PROGMEM = "U3 sem GND: confira o fio preto da coluna 8 ao - de baixo.";
const char H2o[] PROGMEM = "U2 pino 14 (perna do CI ou furo livre d12)";
const char H2d[] PROGMEM = "U2 sem 5 V: confira o fio vermelho da coluna 12 ao + de cima.";
const char H3o[] PROGMEM = "U2 pino 7 (perna do CI ou furo livre g18)";
const char H3d[] PROGMEM = "U2 sem GND: confira o fio preto da coluna 18 ao - de baixo.";
const char H4o[] PROGMEM = "U3 pino 10 (perna do CI ou furo livre d6) - entrada fixa em 1 (inversor)";
const char H4d[] PROGMEM = "O pino 10 do U3 tem que estar no +5 V: sem isso H = DIFERENTE e o circuito inverte tudo. Confira o fio vermelho curto desse pino ao + de cima.";
const char H5o[] PROGMEM = "U3 pino 1 (perna do CI ou furo livre h2) - X1";
const char H5d[] PROGMEM = "X1 errado no U3. Confira o fio de T+2 da placa 1 ate U3 pino 1.";
const char H6o[] PROGMEM = "U3 pino 4 (perna do CI ou furo livre h5) - X0";
const char H6d[] PROGMEM = "X0 errado no U3. Confira o fio de b20 da placa 1 ate U3 pino 4.";
const char H7o[] PROGMEM = "U3 pino 2 (perna do CI ou furo livre h3) - P1 (botao SW2 solto)";
const char H7d[] PROGMEM = "P1 errado no U3. Confira o fio de g56 da placa 1 ate U3 pino 2. Se o botao esta solto e da 1, falta o pull-down de 10 k ou o botao esta fora da diagonal.";
const char H8o[] PROGMEM = "U3 pino 5 (perna do CI ou furo livre h6) - P0 (botao SW1 solto)";
const char H8d[] PROGMEM = "P0 errado no U3. Confira o fio de g60 da placa 1 ate U3 pino 5. Se o botao esta solto e da 1, falta o pull-down de 10 k ou o botao esta fora da diagonal.";
const char H9o[] PROGMEM = "U3 pino 3 (perna do CI ou furo livre h4) - saida d1";
const char H9d[] PROGMEM = "d1 = X1 xor P1 deveria ser 0: o U3 esta invertido, com defeito ou nao e um 86.";
const char H10o[] PROGMEM = "U3 pino 6 (perna do CI ou furo livre h7) - saida d0";
const char H10d[] PROGMEM = "d0 = X0 xor P0 deveria ser 0: o U3 esta invertido, com defeito ou nao e um 86.";
const char H11o[] PROGMEM = "U2 pino 4 (perna do CI ou furo livre h15) - d1 chega";
const char H11d[] PROGMEM = "Confira o fio U3 pino 3 -> U2 pino 4.";
const char H12o[] PROGMEM = "U2 pino 5 (perna do CI ou furo livre h16) - d0 chega";
const char H12d[] PROGMEM = "Confira o fio U3 pino 6 -> U2 pino 5.";
const char H13o[] PROGMEM = "U2 pino 6 (perna do CI ou furo livre i17) - saida DIFERENTE (LED CONFERIR)";
const char H13d[] PROGMEM = "DIFERENTE deveria ser 0: o U2 esta invertido, com defeito ou nao e um 32.";
const char H14o[] PROGMEM = "U3 pino 9 (perna do CI ou furo livre c7) - DIFERENTE chega";
const char H14d[] PROGMEM = "Confira o fio U2 pino 6 -> U3 pino 9.";
const char H15o[] PROGMEM = "U3 pino 8 (perna do CI ou furo livre b8) - saida H = DIFERENTE xor 1";
const char H15d[] PROGMEM = "DIFERENTE = 0 e o pino 10 = 1, mas H nao e 1: o U3 esta com defeito ou nao e um 86.";
const char H16o[] PROGMEM = "U3 pino 12 (perna do CI ou furo livre c4) - H chega";
const char H16d[] PROGMEM = "H nao chega no U3 pino 12. Confira o fio U3 pino 8 -> U3 pino 12.";
const char H17o[] PROGMEM = "U3 pino 13 (perna do CI ou furo livre c3) - S2 chega";
const char H17d[] PROGMEM = "S2 deveria ser 0 (soma = 3). Confira o fio da coluna do LED S2 (i40 da placa 1) ate U3 pino 13.";
const char H18o[] PROGMEM = "U3 pino 11 (perna do CI ou furo livre c5) - saida LIBERADO = H xor S2";
const char H18d[] PROGMEM = "H = 1 e S2 = 0, mas LIBERADO nao e 1: o U3 esta com defeito ou nao e um 86.";
const char H19o[] PROGMEM = "Placa 1, furo livre g34 - LIBERADO chega na coluna do LED";
const char H19d[] PROGMEM = "LIBERADO sai do U3 mas nao chega na placa 1. Confira o fio de U3 pino 11 ate j34 da placa 1.";
const char H20o[] PROGMEM = "Placa 1, furo livre b34 - perna longa do LED LIBERADO";
const char H20d[] PROGMEM = "Perto de 0 V: o resistor nao atravessa o canal (e34 a f34). Acima de 2,6 V: LED invertido ou o - de cima sem GND.";
const char H21o[] PROGMEM = "Placa 1, furo livre g30 - coluna do LED CONFERIR";
const char H21d[] PROGMEM = "CONFERIR deveria estar apagado. Confira o fio de U2 pino 6 ate j30 da placa 1.";
const char H22o[] PROGMEM = "Placa 1, furo livre h32 - coluna do LED ALARME (= S2)";
const char H22d[] PROGMEM = "ALARME deveria estar apagado. Confira o jumper g40 -> j32 da placa 1: ele tem que sair da coluna do LED S2.";
const Passo PASSOS_H[] PROGMEM = {
  {H0o, '1', H0d},
  {H1o, '0', H1d},
  {H2o, '1', H2d},
  {H3o, '0', H3d},
  {H4o, '1', H4d},
  {H5o, '0', H5d},
  {H6o, '0', H6d},
  {H7o, '0', H7d},
  {H8o, '0', H8d},
  {H9o, '0', H9d},
  {H10o, '0', H10d},
  {H11o, '0', H11d},
  {H12o, '0', H12d},
  {H13o, '0', H13d},
  {H14o, '0', H14d},
  {H15o, '1', H15d},
  {H16o, '1', H16d},
  {H17o, '0', H17d},
  {H18o, '1', H18d},
  {H19o, '1', H19d},
  {H20o, 'L', H20d},
  {H21o, '0', H21d},
  {H22o, '0', H22d},
};
const uint8_t N_PASSOS_H = sizeof(PASSOS_H) / sizeof(Passo);
const Passo *diagTabela = 0;         // roteiro em andamento (0 = nenhum)
uint8_t diagTotal = 0, diagPasso = 0, diagErros = 0;
int diagPrimeiro = -1;

int lerMedia(uint8_t canal);
uint8_t quantizar(int leitura, uint8_t atual);
void publicar();
void relatar();
void imprimirCanal(const __FlashStringHelper *nome, int leitura, uint8_t valor);
void lerSerial();
void interpretar(char *linha);
void rejeitar();
bool lerInteiro(char *&p, long &v);
bool naFaixa(long v);
bool somenteEspacos(const char *s);
bool emDiag();
void iniciarDiag(const Passo *tabela, uint8_t total, char nome);
void mostrarPasso();
void medirPasso();
void encerrarDiag();
long lerSondaMv();
void imprimirVolts(long mv);

void setup() {
  Serial.begin(9600);
  pinMode(PINO_A0, OUTPUT);
  pinMode(PINO_A1, OUTPUT);
  pinMode(PINO_B0, OUTPUT);
  pinMode(PINO_B1, OUTPUT);
  for (uint8_t i = 0; i < sizeof(PINOS_LIVRES); i++) {
    pinMode(PINOS_LIVRES[i], OUTPUT);
    digitalWrite(PINOS_LIVRES[i], LOW);
  }
  // valor inicial sem histerese, para comecar na faixa certa
  n0 = lerMedia(A0);
  n1 = lerMedia(A1);
  a = n0 >> 8;
  b = n1 >> 8;
  publicar();
  Serial.println(F("Conferencia de carga - AP1 2026.2 - versao 2 bits"));
  Serial.println(F("Comandos: TESTE <N0> <N1> | ANALOGICO"));
  Serial.println(F("Modo atual: ANALOGICO"));
}

void loop() {
  lerSerial();

  if (millis() - ultimaAmostra >= PERIODO_MS) {
    ultimaAmostra = millis();
    if (modoAnalogico) {
      n0 = lerMedia(A0);
      n1 = lerMedia(A1);
      a = quantizar(n0, a);
      b = quantizar(n1, b);
    }
    publicar();
  }

  if (!emDiag() && millis() - ultimoRelato >= RELATO_MS) {   // no autoteste a tela fica so com os passos
    ultimoRelato = millis();
    relatar();
  }
}

// Media de 16 leituras. A primeira leitura apos trocar de canal e descartada,
// porque o conversor ainda pode estar com a tensao do canal anterior.
int lerMedia(uint8_t canal) {
  analogRead(canal);
  unsigned int soma = 0;                       // 16 x 1023 = 16368, cabe
  for (uint8_t i = 0; i < AMOSTRAS; i++) soma += analogRead(canal);
  return soma / AMOSTRAS;
}

// Converte 0..1023 em 0..3 com histerese. So muda de faixa quando a leitura
// passa a fronteira por mais de HISTERESE contagens; perto da fronteira,
// fica na faixa vizinha mais proxima da atual.
uint8_t quantizar(int leitura, uint8_t atual) {
  uint8_t alvo = leitura >> 8;                 // faixa sem histerese
  if (alvo == atual) return atual;
  if (alvo > atual) {                          // subindo: fronteira = 256 * alvo
    if (leitura >= 256 * alvo + HISTERESE) return alvo;
    return alvo - 1;
  }
  // descendo: fronteira = 256 * (alvo + 1)
  if (leitura < 256 * (alvo + 1) - HISTERESE) return alvo;
  return alvo + 1;
}

// Escreve os 2 bits de cada valor nos pinos (LEDs e entradas dos CIs).
void publicar() {
  digitalWrite(PINO_A1, (a >> 1) & 1);
  digitalWrite(PINO_A0, a & 1);
  digitalWrite(PINO_B1, (b >> 1) & 1);
  digitalWrite(PINO_B0, b & 1);
}

// Ex.: [ANALOGICO] POT1: 612 (59%) -> 10 (2)  |  POT2: 130 (12%) -> 00 (0)
void relatar() {
  Serial.print(modoAnalogico ? F("[ANALOGICO] ") : F("[TESTE]     "));
  imprimirCanal(F("POT1"), n0, a);
  Serial.print(F("  |  "));
  imprimirCanal(F("POT2"), n1, b);
  Serial.println();
}

void imprimirCanal(const __FlashStringHelper *nome, int leitura, uint8_t valor) {
  Serial.print(nome);
  Serial.print(F(": "));
  Serial.print(leitura);
  Serial.print(F(" ("));
  Serial.print((long)leitura * 100 / CODIGO_MAX);
  Serial.print(F("%) -> "));
  Serial.print((valor >> 1) & 1);
  Serial.print(valor & 1);
  Serial.print(F(" ("));
  Serial.print(valor);
  Serial.print(F(")"));
}

// Acumula caracteres ate o final de linha (\n ou \r); so entao interpreta.
void lerSerial() {
  static char linha[32];
  static uint8_t n = 0;
  static bool estourou = false;

  while (Serial.available()) {
    char c = Serial.read();
    if (c != '\n' && c != '\r') {
      if (n < sizeof(linha) - 1) linha[n++] = c;
      else estourou = true;
      continue;
    }
    linha[n] = '\0';
    if (estourou) rejeitar();
    else if (n > 0) interpretar(linha);
    n = 0;
    estourou = false;
  }
}

void interpretar(char *linha) {
  for (char *p = linha; *p; p++) *p = toupper(*p);
  while (*linha == ' ') linha++;
  for (int k = strlen(linha) - 1; k >= 0 && linha[k] == ' '; k--) linha[k] = '\0';

  if (emDiag()) {                    // durante o autoteste: M mede, SAIR encerra
    if (strcmp(linha, "SAIR") == 0) encerrarDiag();
    else medirPasso();
    return;
  }
  if (strcmp(linha, "DIAG S") == 0) { iniciarDiag(PASSOS_S, N_PASSOS_S, 'S'); return; }
  if (strcmp(linha, "DIAG H") == 0) { iniciarDiag(PASSOS_H, N_PASSOS_H, 'H'); return; }

  if (strcmp(linha, "ANALOGICO") == 0) {
    modoAnalogico = true;
    Serial.println(F("Modo atual: ANALOGICO"));
    return;
  }

  if (strncmp(linha, "TESTE ", 6) == 0) {
    char *p = linha + 6;
    long v0, v1;
    if (lerInteiro(p, v0) && lerInteiro(p, v1) && somenteEspacos(p) && naFaixa(v0) && naFaixa(v1)) {
      modoAnalogico = false;
      n0 = v0;
      n1 = v1;
      a = n0 >> 8;                             // no teste, sem histerese
      b = n1 >> 8;
      Serial.println(F("Modo atual: TESTE"));
      return;
    }
  }
  rejeitar();
}

void rejeitar() {
  Serial.println(F("Comando invalido - par vigente mantido"));
  Serial.println(F("Use: TESTE <0-1023> <0-1023> | ANALOGICO | DIAG S | DIAG H"));
}

bool lerInteiro(char *&p, long &v) {
  char *fim;
  v = strtol(p, &fim, 10);
  if (fim == p) return false;
  p = fim;
  return true;
}

bool naFaixa(long v) {
  return v >= 0 && v <= CODIGO_MAX;
}

bool somenteEspacos(const char *s) {
  while (*s) {
    if (!isspace(*s++)) return false;
  }
  return true;
}

// ======================= autoteste =======================
bool emDiag() { return diagTabela != 0; }

void iniciarDiag(const Passo *tabela, uint8_t total, char nome) {
  modoAnalogico = false;
  n0 = 0; n1 = 1023;
  a = 0;                             // pot. 1 = 00
  b = 3;                             // pot. 2 = 11 -> com os botoes soltos: H = 1, S = 0011
  publicar();
  diagTabela = tabela; diagTotal = total; diagPasso = 0; diagErros = 0; diagPrimeiro = -1;
  Serial.println();
  Serial.print(F("=== AUTOTESTE DIAG ")); Serial.print(nome); Serial.println(F(" ==="));
  Serial.println(F("Valores fixos: pot. 1 = 00 e pot. 2 = 11 (TESTE 0 1023). Deixe os DOIS botoes SOLTOS."));
  Serial.println(F("Ligue um jumper no pino A2 do Mega. Em cada passo, encoste a outra ponta"));
  Serial.println(F("no ponto pedido, digite M e aperte Enter. Digite SAIR para parar."));
  mostrarPasso();
}

void mostrarPasso() {
  Passo p;
  memcpy_P(&p, &diagTabela[diagPasso], sizeof(Passo));
  Serial.println();
  Serial.print(F("Passo ")); Serial.print(diagPasso + 1); Serial.print('/'); Serial.print(diagTotal);
  Serial.print(F(": ")); Serial.println((const __FlashStringHelper *)p.onde);
  Serial.print(F("  esperado: "));
  if (p.esperado == '1') Serial.println(F("1 (acima de 2,4 V)"));
  else if (p.esperado == '0') Serial.println(F("0 (abaixo de 0,8 V)"));
  else Serial.println(F("LED aceso (entre 1,4 e 2,6 V)"));
}

void medirPasso() {
  Passo p;
  memcpy_P(&p, &diagTabela[diagPasso], sizeof(Passo));
  long mv = lerSondaMv();
  bool ok;
  if (p.esperado == '1') ok = mv >= 2400;
  else if (p.esperado == '0') ok = mv <= 800;
  else ok = mv >= 1400 && mv <= 2600;
  Serial.print(F("  medido: ")); imprimirVolts(mv);
  if (ok) {
    Serial.println(F(" -> OK"));
  } else {
    Serial.println(F(" -> ERRO"));
    Serial.print(F("  ")); Serial.println((const __FlashStringHelper *)p.dica);
    diagErros++;
    if (diagPrimeiro < 0) diagPrimeiro = diagPasso;
  }
  diagPasso++;
  if (diagPasso < diagTotal) { mostrarPasso(); return; }

  Serial.println();
  if (diagErros == 0) {
    Serial.println(F("RESULTADO: tudo certo neste caminho."));
  } else {
    Passo q;
    memcpy_P(&q, &diagTabela[diagPrimeiro], sizeof(Passo));
    Serial.print(F("RESULTADO: ")); Serial.print(diagErros);
    Serial.println(F(" ponto(s) com erro. Corrija primeiro o do passo abaixo e rode de novo:"));
    Serial.print(F("  passo ")); Serial.print(diagPrimeiro + 1); Serial.print(F(": "));
    Serial.println((const __FlashStringHelper *)q.onde);
    Serial.print(F("  ")); Serial.println((const __FlashStringHelper *)q.dica);
  }
  encerrarDiag();
}

void encerrarDiag() {
  diagTabela = 0;
  Serial.println(F("Autoteste encerrado. Continua em modo TESTE com pot. 1 = 00 e pot. 2 = 11."));
}

// Media de 16 leituras do A2 em milivolts (a primeira leitura apos trocar de canal e descartada).
long lerSondaMv() {
  analogRead(PINO_SONDA);
  long soma = 0;
  for (uint8_t i = 0; i < 16; i++) soma += analogRead(PINO_SONDA);
  return soma * 5000L / (1023L * 16L);
}

void imprimirVolts(long mv) {
  Serial.print(mv / 1000);
  Serial.print(',');
  long cent = (mv % 1000) / 10;
  if (cent < 10) Serial.print('0');
  Serial.print(cent);
  Serial.print(F(" V"));
}
