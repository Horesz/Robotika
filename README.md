# Packet Tracer és a Python okosotthon script integrálása

## 1. Packet Tracer konfigurálás

A Packet Tracer IoT eszközök programozása és a mellékelt Python script integrálása a következő lépésekkel végezhető el:

### 1.1 Eszközök beállítása

1. Nyisd meg a Packet Tracert és töltsd be az okosotthon tervét
2. Minden IoT eszközt konfiguráld:
   - Jobb klikk minden eszközön
   - Advanced Setup > IoT Server menüpont
   - Engedélyezd a "Remote Server" opciót
   - Port: 5000 (vagy amit a Python script használ)
   - Protokoll: TCP/IP

### 1.2 IoT szolgáltatások beállítása

1. A Home Gateway eszközön:
   - Konfiguráld a szolgáltatásokat
   - Adj hozzá egy Registration Servert az 5000-es porton

## 2. Python script módosítása

A jelenlegi Python script szimulációs üzemmódban működik. Az igazi Packet Tracer API-val való kommunikációhoz módosítani kell:

```python
# A PacketTracerInterface.discover_devices metódus módosítása
def discover_devices(self):
    """
    Felderíti az elérhető eszközöket a Packet Tracer szimulációban.
    Valós API hívásokat használ.
    """
    if not self.connected:
        print("Nincs kapcsolat a Packet Tracer-rel!")
        return {}
    
    try:
        # Küldünk egy lekérdezést a PT Registration Servernek
        self.socket.send(b"GET_DEVICES\n")
        response = self.socket.recv(4096).decode('utf-8')
        
        # Feldolgozzuk a választ
        devices = {}
        for line in response.strip().split("\n"):
            if ":" in line:
                device_id, device_info = line.split(":", 1)
                device_data = json.loads(device_info)
                devices[device_id] = device_data
        
        self.device_registry = devices
        print(f"{len(self.device_registry)} eszköz felderítve a Packet Tracer szimulációban")
        return self.device_registry
    except Exception as e:
        print(f"Hiba az eszközfelderítés során: {e}")
        return {}
```

Hasonlóan módosítani kell a `set_device_state` és `get_device_state` metódusokat is.

## 3. A script futtatása

1. Telepítsd a szükséges Python csomagokat:
   ```
   pip install python-socketio
   ```

2. Indítsd el a Packet Tracert és töltsd be az okosotthon projektfájlt

3. Futtasd a Python scriptet:
   ```
   python SmartHome_script.py
   ```

4. Ha minden jól működik, a script csatlakozik a Packet Tracerhez és irányítja az okosotthon eszközeit

## 4. Hibaelhárítás

- Ellenőrizd, hogy a Packet Tracer fut és hogy az eszközök megfelelően vannak konfigurálva
- Ellenőrizd a tűzfal beállításait, hogy engedélyezve van-e a kommunikáció az 5000-es porton
- Ellenőrizd a hálózati beállításokat a Packet Tracerben és a Python scriptben

## 5. Fejlesztési tippek

- Kezdj egyszerű parancsokkal, például egy lámpa ki-be kapcsolásával
- Fokozatosan adj hozzá összetettebb funkciókat
- A hibaüzeneteket naplózd egy fájlba a könnyebb hibakeresés érdekében