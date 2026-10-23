/*
  HIGROLAR - AP2 (UFPI 2026.2)
  ESP32 + DHT11 + OLED SSD1306 + Wi-Fi + MQTT (EMQX)

  Baseado no firmware da AP1 e no Laboratorio 03 da disciplina.
  Bibliotecas: DHT sensor library (Adafruit), Adafruit GFX, Adafruit SSD1306,
               ArduinoJson 7, MQTT (Joel Gaehwiler, arduino-mqtt).

  Topicos:
    ufpi-iot26/<EQUIPE>/<NO>/telemetria : publicacao QoS 1, nao retida
    ufpi-iot26/<EQUIPE>/<NO>/status     : online/offline, retido, QoS 1
    ufpi-iot26/<EQUIPE>/<NO>/config     : assina QoS 1

  secrets.h deve definir:
    WIFI_SSID, WIFI_SENHA, WIFI_CANAL,
    MQTT_HOST, MQTT_PORTA, MQTT_USUARIO, MQTT_SENHA

  NOTA: na porta 8883, usa TLS; se MQTT_CA_PEM nao estiver definido,
  setInsecure() NAO valida a identidade do servidor (apenas para teste).
  Na porta 1883, usa TCP sem TLS (so em rede confiavel).
*/

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <MQTT.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <time.h>
#include <math.h>
#include <Preferences.h>
#include <esp_system.h>
#include "secrets.h"

// ==================== IDENTIFICACAO ====================
// No EMQX proprio, EQUIPE nao precisa ser igual ao usuario MQTT.
// Para seguir a convencao do professor, use o codigo real eqNN na entrega.
const char *EQUIPE = "eq04";
const char *NO = "no02";

// ==================== HARDWARE ====================
constexpr uint8_t OLED_SDA = 21;
constexpr uint8_t OLED_SCL = 22;
constexpr uint8_t DHT_PIN = 4;
constexpr uint16_t LARGURA_OLED = 128;
constexpr uint16_t ALTURA_OLED = 64;
constexpr uint32_t INTERVALO_SENSOR_MS = 2000;

Adafruit_SSD1306 display(LARGURA_OLED, ALTURA_OLED, &Wire, -1);
DHT dht(DHT_PIN, DHT11);
bool oledDisponivel = false;
bool telaErro = false;
int ultimaTempDecimos = -9999;
int ultimaUmidadeInteira = -9999;

// ==================== WIFI / MQTT ====================
WiFiClient netNormal;
WiFiClientSecure netSeguro;
MQTTClient mqtt(1024);

char idNo[32];
char clientId[48];
char tTele[80];
char tStatus[80];
char tConfig[80];

uint32_t periodo_s = 5;  // configuravel por MQTT: {"periodo_s": 30}
uint32_t seq = 0;
uint32_t bootId = 0;  // contador de inicializacoes persistido na NVS
uint32_t ultimaTentativaWiFi = 0;
uint32_t ultimaTentativaMQTT = 0;
bool wifiEstavaConectado = false;

// ==================== ULTIMA MEDICAO ====================
float temperaturaAtual = NAN;
float umidadeAtual = NAN;
bool sensorOK = false;
bool jaLeuSensor = false;
uint32_t tsUltimaMedicao = 0; // Unix UTC ou 0 se NTP ainda nao sincronizou

// ==================== FILA LOCAL EM RAM ====================
// 120 leituras = 10 min com periodo de 5 s, ou 60 min com 30 s.
// Nao sobrevive a falta de energia / reset.
constexpr size_t CAPACIDADE_FILA = 120;
struct LeituraPendente {
  uint32_t numero;
  uint32_t timestamp;
  float temperatura;
  float umidade;
  bool valida;
};
LeituraPendente fila[CAPACIDADE_FILA];
size_t cabeca = 0;
size_t quantidade = 0;
uint32_t descartadas = 0;

