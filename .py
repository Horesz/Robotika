from gpio import *
from time import *

def main():
    pinMode(0, IN)   # D0: Hőmérséklet szenzor
    pinMode(1, OUT)  # D1: Klíma vezérlés
    
    # Beállíthatod a hőmérséklet küszöbértéket Celsius fokban
    HOMERSEKLET_KUSZOB = 25
    
    while True:
        # Olvassuk a hőmérséklet értéket
        homerseklet = analogRead(0)
        
        # Konvertáljuk a nyers értéket Celsius fokra
        # Megjegyzés: Ez a konverzió a szenzortól függően változhat
        homerseklet_celsius = (homerseklet * 0.48875)
        
        print("Aktuális hőmérséklet:", round(homerseklet_celsius, 1), "°C")
        
        # Ha a hőmérséklet magasabb, mint a küszöbérték
        if homerseklet_celsius > HOMERSEKLET_KUSZOB:
            print("Hőmérséklet túl magas:", round(homerseklet_celsius, 1), "°C - Klíma bekapcsolása")
            digitalWrite(1, HIGH)  # Klíma bekapcsolása
        else:
            print("Hőmérséklet megfelelő:", round(homerseklet_celsius, 1), "°C - Klíma kikapcsolása")
            digitalWrite(1, LOW)   # Klíma kikapcsolása
            
        sleep(10)  # 10 másodpercenként ellenőrizzük a hőmérsékletet
        
if __name__ == "__main__":
    main()