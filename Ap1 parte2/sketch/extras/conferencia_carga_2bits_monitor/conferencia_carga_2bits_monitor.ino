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
 * >>> VERSAO COM MONITOR DAS SAIDAS (para testes) <<<
 * Faz tudo o que o sketch principal faz e tambem LE as saidas do circuito,
 * sem calcular nem acionar nada: a logica continua toda nos CIs. Cada linha
 * do monitor serial mostra S3..S0, CONFERIR, ALARME, LIBERADO e os botoes,
 * e compara com o resultado esperado para os valores e os botoes.
 *
 * Ligacoes extras (jumpers do Mega ate as protoboards):
 *   A2 <- S0 (placa 1, g44)   A3 <- S1 (placa 1, g42)   A4 <- S2 (placa 2, c35 = U6 pino 13)
 *   A5 <- S3 (placa 1, g38)   A6 <- CONFERIR (placa 1, g30)   A7 <- ALARME (placa 1, g32)
 *   A8 <- LIBERADO (placa 1, g34)   A9 <- P1 / SW2 (placa 1, i56)   A10 <- P0 / SW1 (placa 1, i60)
 * Comandos extras: STATUS (tabela detalhada com tensoes), PAUSA, CONTINUA.
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

// ---------------- monitor das saidas do circuito ----------------
const uint8_t N_SINAIS = 9;
const uint8_t PINO_SINAL[N_SINAIS] = {A2, A3, A4, A5, A6, A7, A8, A9, A10};
enum { S0_, S1_, S2_, S3_, CONF_, AL_, LIB_, P1_, P0_ };
const char NOME0[] PROGMEM = "S0";
const char NOME1[] PROGMEM = "S1";
const char NOME2[] PROGMEM = "S2";
const char NOME3[] PROGMEM = "S3";
const char NOME4[] PROGMEM = "CONFERIR";
const char NOME5[] PROGMEM = "ALARME";
const char NOME6[] PROGMEM = "LIBERADO";
const char NOME7[] PROGMEM = "P1 (SW2)";
const char NOME8[] PROGMEM = "P0 (SW1)";
const char *const NOME_SINAL[N_SINAIS] PROGMEM = {NOME0, NOME1, NOME2, NOME3, NOME4, NOME5, NOME6, NOME7, NOME8};
bool pausado = false;                // PAUSA: para as linhas automaticas

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
long lerMv(uint8_t pino);
char nivel(long mv);
void lerCircuito(char lv[], long mv[]);
bool esperado(char p1, char p0, char esp[]);
void imprimirVolts(long mv);
void imprimirStatus();

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

  if (!pausado && millis() - ultimoRelato >= RELATO_MS) {
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

  char lv[N_SINAIS]; long mv[N_SINAIS];
  lerCircuito(lv, mv);
  Serial.print(F("  | S="));
  for (int8_t i = S3_; i >= S0_; i--) Serial.print(lv[i]);
  Serial.print(F(" CONF=")); Serial.print(lv[CONF_]);
  Serial.print(F(" AL="));   Serial.print(lv[AL_]);
  Serial.print(F(" LIB="));  Serial.print(lv[LIB_]);
  Serial.print(F(" | P1P0=")); Serial.print(lv[P1_]); Serial.print(lv[P0_]);
  char esp[7];
  if (!esperado(lv[P1_], lv[P0_], esp)) { Serial.println(F(" | botoes ??")); return; }
  bool ok = true;
  for (uint8_t i = 0; i < 7; i++) if (lv[i] != esp[i]) ok = false;
  if (ok) { Serial.println(F(" | OK")); return; }
  Serial.print(F(" | ERRO, esperado S="));
  for (int8_t i = S3_; i >= S0_; i--) Serial.print(esp[i]);
  Serial.print(F(" CONF=")); Serial.print(esp[CONF_]);
  Serial.print(F(" AL="));   Serial.print(esp[AL_]);
  Serial.print(F(" LIB="));  Serial.println(esp[LIB_]);
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

  if (strcmp(linha, "STATUS") == 0) { pausado = true; imprimirStatus(); return; }
  if (strcmp(linha, "PAUSA") == 0) { pausado = true; Serial.println(F("Linhas automaticas pausadas. Digite CONTINUA para voltar.")); return; }
  if (strcmp(linha, "CONTINUA") == 0) { pausado = false; return; }

  if (strcmp(linha, "ANALOGICO") == 0) {
    pausado = false;
    modoAnalogico = true;
    Serial.println(F("Modo atual: ANALOGICO"));
    return;
  }

  if (strncmp(linha, "TESTE ", 6) == 0) {
    char *p = linha + 6;
    long v0, v1;
    if (lerInteiro(p, v0) && lerInteiro(p, v1) && somenteEspacos(p) && naFaixa(v0) && naFaixa(v1)) {
      modoAnalogico = false;
      pausado = false;
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
  Serial.println(F("Use: TESTE <0-1023> <0-1023> | ANALOGICO | STATUS | PAUSA | CONTINUA"));
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

// ======================= monitor das saidas =======================
// Tensao media em milivolts num pino analogico (descarta a 1a leitura apos trocar de canal).
long lerMv(uint8_t pino) {
  analogRead(pino);
  long soma = 0;
  for (uint8_t i = 0; i < 4; i++) soma += analogRead(pino);
  return soma * 5000L / (1023L * 4L);
}

// 1 a partir de 2,4 V, 0 ate 0,8 V, ? no meio (fio solto ou disputa).
char nivel(long mv) {
  if (mv >= 2400) return '1';
  if (mv <= 800) return '0';
  return '?';
}

void lerCircuito(char lv[], long mv[]) {
  for (uint8_t i = 0; i < N_SINAIS; i++) {
    mv[i] = lerMv(PINO_SINAL[i]);
    lv[i] = nivel(mv[i]);
  }
}

// Resultado esperado pelo esquema para os valores vigentes (a, b) e os botoes lidos.
// So para conferencia: nada disso aciona o circuito.
bool esperado(char p1, char p0, char esp[]) {
  if (p1 == '?' || p0 == '?') return false;
  int r1 = p1 - '0', r0 = p0 - '0';
  int dif = (((a >> 1) & 1) ^ r1) | ((a & 1) ^ r0);   // DIFERENTE = CONFERIR
  int h = !dif;                                       // H = DIFERENTE xor 1
  int s = h ? a + b : 0;
  int s2 = (s >> 2) & 1;                              // ALARME = S2
  for (uint8_t i = 0; i < 4; i++) esp[i] = '0' + ((s >> i) & 1);
  esp[CONF_] = '0' + dif;
  esp[AL_] = '0' + s2;
  esp[LIB_] = '0' + (h ^ s2);                         // LIBERADO = H xor S2
  return true;
}

void imprimirVolts(long mv) {
  Serial.print(mv / 1000);
  Serial.print(',');
  long cent = (mv % 1000) / 10;
  if (cent < 10) Serial.print('0');
  Serial.print(cent);
  Serial.print(F(" V"));
}

void imprimirStatus() {
  char lv[N_SINAIS]; long mv[N_SINAIS]; char esp[7];
  lerCircuito(lv, mv);
  bool temEsp = esperado(lv[P1_], lv[P0_], esp);
  Serial.println();
  Serial.print(F("--- STATUS DO CIRCUITO  (POT1 = ")); Serial.print((a >> 1) & 1); Serial.print(a & 1);
  Serial.print(F(", POT2 = ")); Serial.print((b >> 1) & 1); Serial.print(b & 1); Serial.println(F(") ---"));
  uint8_t erros = 0;
  for (uint8_t i = 0; i < N_SINAIS; i++) {
    const char *nome = (const char *)pgm_read_ptr(&NOME_SINAL[i]);
    Serial.print((const __FlashStringHelper *)nome);
    for (uint8_t k = strlen_P(nome); k < 10; k++) Serial.print(' ');
    imprimirVolts(mv[i]);
    Serial.print(F("  -> ")); Serial.print(lv[i]);
    if (i < 7 && temEsp) {
      Serial.print(F("   esperado ")); Serial.print(esp[i]);
      if (lv[i] == esp[i]) Serial.println(F("   OK"));
      else { Serial.println(F("   ERRO")); erros++; }
    } else {
      Serial.println();
    }
  }
  if (!temEsp) Serial.println(F("Botoes com leitura ?: confira os fios do A9 (i56) e do A10 (i60)."));
  else if (erros == 0) Serial.println(F("Resultado: tudo certo."));
  else { Serial.print(F("Resultado: ")); Serial.print(erros); Serial.println(F(" saida(s) diferente(s) do esperado.")); }
  Serial.println(F("Linhas automaticas pausadas. Digite CONTINUA (ou um novo TESTE) para voltar."));
}
