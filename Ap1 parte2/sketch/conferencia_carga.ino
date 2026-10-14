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

  if (millis() - ultimoRelato >= RELATO_MS) {
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
  Serial.println(F("Use: TESTE <0-1023> <0-1023> | ANALOGICO"));
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