// ==================== IDENTIFICADOR DE INICIALIZACAO ====================
// Uma escrita na NVS por reinicio. EN e desligar/ligar geram novo boot_id.
// Se a NVS for apagada (Erase All Flash), o contador reinicia.
// O boot_id identifica a inicializacao; seq identifica a mensagem nela.
void inicializarBootId() {
  Preferences prefs;
  if (!prefs.begin("higrolar", false)) {
    bootId = esp_random();
    if (bootId == 0) bootId = 1;
    Serial.printf("[boot] ERRO ao abrir NVS; boot_id aleatorio=%lu (nao persistente)\n",
                  (unsigned long)bootId);
    return;
  }

  uint32_t anterior = prefs.getUInt("boot_count", 0);
  uint32_t proximo = anterior + 1;
  if (proximo == 0) {
    // Overflow improvavel: 2^32 reinicializacoes.
    proximo = 1;
    Serial.println("[boot] AVISO: contador NVS atingiu limite e voltou a 1");
  }

  if (prefs.putUInt("boot_count", proximo) != sizeof(uint32_t)) {
    bootId = esp_random();
    if (bootId == 0) bootId = 1;
    Serial.printf("[boot] ERRO ao salvar NVS; boot_id aleatorio=%lu (nao persistente)\n",
                  (unsigned long)bootId);
  } else {
    bootId = proximo;
    Serial.printf("[boot] boot_id=%lu (persistido na NVS)\n",
                  (unsigned long)bootId);
  }
  prefs.end();
}

// ==================== OLED ====================
void exibirMensagemInicial() {
  if (!oledDisponivel) return;
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(0, 10);
  display.println("HIGROLAR");
  display.setTextSize(1);
  display.setCursor(0, 42);
  display.println("Iniciando AP2...");
  display.display();
}

void exibirErroSensor() {
  if (!oledDisponivel || telaErro) return;
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 20);
  display.println("Falha no DHT11");
  display.display();
  telaErro = true;
}

void atualizarOLED(float temperatura, float umidade) {
  if (!oledDisponivel) return;

  // Compara o que efetivamente aparece na tela, evitando erros de float.
  int tempDecimos = lroundf(temperatura * 10.0f);
  int umidadeInteira = lroundf(umidade);
  if (!telaErro && tempDecimos == ultimaTempDecimos &&
      umidadeInteira == ultimaUmidadeInteira) return;

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println("TEMPERATURA");
  display.setTextSize(2);
  display.setCursor(0, 12);
  display.print(temperatura, 1);
  display.println(" C");

  display.setTextSize(1);
  display.setCursor(0, 36);
  display.println("UMIDADE");
  display.setTextSize(2);
  display.setCursor(0, 48); // 48 + 16 = 64: sem cortar texto
  display.print(umidade, 0);
  display.println(" %");
  display.display();

  ultimaTempDecimos = tempDecimos;
  ultimaUmidadeInteira = umidadeInteira;
  telaErro = false;
  Serial.println("[oled] atualizado");
}

// ==================== SENSOR (SEMPRE, MESMO SEM WIFI) ====================
void tarefaSensor() {
  static uint32_t ultimaLeitura = 0;
  uint32_t agoraMs = millis();
  // Primeira leitura apos 2 segundos: permite estabilizar o DHT11.
  if ((uint32_t)(agoraMs - ultimaLeitura) < INTERVALO_SENSOR_MS) return;
  ultimaLeitura = agoraMs;

  float t = dht.readTemperature();
  float u = dht.readHumidity();
  jaLeuSensor = true;
  time_t agoraUnix = time(nullptr);
  tsUltimaMedicao = (agoraUnix > 1700000000LL) ? (uint32_t)agoraUnix : 0;

  if (isnan(t) || isnan(u)) {
    sensorOK = false;
    Serial.println("[sensor] falha na leitura do DHT11");
    exibirErroSensor();
    return;
  }

  sensorOK = true;
  temperaturaAtual = t;
  umidadeAtual = u;
  Serial.printf("[sensor] T=%.1f C | UR=%.0f %%\n", t, u);
  atualizarOLED(t, u);
}

