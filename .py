from gpio import *
from time import *

def main():
    # Konfiguráljuk a kimenetet a locsoló rendszerhez
    pinMode(2, OUT)  # D2: Locsolo rendszer vezerlese
    locsolas_idotartam = 30  # Locsolas idotartama percben
    
    while True:
        # Aktuális idő lekérdezése a time modulból
        aktualis_ido = localtime()
        ora = aktualis_ido[3]    # Az óra a 3. elem a time tuple-ben
        perc = aktualis_ido[4]   # A perc a 4. elem a time tuple-ben
        
        # Időzítés ellenőrzése (17:00)
        if ora == 17 and perc == 0:
            print("17:00 - Locsolas kezdese")
            digitalWrite(2, HIGH)  # Locsolo rendszer bekapcsolasa
            
            # Locsolás a beállított ideig
            sleep(locsolas_idotartam * 60)  # Másodpercekre átváltva
            
            # Locsolás befejezése
            digitalWrite(2, LOW)  # Locsolo rendszer kikapcsolasa
            print("Locsolas befejezve")
            
            # Várjunk 1 percet, hogy ne induljon újra azonnal
            sleep(60)
        
        # Ellenőrzés 10 másodpercenként
        sleep(10)
        
if __name__ == "__main__":
    main()