#include <cstdint>
#include <cstdio>
#include <string>
#include <deque>
#include <random>
#include <ctype.h>
#include <stdlib.h>
#include <string.h>
struct __FlashStringHelper;
#define F(s) ((const __FlashStringHelper *)(s))
#define OUTPUT 1
#define LOW 0
#define HIGH 1
#define A0 54
#define A1 55
static int PIN[70]; static int PMODE[70]; static unsigned long NOW = 0; static int ANALOG[70]; static int NOISE = 0; static long READS = 0;
static std::mt19937 rng(1234);
inline void pinMode(int p, int m){ PMODE[p]=m; }
inline void digitalWrite(int p, int v){ PIN[p]= v?1:0; }
inline int analogRead(int p){ READS++; int v = ANALOG[p]; if (NOISE) v += (int)(rng() % (2*NOISE+1)) - NOISE; return v < 0 ? 0 : v > 1023 ? 1023 : v; }
inline unsigned long millis(){ return NOW; }
struct SerialMock {
  std::deque<char> in; std::string out;
  void begin(long){}
  int available(){ return (int)in.size(); }
  int read(){ char c=in.front(); in.pop_front(); return c; }
  void print(const char*s){ out+=s; }
  void print(const __FlashStringHelper*s){ out+=(const char*)s; }
  void print(int v){ out+=std::to_string(v); }
  void print(unsigned v){ out+=std::to_string(v); }
  void print(long v){ out+=std::to_string(v); }
  void print(unsigned char v){ out+=std::to_string((int)v); }
  void print(char c){ out+=c; }
  void println(const char*s){ out+=s; out+="\n"; }
  void println(const __FlashStringHelper*s){ out+=(const char*)s; out+="\n"; }
  void println(){ out+="\n"; }
  void send(const std::string&s){ for(char c: s) in.push_back(c); }
} Serial;
