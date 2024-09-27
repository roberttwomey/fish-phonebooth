const int sensor = 6;
const int air = 10;
int state;
char receivedChar;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(1);

  pinMode(sensor, INPUT_PULLUP);
  pinMode(air, OUTPUT);
  
  digitalWrite(air, HIGH); // turn off light
}

void loop() {
  // put your main code here, to run repeatedly:
  state = digitalRead(sensor);
  
  receivedChar = Serial.read();
  
  if (state == LOW){
    Serial.print("closed");
    
    //digitalWrite(air, LOW);
  }
  else{
    Serial.print("open");
    //digitalWrite(air, HIGH);
  }
  if (receivedChar == '~'){
    // turn light off
    digitalWrite(air, LOW);
  }
  if (receivedChar == 'n'){
    // turn light on
    digitalWrite(air, HIGH);
  }
  delay(1000);
}
