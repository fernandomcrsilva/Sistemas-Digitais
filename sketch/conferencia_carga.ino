/*
 * Trabalho AP1 - Sistemas Digitais 2026.2 - Turma 6a
 * Conferencia de carga para inspecao - Arduino Mega 2560
 * Prof. Clayton J A Silva - Entrega: 02/10/2026
 *
 * Integrantes:
 *   <NOME COMPLETO> - <MATRICULA>   (representante)
 *   <NOME COMPLETO> - <MATRICULA>
 *   <NOME COMPLETO> - <MATRICULA>
 *
 * Escopo do firmware (item 5.1 do enunciado): adquirir N0 (A0) e N1 (A1) a
 * cada ~100 ms, publicar os bits em D22-D33 e relatar o par no monitor serial.
 * Validacao de X, comparacao com os push-buttons, habilitacao, soma e LEDs de
 * status sao feitos pelo circuito externo - este sketch NAO le botoes e NAO
 * calcula FALHA, IGUAL, H, S nem CONFERIR/ALARME/LIBERADO.
 *
 * Pinos: D22 = bit 0 ... D31 = bit 9 de N0;  D32 = bit 0 e D33 = bit 1 de N1.
 *
 * Monitor serial: 9600 baud, final de linha "Nova linha" (ou "Ambos").
 *   TESTE <N0> <N1>   par fixo, dois inteiros de 0 a 1023 (item 4.3)
 *   ANALOGICO         retoma a leitura dos potenciometros
 * Comando ou valor invalido e rejeitado sem alterar o par vigente.
 */

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

const uint8_t PINO_N0 = 22;          // D22 = bit 0 ... D31 = bit 9 de N0
const uint8_t PINO_N1 = 32;          // D32 = bit 0, D33 = bit 1 de N1
const uint8_t BITS_N0 = 10;
const uint8_t BITS_N1 = 2;           // so os 2 bits inferiores alimentam B
const long CODIGO_MAX = 1023;
const unsigned long PERIODO_MS = 100;

bool modoAnalogico = true;
int n0 = 0;                          // par vigente: sempre o que esta nos pinos
int n1 = 0;
unsigned long ultimaAmostra = 0;

void adquirir();
void publicar(int v0, int v1);
void imprimirBinario10(int v);
void relatar();
void lerSerial();
void interpretar(char *linha);
void rejeitar();
bool lerInteiro(char *&p, long &v);
bool naFaixa(long v);
bool somenteEspacos(const char *s);

void setup() {
  Serial.begin(9600);
  for (uint8_t i = 0; i < BITS_N0; i++) pinMode(PINO_N0 + i, OUTPUT);
  for (uint8_t i = 0; i < BITS_N1; i++) pinMode(PINO_N1 + i, OUTPUT);
  publicar(n0, n1);
  Serial.println(F("Conferencia de carga - AP1 2026.2"));
  Serial.println(F("Comandos: TESTE <N0> <N1> | ANALOGICO"));
  Serial.println(F("Modo atual: ANALOGICO"));
}

void loop() {
  lerSerial();

  if (millis() - ultimaAmostra >= PERIODO_MS) {
    ultimaAmostra = millis();
    adquirir();
    publicar(n0, n1);                // pinos e serial sempre com o mesmo par
    relatar();
  }
}

// Amostra os dois canais em sequencia. No modo TESTE o par fixo permanece.
void adquirir() {
  if (!modoAnalogico) return;
  n0 = analogRead(A0);
  n1 = analogRead(A1);
}

// Espelha os bits do par vigente nos pinos digitais (item 5.2 do enunciado).
void publicar(int v0, int v1) {
  for (uint8_t i = 0; i < BITS_N0; i++) digitalWrite(PINO_N0 + i, (v0 >> i) & 1);
  for (uint8_t i = 0; i < BITS_N1; i++) digitalWrite(PINO_N1 + i, (v1 >> i) & 1);
}

// Serial.print(v, BIN) suprime zeros a esquerda; imprime bit a bit, 10 digitos.
void imprimirBinario10(int v) {
  for (int8_t i = BITS_N0 - 1; i >= 0; i--) Serial.print((v >> i) & 1);
}

// Uma linha por atualizacao, com o modo atual e o par em decimal e binario.
void relatar() {
  Serial.print(modoAnalogico ? F("[ANALOGICO] ") : F("[TESTE]     "));
  Serial.print(F("N0 = "));
  Serial.print(n0);
  Serial.print(F(" ("));
  imprimirBinario10(n0);
  Serial.print(F(")  N1 = "));
  Serial.print(n1);
  Serial.print(F(" ("));
  imprimirBinario10(n1);
  Serial.println(F(")"));
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
      else estourou = true;          // linha longa demais: rejeita inteira
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
  for (char *p = linha; *p; p++) *p = toupper(*p);   // aceita minusculas
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
      Serial.println(F("Modo atual: TESTE"));
      return;
    }
  }
  rejeitar();
}

// Rejeicao: nao altera o modo nem o par vigente (item 4.3 do enunciado).
void rejeitar() {
  Serial.println(F("Comando invalido - par vigente mantido"));
  Serial.println(F("Use: TESTE <0-1023> <0-1023> | ANALOGICO"));
}

// Le um inteiro decimal a partir de p e avanca p. Estouro satura em
// LONG_MAX/LONG_MIN, que cai fora da faixa e e rejeitado por naFaixa.
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

// Recusa lixo depois dos dois inteiros ("TESTE 5 5 xyz").
bool somenteEspacos(const char *s) {
  while (*s) {
    if (!isspace(*s++)) return false;
  }
  return true;
}
