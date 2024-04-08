// Bibliotecas utilizadas
#include <Arduino.h>
#include <max6675.h>
#include <PID_v1.h>
#include <Adafruit_ADS1X15.h>
#include <Adafruit_INA219.h>

// Pinos utilizados
// Peltier
#define hotPLT  5         //  Peltier quente
#define coldPLT 6         //  Peltier fria
//  Termopares
#define SO        2
#define CLK       4
#define CS1       7       //  Termopar frio
#define CS2       3       //  Termopar quente
// Chaveamento
#define relay    8
// LEDs
#define plt1LED   9
#define plt2LED   10
#define refLED    11
// Tolerancia
#define tolerancia 3

// Variáveis globais
String received;                                  //  Leitura serial
unsigned int time = 0;                            //  Tempo atual
unsigned int last = 0;                            //  Última leitura
double upper = 50;                                //  Temperatura quente - default
double lower = 20;                                //  Temperatura fria - default
int waveForm = 1;                                 //  Forma de onda
int periodo = 120;                                 //  Período
int maxT = 90, minT = 50;                         //  Temperatura máxima e mínima
double aux = 0;
bool estado = true;
double Setpoint1 = 50, Input1 = 0, Output1 = 0;   //  Referência, entrada e saída para peltier fria
double Setpoint2 = 50, Input2 = 0, Output2 = 0;   //  Referência, entrada e saída para peltier quente
double Kp1 = 4, Ki1 = 3, Kd1 = 0;                    //  Parâmetros PID dos controladores
double Kp2 = 1 , Ki2 = 1, Kd2 = 0;                    //  Parâmetros PID dos controladores


// Funções criadas
void changeParameter(String rString);
void controlTemp(int time);
void modeChange();
void monitorTempVolt() ;
void setTemp(int temp, int peltier);

// Configurando controladores
PID PIDhot(&Input1, &Output1, &Setpoint1, Kp2, Ki2, Kd2, DIRECT);
PID PIDcold(&Input2, &Output2, &Setpoint2, Kp1, Ki1, Kd1, DIRECT);

// Configurando termopares
MAX6675 ktc1(CLK, CS1, SO);
MAX6675 ktc2(CLK, CS2, SO);

//  ADS1115
Adafruit_ADS1115 ads;

void setup() {
  //  Configuração Serial
  Serial.begin(115200);
  //  Referência de tensão analógica
  analogReference(INTERNAL);
  //  Definindo saídas para as Peltiers
  pinMode(hotPLT, OUTPUT);
  pinMode(coldPLT, OUTPUT);
  //  Configuração dos controladores
  PIDhot.SetMode(AUTOMATIC);
  PIDcold.SetMode(AUTOMATIC);
  // Configuração do ADS1115
  if (!ads.begin())
  {
    Serial.println("Failed to initialize ADS.");
    while (1);
  }
  //                                                                ADS1015  ADS1115
  //                                                                -------  -------
  // ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
  ads.setGain(GAIN_ONE);           // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV

  // Relay
  pinMode(relay, OUTPUT);

  // LEDs
  pinMode(plt1LED, OUTPUT);
  pinMode(plt2LED, OUTPUT);
  pinMode(refLED, OUTPUT);
}

void loop() {
  if(Serial.available())
  {
    String received = Serial.readStringUntil('\n');
    changeParameter(received);
  }
  delay(10);

  time = millis();
  if(time - last > 1000)
  {
    controlTemp(waveForm);
    monitorTempVolt();

    last = time;
  }
}

void setTemp(int temp, int peltier)
{
  if(peltier == 1)    //  Setting cold peltier
  {
    Setpoint1 = temp;
    Input1 = ktc1.readCelsius();  
    PIDcold.Compute();  
    analogWrite(coldPLT, 255 - Output1);
  }
  else if(peltier == 2)   //  Setting hot peltier
  {
    Setpoint2 = temp;
    Input2 = ktc2.readCelsius();
    PIDhot.Compute();
    analogWrite(hotPLT, Output2);
  }
  return;
}


void changeParameter(String rString)
{
  if(rString != 0)
  {
    String str_aux = rString;
    String str_data[4];

    for(int i=0; i<4; i++)
    {
      int index = str_aux.lastIndexOf(' ');
      int lenght = str_aux.length();

      str_data[i] = str_aux.substring(index,lenght);
      str_aux = str_aux.substring(0, index);
    }

    str_aux = str_data[0];
    periodo = str_aux.toDouble();
    str_aux = str_data[1];
    waveForm = str_aux.toDouble();
    str_aux = str_data[2];
    upper = str_aux.toInt();
    str_aux = str_data[3];
    lower = str_aux.toInt();
  }
}

void controlTemp(int wave)
{
  switch(wave)
  {
    case 1:                     //  Waveform Constant
      digitalWrite(plt1LED, HIGH);
      digitalWrite(plt2LED, HIGH);
      setTemp(lower, 1);
      setTemp(upper, 2);
      break;
    case 2:                     //  Onda quadrada
      digitalWrite(plt1LED, HIGH);
      digitalWrite(plt2LED, HIGH);
      if(estado)
      {
        setTemp(lower,1);
        setTemp(upper,2);
        aux += 1;
      }
      else
      {
        setTemp(lower,1);
        setTemp(lower,2);
        aux += 1;
      }

      if(aux == periodo)
      {
        estado = !estado;
        aux = 0;
      }
      break;
    case 3:   //  Somente esfriar
      digitalWrite(plt1LED, HIGH);
      digitalWrite(plt2LED, LOW);
      setTemp(lower, 1);
      analogWrite(hotPLT, 0);
      break;
    case 4:   //  Somente esquentar
      digitalWrite(plt1LED, LOW);
      digitalWrite(plt2LED, HIGH);
      analogWrite(coldPLT, 0);
      setTemp(upper, 2);
      break;
    case 5:   //  Desligado
      digitalWrite(plt1LED, LOW);
      digitalWrite(plt2LED, LOW);
      analogWrite(coldPLT, 0);
      analogWrite(hotPLT, 0);
      break;
    //  Encontrado um erro
    default:
      Serial.println("Ocorreu algum problema...");
      delay(1000);
      break;
  }
  return;
}

void monitorTempVolt()
{
  int16_t results;
  float corrente = 0.0, multiplier = 0.125F;
  float voltage = 0.0, rsw = 0.8;
  float vshunt = 0, auxdata = 0;;
  float termopar1 = ktc1.readCelsius(); 
  float termopar2 = ktc2.readCelsius();
  int sample = 10;

  //  ADS - Corrente
  digitalWrite(relay, HIGH);
  delay(30);
  for(int i=0; i < sample; i++)
  {
    results = ads.readADC_Differential_0_1();
    vshunt = results * multiplier; 
    auxdata += (vshunt / rsw);
    delay(20);
  }
  corrente = auxdata / sample;
  auxdata = 0;

  // ADS - Tensão
  digitalWrite(relay, LOW);
  delay(30);
  for(int i=0; i < sample; i++)
  {
    results = ads.readADC_Differential_0_1();
    auxdata += results * multiplier;
    delay(20);
  }
  voltage = auxdata / sample;
  
  Serial.print(waveForm);
  Serial.print(" ");
  Serial.print(termopar1);
  Serial.print(" ");
  Serial.print(termopar2);
  Serial.print(" ");
  Serial.print(voltage);
  Serial.print(" ");
  Serial.println(corrente);
}