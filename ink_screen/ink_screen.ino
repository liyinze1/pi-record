/***************************************************
  Adafruit invests time and resources providing this open source code,
  please support Adafruit and open-source hardware by purchasing
  products from Adafruit!

  Written by Limor Fried/Ladyada for Adafruit Industries.
  MIT license, all text above must be included in any redistribution
 ****************************************************/

#include "Adafruit_ThinkInk.h"
#include "qrcode.h"

#ifdef ARDUINO_ADAFRUIT_FEATHER_RP2040_THINKINK // detects if compiling for
                                                // Feather RP2040 ThinkInk
#define EPD_DC PIN_EPD_DC       // ThinkInk 24-pin connector DC
#define EPD_CS PIN_EPD_CS       // ThinkInk 24-pin connector CS
#define EPD_BUSY PIN_EPD_BUSY   // ThinkInk 24-pin connector Busy
#define SRAM_CS -1              // use onboard RAM
#define EPD_RESET PIN_EPD_RESET // ThinkInk 24-pin connector Reset
#define EPD_SPI &SPI1           // secondary SPI for ThinkInk
#else
#define EPD_DC 10
#define EPD_CS 9
#define EPD_BUSY -1 // can set to -1 to not use a pin (will wait a fixed delay)
#define SRAM_CS 6
#define EPD_RESET -1  // can set to -1 and share with microcontroller Reset!
#define EPD_SPI &SPI // primary SPI
#endif


ThinkInk_213_Mono_GDEY0213B74 display(EPD_DC, EPD_RESET, EPD_CS, SRAM_CS, EPD_BUSY, EPD_SPI);

String message = "";
String token = "";

QRCode qrcode;
uint8_t *qrcodeData; // Version 3 can fit 8 chars easily
int pixelSize = 3; // Size of each QR module (dot) in pixels
int offsetX = 5;
int offsetY = 5;


void setup() {
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }

  qrcodeData = (uint8_t *)malloc(qrcode_getBufferSize(3));
  if (qrcodeData == NULL) {
    Serial.println("Failed to allocate memory!");
    while (1);
  }
  
  display.begin(THINKINK_MONO);
  display.setRotation(2);
}

void loop() {
  while (Serial.available()) {
    char key = (char)Serial.read();
    String payload = "";
    while (Serial.available()) {
      char c = (char)Serial.read();
      if (c != '\n') {
        payload += c;
      } else {
        break;
      }
    }
    if (key == 'T') {
        if (payload != token) {
          token = payload;
          // generate QR
          qrcode_initText(&qrcode, qrcodeData, 3, ECC_LOW, token.c_str()); // version=3, error correction=low
          render();
        }
    } else if (key == 'M') {
        if (payload != message) {
          message = payload;
          render();
        }
    }
  }
}

void render() {

  display.clearBuffer();

  // Draw message
  display.setTextColor(EPD_BLACK);
  display.setTextSize(2);
  int y = offsetY;
  String temp = "";
  for (int i = 0; i < message.length(); i++) {
    char c = message[i];
    if (c == ' ') {
      display.setCursor(110, y);
      display.print(temp);
      y += 30;
      temp = "";
    } else {
      temp += c;
    }
  }
  // update time stamp
  if (temp.length() > 0) {
    display.setCursor(10, 110);
    display.setTextSize(1);
    display.print(temp);
  }
  

  // Draw QR code
  for (uint8_t y = 0; y < qrcode.size; y++) {
    for (uint8_t x = 0; x < qrcode.size; x++) {
      if (qrcode_getModule(&qrcode, x, y)) {
        display.fillRect(offsetX + x * pixelSize, offsetY + y * pixelSize,
                         pixelSize, pixelSize, EPD_BLACK);
      }
    }
  }
  
  display.display(); // Push buffer to screen
}
