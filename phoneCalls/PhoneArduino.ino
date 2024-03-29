//www.elegoo.com
//2016.12.9

/*
  LiquidCrystal Library - Hello World

 Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
 library works with all LCD displays that are compatible with the
 Hitachi HD44780 driver. There are many of them out there, and you
 can usually tell them by the 16-pin interface.

 This sketch prints "Hello World!" to the LCD
 and shows the time.

  The circuit:
 * LCD RS pin to digital pin 7
 * LCD Enable pin to digital pin 8
 * LCD D4 pin to digital pin 9
 * LCD D5 pin to digital pin 10
 * LCD D6 pin to digital pin 11
 * LCD D7 pin to digital pin 12
 * LCD R/W pin to ground
 * LCD VSS pin to ground
 * LCD VCC pin to 5V
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)

 Library originally added 18 Apr 2008
 by David A. Mellis
 library modified 5 Jul 2009
 by Limor Fried (http://www.ladyada.net)
 example added 9 Jul 2009
 by Tom Igoe
 modified 22 Nov 2010
 by Tom Igoe

 This example code is in the public domain.

 http://www.arduino.cc/en/Tutorial/LiquidCrystal
 */

// include the library code:
#include <LiquidCrystal.h>

#include <Keypad.h>

const byte ROWS = 4; //four rows
const byte COLS = 3; //four columns
char keys[ROWS][COLS] = {
  {'1','2','3'},
  {'4','5','6'},
  {'7','8','9'},
  {'*','0','#'}
};

byte rowPins[ROWS] = {A4, A3, A2, A1}; //connect to the row pinouts of the keypad
byte colPins[COLS] = {7, 6, 5}; //connect to the column pinouts of the keypad

Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, ROWS, COLS );

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 9, 10, 11, 12, 13);

int col = 0;
String x;

char num[11] = {'*','*','*','*','*','*','*','*','*','*'};

void setup() {
  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);
  // Print a message to the LCD.
  lcd.print("Enter Phone #: ");
  
  lcd.setCursor(0, 1);
  lcd.print(num);
  
  Serial.begin(9600);
}

void loop() {
//  while (!Serial.available()); 
//  x = Serial.readString(); 
//  // Serial.print(x + 1); 
//  lcd.setCursor(0, 0);
//  lcd.print(x);

  
  // set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
  
  // print the number of seconds since reset:
  // lcd.print(millis() / 1000);


  
  char key = keypad.getKey();
  
  if (key){
    
    if (key == '*' && col >= 0){
      col--;
      lcd.setCursor(col, 1);
      lcd.print('*');
      num[col] = '*';
    }
    else if (col <= 9 && key != '#'){
      lcd.setCursor(col, 1);
      //Serial.println(key);
      lcd.print(key);
      num[col] = key;
      col++;
    }
    else if (key == '#' && col == 10){
      lcd.setCursor(0, 1);
      col = 0;
      
      Serial.println(num);
      
      for(int i = 0; i < 10; i++){
        num[i] = '*';
      }
      lcd.print(num);
      lcd.setCursor(0, 0);
      lcd.print("Thank You! Enjoy!");
      delay(5000);
      lcd.setCursor(0, 0);
      lcd.print("Enter Phone #:      ");
    }
  }
}
