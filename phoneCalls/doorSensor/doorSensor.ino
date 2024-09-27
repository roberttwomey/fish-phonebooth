const int sensor = 10;
const int air = 7;
int state;
char receivedChar;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(1);

  pinMode(sensor, INPUT_PULLUP);
  pinMode(air, OUTPUT);
  
  digitalWrite(air, LOW); // turn off light
}

void loop() {
  // put your main code here, to run repeatedly:
  
  receivedChar = Serial.read();
  
  if (receivedChar == '~'){
    // turn light off
    digitalWrite(air, LOW);
  }
  if (receivedChar == 'n'){
    // turn light on
    digitalWrite(air, HIGH);
  }
  if (receivedChar == '?'){
    state = digitalRead(sensor);
    if (state == LOW){
      Serial.print("c");
      //digitalWrite(air, LOW);
    } else {
      Serial.print("o");
      //digitalWrite(air, HIGH);
    }
  }
  delay(10);
}