// ==================== FILA ====================
void adicionarNaFila() {
  if (!jaLeuSensor) return;

  LeituraPendente nova;
  nova.numero = ++seq;
  nova.timestamp = tsUltimaMedicao;
  nova.temperatura = temperaturaAtual;
  nova.umidade = umidadeAtual;
  nova.valida = sensorOK;

  if (quantidade == CAPACIDADE_FILA) {
    cabeca = (cabeca + 1) % CAPACIDADE_FILA;
    quantidade--;
    descartadas++;
    Serial.printf("[fila] cheia: leitura mais antiga descartada (total=%lu)\n",
                  (unsigned long)descartadas);
  }

  size_t pos = (cabeca + quantidade) % CAPACIDADE_FILA;
  fila[pos] = nova;
  quantidade++;
}

void tarefaAgendarTelemetria() {
  static uint32_t ultimaAgenda = 0;
  uint32_t agora = millis();
  if ((uint32_t)(agora - ultimaAgenda) < periodo_s * 1000UL) return;
  ultimaAgenda = agora;
  adicionarNaFila();
}

void tarefaEnviarFila() {
  static uint32_t ultimoEnvio = 0;
  if (!mqtt.connected() || quantidade == 0) return;
  if ((uint32_t)(millis() - ultimoEnvio) < 100) return;
  ultimoEnvio = millis();

  const LeituraPendente &p = fila[cabeca];
  JsonDocument doc;
  doc["id"] = idNo;
  doc["boot_id"] = bootId;
  doc["seq"] = p.numero;
  if (p.timestamp != 0) doc["ts"] = p.timestamp;
  else                  doc["ts"] = nullptr;
  doc["sensor_ok"] = p.valida;

  if (p.valida) {
    doc["temp_c"] = roundf(p.temperatura * 10.0f) / 10.0f;
    doc["umid_pct"] = roundf(p.umidade);
  } else {
    doc["temp_c"] = nullptr;
    doc["umid_pct"] = nullptr;
  }

  char json[256];
  size_t tamanho = serializeJson(doc, json, sizeof(json));
  if (tamanho == 0 || tamanho >= sizeof(json) - 1) {
    Serial.println("[pub] erro ao serializar o JSON");
    return;
  }

  bool enviado = mqtt.publish(tTele, json, false, 1);  // QoS 1, nao retido
  if (!enviado) {
    Serial.printf("[pub] FALHOU; leitura seq=%lu permanece na fila\n",
                  (unsigned long)p.numero);
    return;
  }

  Serial.printf("[pub] %s %s (fila=%u)\n", tTele, json,
                (unsigned int)(quantidade - 1));
  cabeca = (cabeca + 1) % CAPACIDADE_FILA;
  quantidade--;
}

// ==================== CONFIG RECEBIDA ====================
void aoReceber(String &topico, String &carga) {
  if (topico != tConfig) return;
  Serial.printf("[sub] %s %s\n", topico.c_str(),
                (carga.length() == 0) ? "(vazia)" : carga.c_str());

  if ((carga.length() == 0)) {
    periodo_s = 5;
    Serial.println("[config] periodo padrao = 5 s");
    return;
  }

  JsonDocument cfg;
  if (deserializeJson(cfg, carga)) {
    Serial.println("[config] JSON invalido: ignorado");
    return;
  }
  if (cfg["periodo_s"].is<int>()) {
    // O DHT11 fornece nova amostra a cada 2 s; nao publicar mais rapido.
    periodo_s = constrain(cfg["periodo_s"].as<int>(), 2, 3600);
    Serial.printf("[config] periodo_s = %lu\n", (unsigned long)periodo_s);
  }
}

// ==================== WIFI ====================
void conectarWiFi() {
  if (WIFI_CANAL > 0) WiFi.begin(WIFI_SSID, WIFI_SENHA, WIFI_CANAL);
  else                WiFi.begin(WIFI_SSID, WIFI_SENHA);
  ultimaTentativaWiFi = millis();
  Serial.printf("[wifi] tentando conectar em '%s'\n", WIFI_SSID);
}

void tarefaWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    if (!wifiEstavaConectado) {
      wifiEstavaConectado = true;
      Serial.printf("[wifi] conectado - IP %s\n",
                    WiFi.localIP().toString().c_str());
    }
    return;
  }

  if (wifiEstavaConectado) {
    wifiEstavaConectado = false;
    Serial.println("[wifi] conexao perdida; sensor e OLED continuam ativos");
  }
  if ((uint32_t)(millis() - ultimaTentativaWiFi) >= 15000) conectarWiFi();
}

// ==================== MQTT ====================
void conectarBroker() {
  mqtt.setWill(tStatus, "offline", true, 1);
  mqtt.setCleanSession(false);
  mqtt.setKeepAlive(30);

  Serial.printf("[mqtt] conectando como %s...\n", clientId);
  if (!mqtt.connect(clientId, MQTT_USUARIO, MQTT_SENHA)) {
    Serial.printf("[mqtt] falhou: erro=%d retorno=%d\n",
                  (int)mqtt.lastError(), (int)mqtt.returnCode());
    return;
  }

  Serial.println("[mqtt] conectado");
  bool statusOk = mqtt.publish(tStatus, "online", true, 1);
  bool assinaturaOk = mqtt.subscribe(tConfig, 1);
  Serial.printf("[mqtt] status online=%s, config=%s\n",
                statusOk ? "ok" : "falhou", assinaturaOk ? "ok" : "falhou");
}

void tarefaMQTT() {
  if (WiFi.status() != WL_CONNECTED) return;

  if (mqtt.connected()) {
    mqtt.loop(); // mantem o keepalive e recebe mensagens de config
    return;
  }

  if ((uint32_t)(millis() - ultimaTentativaMQTT) < 5000) return;
  ultimaTentativaMQTT = millis();
  conectarBroker();
}

// ==================== SETUP / LOOP ====================
void setup() {
  Serial.begin(115200);
  inicializarBootId();
  Wire.begin(OLED_SDA, OLED_SCL);
  oledDisponivel = display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  if (!oledDisponivel) Serial.println("[oled] nao detectado; telemetria continuara");
  else exibirMensagemInicial();

  dht.begin();
  snprintf(idNo, sizeof(idNo), "%s-%s", EQUIPE, NO);
  snprintf(clientId, sizeof(clientId), "ufpi-iot26-%s-%s", EQUIPE, NO);
  snprintf(tTele, sizeof(tTele), "ufpi-iot26/%s/%s/telemetria", EQUIPE, NO);
  snprintf(tStatus, sizeof(tStatus), "ufpi-iot26/%s/%s/status", EQUIPE, NO);
  snprintf(tConfig, sizeof(tConfig), "ufpi-iot26/%s/%s/config", EQUIPE, NO);

  // Broker EMQX: 8883 = MQTT/TLS; 1883 = MQTT sem TLS.
  const bool usarTLS = (MQTT_PORTA != 1883);
  if (usarTLS) {
#ifdef MQTT_CA_PEM
    netSeguro.setCACert(MQTT_CA_PEM);
#else
    netSeguro.setInsecure(); // TESTE: nao autentica certificado do servidor!
    Serial.println("[tls] ATENCAO: certificado do broker nao sera validado");
#endif
  } else {
    Serial.println("[mqtt] ATENCAO: porta 1883 sem criptografia");
  }
  Client &transporte = usarTLS ? static_cast<Client &>(netSeguro)
                              : static_cast<Client &>(netNormal);
  mqtt.begin(MQTT_HOST, MQTT_PORTA, transporte);
  mqtt.onMessage(aoReceber);

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  conectarWiFi();
  configTime(0, 0, "pool.ntp.org", "time.google.com"); // Unix UTC
}

void loop() {
  tarefaSensor();             // cada 2 s, independentemente da rede
  tarefaWiFi();               // nao bloqueia em while de conexao
  tarefaMQTT();               // conecta, recebe config, mantem keepalive
  tarefaAgendarTelemetria();  // a cada periodo_s, tambem offline
  tarefaEnviarFila();        // tenta descarregar backlog quando online
  delay(1);                  // cede tempo ao sistema, nao bloqueia 2 s
}
