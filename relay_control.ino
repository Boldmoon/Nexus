void setup()
{
  pinMode(5, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(14, OUTPUT);
  pinMode(12, OUTPUT);
  digitalWrite(5, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(14, HIGH);
  digitalWrite(12, HIGH);
}

void loop()
{
  digitalWrite(5, LOW);
  digitalWrite(4, LOW);
  digitalWrite(14, LOW);
  digitalWrite(12, LOW);
  delay(2000);
  digitalWrite(5, HIGH);
  digitalWrite(4, HIGH);
  digitalWrite(14, HIGH);
  digitalWrite(12, HIGH);
  delay(2000);
}
