#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

// =========================
// OLED
// =========================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define OLED_SDA 21
#define OLED_SCL 22

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  -1
);

// =========================
// DHT11
// =========================

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// =========================
// CONTROLE DAS ATUALIZAÇÕES
// =========================

// Últimos valores exibidos no OLED
float ultimaTemperatura = -999.0;
float ultimaUmidade = -999.0;

// Tolerâncias para atualização
const float VARIACAO_TEMPERATURA = 0.1;
const float VARIACAO_UMIDADE = 1.0;

// =========================
// SETUP
// =========================

void setup() {

  Serial.begin(115200);

  // Inicializa I2C
  Wire.begin(OLED_SDA, OLED_SCL);

  // Inicializa OLED
  if (!display.begin(
        SSD1306_SWITCHCAPVCC,
        0x3C
      )) {

    Serial.println("Erro: OLED nao encontrado!");

    while (true) {
      delay(100);
    }
  }

  // Inicializa DHT11
  dht.begin();

  // =========================
  // TELA INICIAL
  // =========================

  display.clearDisplay();

  display.setTextColor(SSD1306_WHITE);

  display.setTextSize(2);

  display.setCursor(0, 10);

  display.println("Iniciando");

  display.setTextSize(1);

  display.setCursor(0, 40);

  display.println("DHT11 + OLED");

  display.display();

  delay(2000);
}

// =========================
// LOOP
// =========================

void loop() {

  // =========================
  // LEITURA DO DHT11
  // =========================

  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();

  // =========================
  // VERIFICA ERRO
  // =========================

  if (isnan(temperatura) || isnan(umidade)) {

    Serial.println("Erro ao ler DHT11!");

    display.clearDisplay();

    display.setTextColor(SSD1306_WHITE);

    display.setTextSize(1);

    display.setCursor(0, 20);

    display.println("Erro no DHT11!");

    display.display();

    delay(2000);

    return;
  }

  // =========================
  // SERIAL MONITOR
  // =========================

  Serial.print("Temperatura: ");
  Serial.print(temperatura, 1);
  Serial.println(" C");

  Serial.print("Umidade: ");
  Serial.print(umidade, 0);
  Serial.println(" %");

  Serial.println("--------------------");

  // =========================
  // VERIFICA SE PRECISA
  // ATUALIZAR O OLED
  // =========================

  bool temperaturaMudou =
    abs(temperatura - ultimaTemperatura)
    >= VARIACAO_TEMPERATURA;

  bool umidadeMudou =
    abs(umidade - ultimaUmidade)
    >= VARIACAO_UMIDADE;

  // =========================
  // ATUALIZA OLED
  // =========================

  if (temperaturaMudou || umidadeMudou) {

    display.clearDisplay();

    display.setTextColor(SSD1306_WHITE);

    // -------------------------
    // Temperatura
    // -------------------------

    display.setTextSize(1);

    display.setCursor(0, 0);

    display.println("TEMPERATURA");

    display.setTextSize(2);

    display.setCursor(0, 12);

    display.print(temperatura, 1);

    display.println(" C");

    // -------------------------
    // Umidade
    // -------------------------

    display.setTextSize(1);

    display.setCursor(0, 40);

    display.println("UMIDADE");

    display.setTextSize(2);

    display.setCursor(0, 50);

    display.print(umidade, 0);

    display.println(" %");

    // -------------------------
    // Envia para o OLED
    // -------------------------

    display.display();

    // Guarda os valores exibidos
    ultimaTemperatura = temperatura;
    ultimaUmidade = umidade;

    Serial.println("OLED atualizado.");
  }
  else {

    Serial.println("OLED sem alteracao.");
  }

  // =========================
  // AGUARDA 2 SEGUNDOS
  // =========================

  delay(2000);
}