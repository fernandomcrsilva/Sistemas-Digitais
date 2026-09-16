// Teste do sketch no PC, sem Arduino: simula Serial, millis() e analogRead()
// e confere o formato da saida serial, os pinos e o parser do modo de teste.
//
//   g++ -std=gnu++11 -Isketch sketch/teste_host.cpp -o /tmp/teste_host && /tmp/teste_host
//
// Deve terminar com "teste_host: OK". Nao faz parte do sketch entregue.
#include <cassert>
#include <cctype>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#define OUTPUT 1
#define A0 54
#define A1 55
#define F(x) x

static std::string entrada, saida;
static unsigned long agora = 0;
static int adc[2] = {0, 0};
static int pinos[64];

struct SerialSim {
  void begin(long) {}
  void print(const char *s) { saida += s; }
  void print(int v) { saida += std::to_string(v); }
  void println(const char *s) { saida += s; saida += "\n"; }
  int available() { return (int)entrada.size(); }
  char read() { char c = entrada[0]; entrada.erase(0, 1); return c; }
} Serial;
void pinMode(uint8_t, uint8_t) {}
void digitalWrite(uint8_t p, uint8_t v) { pinos[p] = v; }
int analogRead(uint8_t p) { return adc[p - A0]; }
unsigned long millis() { return agora; }

#include "conferencia_carga.ino"

// Envia um comando (opcional), avanca 100 ms e roda uma volta do loop.
static void passo(const char *cmd = nullptr) {
  saida.clear();
  if (cmd) entrada += cmd;
  agora += 100;
  loop();
}

static std::string bits(int p0, int n) {
  std::string s;
  for (int i = n - 1; i >= 0; i--) s += pinos[p0 + i] ? '1' : '0';
  return s;
}

static bool tem(const char *s) { return saida.find(s) != std::string::npos; }

int main() {
  setup();
  adc[0] = 18;                                   // N0 = 18 -> X = 2, A = 2
  adc[1] = 5;                                    // N1 = 5  -> B = 1
  passo();
  assert(saida == "[ANALOGICO] N0 = 18 (0000010010)  N1 = 5 (0000000101)\n");
  assert(bits(22, 10) == "0000010010" && bits(32, 2) == "01");

  passo("TESTE 1023 0\n");
  assert(tem("Modo atual: TESTE"));
  assert(tem("[TESTE]     N0 = 1023 (1111111111)  N1 = 0 (0000000000)"));
  assert(bits(22, 10) == "1111111111" && bits(32, 2) == "00");

  // invalidos: rejeitados sem alterar o par nem o modo
  const char *ruins[] = {"TESTE 1024 0\n", "TESTE -1 5\n", "TESTE 5\n", "TESTE 5 5 5\n", "TESTE 5.5 3\n",
                         "TESTE 65541 0\n", "TESTE 99999999999999999999 0\n", "TESTEX 1 2\n", "TESTE1 2\n",
                         "XYZ\n", "ANALOGICO 1\n"};
  for (const char *r : ruins) {
    passo(r);
    assert(tem("Comando invalido"));
    assert(tem("[TESTE]     N0 = 1023 (1111111111)  N1 = 0 (0000000000)"));
    assert(bits(22, 10) == "1111111111" && bits(32, 2) == "00");
  }

  passo("teste 2 3\r\n");                        // minusculas e CR+LF
  assert(tem("Modo atual: TESTE") && tem("N0 = 2 (0000000010)  N1 = 3 (0000000011)"));
  assert(bits(22, 10) == "0000000010" && bits(32, 2) == "11");

  passo("ANALOGICO\r");                          // so CR
  assert(tem("Modo atual: ANALOGICO") && tem("[ANALOGICO] N0 = 18 (0000010010)  N1 = 5 (0000000101)"));
  assert(bits(22, 10) == "0000010010" && bits(32, 2) == "01");

  passo("TESTE 7 7                                              x\n");   // longa demais
  assert(tem("Comando invalido") && tem("[ANALOGICO] N0 = 18"));

  passo("\n");                                   // linha vazia: ignorada
  assert(!tem("Comando invalido") && tem("[ANALOGICO] N0 = 18"));

  puts("teste_host: OK");
  return 0;
}
