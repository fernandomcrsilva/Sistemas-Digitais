#include "mock.h"
#include "../sketch/conferencia_carga.ino"
#include <cassert>
static int potA(){ return PIN[22] | (PIN[23] << 1); }
static int potB(){ return PIN[32] | (PIN[33] << 1); }
static void step(int ms){ for(int i=0;i<ms;i++){ NOW++; loop(); } }
static std::string lastline(){ auto &o=Serial.out; if(o.empty()) return ""; size_t e=o.size()-1; size_t b=o.rfind('\n', e-1); return o.substr(b==std::string::npos?0:b+1, e-(b==std::string::npos?0:b+1)); }
int main(){
  int falhas = 0;
  setup();
  for(int p: {22,23,32,33,24,25,34,35}) if(PMODE[p]!=OUTPUT){ printf("pino %d nao e saida\n", p); falhas++; }
  for(int p: {24,25,34,35}) if(PIN[p]!=0){ printf("pino %d nao esta em LOW\n", p); falhas++; }
  // 1) subida e descida lentas: onde troca de faixa (com histerese)
  std::string up, down; int last = potA();
  for(int v=0; v<=1023; v++){ ANALOG[A0]=v; step(100); if(potA()!=last){ up += std::to_string(v)+"->"+std::to_string(potA())+" "; last=potA(); } }
  for(int v=1023; v>=0; v--){ ANALOG[A0]=v; step(100); if(potA()!=last){ down += std::to_string(v)+"->"+std::to_string(potA())+" "; last=potA(); } }
  printf("subindo:  %s\ndescendo: %s\n", up.c_str(), down.c_str());
  if(up != "286->1 542->2 798->3 " || down != "737->2 481->1 225->0 "){ printf("FALHA nas trocas de faixa\n"); falhas++; }
  // 2) parado em cima de cada fronteira com ruido de +-25: nao pode piscar
  NOISE = 25;
  for(int b: {256, 512, 768}){
    for(int start: {b-60, b+60}){
      ANALOG[A0]=start; step(500);
      ANALOG[A0]=b; step(300); int ref=potA(), trocas=0;
      for(int k=0;k<300;k++){ step(100); if(potA()!=ref){ trocas++; ref=potA(); } }
      printf("parado em %d (vindo de %d), ruido +-25, 30 s: %d trocas\n", b, start, trocas);
      if(trocas){ falhas++; }
    }
  }
  NOISE = 0;
  // 3) os dois canais sao independentes
  ANALOG[A0]=100; ANALOG[A1]=900; step(500);
  printf("A0=100 A1=900 -> pot1=%d pot2=%d\n", potA(), potB()); if(potA()!=0||potB()!=3) falhas++;
  // 4) TESTE com todos os valores 0..1023 nos dois canais
  int bad=0;
  for(int v=0; v<1024; v++){ Serial.send("TESTE "+std::to_string(v)+" "+std::to_string(1023-v)+"\n"); step(120);
    if(potA()!=(v>>8) || potB()!=((1023-v)>>8)) bad++; }
  printf("TESTE 0..1023: %d erros\n", bad); falhas += bad;
  // 5) linha do serial
  Serial.out.clear(); Serial.send("TESTE 640 300\n"); step(600);
  printf("serial: [%s]\n", lastline().c_str());
  if(lastline()!="[TESTE]     POT1: 640 (62%) -> 10 (2)  |  POT2: 300 (29%) -> 01 (1)") falhas++;
  // 6) comandos invalidos mantem o par
  for(const char* r: {"TESTE 2000 1\n","TESTE 5\n","abc\n","TESTE -1 3\n","TESTE 5 2 xyz\n"}){
    Serial.out.clear(); Serial.send(r); step(120);
    bool ok = Serial.out.find("Comando invalido")!=std::string::npos && potA()==2 && potB()==1;
    if(!ok){ printf("nao rejeitou %s", r); falhas++; } }
  printf("comandos invalidos: rejeitados sem mudar o par\n");
  Serial.send("teste 1023 0\r\n"); step(120); if(potA()!=3||potB()!=0){ printf("minusculas/CRLF falhou\n"); falhas++; }
  // 7) pares para o teste de ponta a ponta (lidos pelo script python)
  FILE* f=fopen("pares_e2e.txt","w");
  int V[4]={128,384,640,896};
  for(int a=0;a<4;a++) for(int b=0;b<4;b++){ Serial.send("TESTE "+std::to_string(V[a])+" "+std::to_string(V[b])+"\n"); step(120);
    fprintf(f,"%d %d %d %d %d %d\n", V[a], V[b], PIN[23], PIN[22], PIN[33], PIN[32]); }
  fclose(f);
  if(falhas) printf("RESULTADO: %d falha(s)\n", falhas); else printf("RESULTADO: sketch OK\n");
  return falhas != 0;
}
