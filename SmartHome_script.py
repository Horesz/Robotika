import socket
import json
import time
import threading
from datetime import datetime

# --------------------------
# Packet Tracer valós interfész osztály
# --------------------------
class PacketTracerInterface:
    def __init__(self, host='127.0.0.1', port=5000):
        """
        Inicializálja a Packet Tracer interfészt.
        A Packet Tracer Registration Serverhez kapcsolódik.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.device_registry = {}
        print(f"Packet Tracer interfész inicializálva: {host}:{port}")
    
    def connect(self):
        """Kapcsolódás a Packet Tracer Registration Serverhez"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print("Sikeres kapcsolódás a Packet Tracer-hez")
            return True
        except Exception as e:
            print(f"Hiba a kapcsolódás során: {e}")
            self.connected = False
            return False
    
    def discover_devices(self):
        """
        Felderíti az elérhető eszközöket a Packet Tracer szimulációban.
        Valós Packet Tracer API hívásokat használ.
        """
        if not self.connected:
            print("Nincs kapcsolat a Packet Tracer-rel!")
            return {}
        
        try:
            # Az egyszerűség kedvéért egy GET_DEVICES parancsot küldünk
            # A valós implementáció a Packet Tracer API-jától függ
            self.socket.sendall(b"GET_DEVICES\n")
            
            # Válasz fogadása
            data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n\n" in data:  # Feltételezzük, hogy a válasz végét két újsor jelzi
                    break
            
            response = data.decode('utf-8')
            
            # A válasz feldolgozása - illeszkednie kell a PT API formátumához
            # Ez csak egy példa, módosítani kell a tényleges API alapján
            devices = {}
            lines = response.strip().split("\n")
            for line in lines:
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        device_id = parts[0].strip()
                        try:
                            device_info = json.loads(parts[1])
                            devices[device_id] = device_info
                        except json.JSONDecodeError:
                            print(f"Hibás JSON válasz: {parts[1]}")
            
            self.device_registry = devices
            print(f"{len(self.device_registry)} eszköz felderítve a Packet Tracer szimulációban")
            return self.device_registry
            
        except Exception as e:
            print(f"Hiba az eszközfelderítés során: {e}")
            return {}
    
    def set_device_state(self, device_id, state):
        """
        Beállítja egy eszköz állapotát a szimulációban.
        Valós Packet Tracer API hívásokat használ.
        """
        if not self.connected or device_id not in self.device_registry:
            return False
        
        try:
            # Parancs összeállítása
            command = {
                "command": "SET_STATE",
                "device_id": device_id,
                "state": state
            }
            
            # Parancs küldése
            self.socket.sendall(json.dumps(command).encode('utf-8') + b"\n")
            
            # Válasz fogadása
            response = self.socket.recv(1024).decode('utf-8')
            
            # Válasz feldolgozása
            if "OK" in response:
                print(f"Eszköz állapot beállítva: {device_id} - {state}")
                
                # Frissítsük a helyi nyilvántartást is
                device = self.device_registry[device_id]
                if isinstance(state, dict):
                    for key, value in state.items():
                        if key in device:
                            device[key] = value
                else:
                    device["status"] = state
                
                return True
            else:
                print(f"Hiba az eszköz állapotának beállításakor: {response}")
                return False
                
        except Exception as e:
            print(f"Hiba az eszköz vezérlése során: {e}")
            return False
    
    def get_device_state(self, device_id):
        """
        Lekérdezi egy eszköz állapotát a szimulációból.
        """
        if not self.connected or device_id not in self.device_registry:
            return None
        
        try:
            # Parancs összeállítása
            command = {
                "command": "GET_STATE",
                "device_id": device_id
            }
            
            # Parancs küldése
            self.socket.sendall(json.dumps(command).encode('utf-8') + b"\n")
            
            # Válasz fogadása
            response = self.socket.recv(1024).decode('utf-8')
            
            # Válasz feldolgozása
            try:
                state = json.loads(response)
                # Frissítsük a helyi nyilvántartást
                self.device_registry[device_id] = state
                return state
            except json.JSONDecodeError:
                print(f"Hibás JSON válasz: {response}")
                return self.device_registry[device_id]
                
        except Exception as e:
            print(f"Hiba az eszköz állapotának lekérdezése során: {e}")
            return self.device_registry[device_id]
    
    def update_sensor_values(self):
        """
        Frissíti a szenzorok értékeit a szimulációban.
        Valós Packet Tracer API hívásokat használ.
        """
        if not self.connected:
            return {}
        
        try:
            # Parancs összeállítása
            command = {
                "command": "GET_SENSOR_VALUES"
            }
            
            # Parancs küldése
            self.socket.sendall(json.dumps(command).encode('utf-8') + b"\n")
            
            # Válasz fogadása
            data = b""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\n\n" in data:
                    break
            
            response = data.decode('utf-8')
            
            # Válasz feldolgozása
            try:
                sensor_values = json.loads(response)
                # Frissítsük a helyi nyilvántartást
                for device_id, value in sensor_values.items():
                    if device_id in self.device_registry:
                        self.device_registry[device_id]["value"] = value
                
                return self.device_registry
            except json.JSONDecodeError:
                print(f"Hibás JSON válasz: {response}")
                return self.device_registry
                
        except Exception as e:
            print(f"Hiba a szenzorértékek frissítése során: {e}")
            return self.device_registry
    
    def close(self):
        """Bezárja a kapcsolatot"""
        if self.connected and self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"Hiba a kapcsolat lezárása során: {e}")
            finally:
                self.connected = False
                print("Kapcsolat lezárva a Packet Tracer-rel")
# --------------------------
# Okos Otthon Vezérlő
# --------------------------
class SmartHomeController:
    def __init__(self, pt_interface):
        """
        Az Okos Otthon vezérlő inicializálása.
        """
        self.pt_interface = pt_interface
        self.devices = {}
        self.routines = []
        self.running = False
        self.update_thread = None
        
    def initialize(self):
        """
        Inicializálja a vezérlőt és felfedezi az eszközöket.
        """
        # Kapcsolódás a Packet Tracer-hez
        if not self.pt_interface.connected:
            self.pt_interface.connect()
        
        # Eszközök felderítése
        self.devices = self.pt_interface.discover_devices()
        
        # Automatizálások beállítása
        self.setup_routines()
        
        return len(self.devices) > 0
    
    def setup_routines(self):
        """
        Beállítja az alapértelmezett automatizálásokat.
        """
        # 1. Ha a hőmérséklet 25°C fölé megy, kapcsolja be a ventilátort
        self.add_routine(
            name="cooling_routine",
            trigger={"type": "sensor", "device_id": "IoT:Sensor:Temp:1", "condition": "above", "value": 25.0},
            actions=[{"device_id": "IoT:Fan:1", "command": {"status": True, "speed": 2}}]
        )
        
        # 2. Ha a hőmérséklet 20°C alá megy, kapcsolja be a klímát fűtési módban
        self.add_routine(
            name="heating_routine",
            trigger={"type": "sensor", "device_id": "IoT:Sensor:Temp:1", "condition": "below", "value": 20.0},
            actions=[{"device_id": "IoT:AC:1", "command": {"status": True, "temp": 22}}]
        )
        
        # 3. Ha mozgást érzékel, kapcsolja be a lámpákat
        self.add_routine(
            name="motion_lights",
            trigger={"type": "sensor", "device_id": "IoT:Sensor:Motion:1", "condition": "equal", "value": True},
            actions=[
                {"device_id": "IoT:Light:1", "command": {"status": True}},
                {"device_id": "IoT:Light:2", "command": {"status": True}}
            ]
        )
        
        # 4. Ha füstöt érzékel, kapcsolja be a ventilátort maximumon és kapcsolja fel az összes lámpát
        self.add_routine(
            name="smoke_emergency",
            trigger={"type": "sensor", "device_id": "IoT:Sensor:Smoke:1", "condition": "equal", "value": True},
            actions=[
                {"device_id": "IoT:Fan:1", "command": {"status": True, "speed": 3}},
                {"device_id": "IoT:Light:1", "command": {"status": True}},
                {"device_id": "IoT:Light:2", "command": {"status": True}},
                {"device_id": "IoT:Light:3", "command": {"status": True}}
            ]
        )
        
        print(f"{len(self.routines)} automatizálás beállítva")
    
    def add_routine(self, name, trigger, actions):
        """
        Új automatizálás hozzáadása.
        """
        routine = {
            "name": name,
            "trigger": trigger,
            "actions": actions,
            "enabled": True
        }
        self.routines.append(routine)
        print(f"Automatizálás hozzáadva: {name}")
        return True
    
    def check_routines(self):
        """
        Ellenőrzi az automatizálásokat a szenzor értékek alapján.
        """
        for routine in self.routines:
            if not routine["enabled"]:
                continue
            
            trigger = routine["trigger"]
            if trigger["type"] == "sensor":
                device_id = trigger["device_id"]
                device = self.pt_interface.get_device_state(device_id)
                
                if not device:
                    continue
                
                value = device.get("value")
                
                # Feltétel ellenőrzése
                condition_met = False
                if trigger["condition"] == "above" and value > trigger["value"]:
                    condition_met = True
                elif trigger["condition"] == "below" and value < trigger["value"]:
                    condition_met = True
                elif trigger["condition"] == "equal" and value == trigger["value"]:
                    condition_met = True
                
                # Automatizálás végrehajtása, ha a feltétel teljesül
                if condition_met:
                    self.execute_routine(routine)
    
    def execute_routine(self, routine):
        """
        Automatizálás végrehajtása.
        """
        print(f"Automatizálás végrehajtása: {routine['name']}")
        
        for action in routine["actions"]:
            device_id = action["device_id"]
            command = action["command"]
            self.pt_interface.set_device_state(device_id, command)
    
    def control_device(self, device_id, command):
        """
        Eszköz vezérlése.
        """
        return self.pt_interface.set_device_state(device_id, command)
    
    def start_monitoring(self):
        """
        Elindítja a rendszer monitorozását.
        """
        if self.running:
            print("A monitorozás már fut!")
            return
        
        self.running = True
        self.update_thread = threading.Thread(target=self._monitoring_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        print("Rendszermonitorozás elindítva")
    
    def stop_monitoring(self):
        """
        Leállítja a rendszer monitorozását.
        """
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
        print("Rendszermonitorozás leállítva")
    
    def _monitoring_loop(self):
        """
        A monitorozás háttérfolyamata.
        """
        while self.running:
            # Szenzorértékek frissítése
            self.pt_interface.update_sensor_values()
            
            # Automatizálások ellenőrzése
            self.check_routines()
            
            # Állapot megjelenítése
            self.status_report()
            
            # Várunk egy kicsit a következő frissítésig
            time.sleep(2)
    
    def status_report(self):
        """
        Állapotjelentés készítése és megjelenítése.
        """
        print("\n--- Smart Home Állapotjelentés ---")
        print(f"Idő: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\nSzenzorok:")
        for device_id, device in self.devices.items():
            if "sensor" in device["type"]:
                print(f"  - {device['name']}: {device['value']}")
        
        print("\nEszközök:")
        for device_id, device in self.devices.items():
            if "sensor" not in device["type"]:
                status_text = "BE" if device.get("status", False) else "KI"
                extra_info = ""
                if device["type"] == "ac":
                    extra_info = f", {device.get('temp', 22)}°C"
                elif device["type"] == "fan":
                    extra_info = f", Sebesség: {device.get('speed', 0)}"
                print(f"  - {device['name']}: {status_text}{extra_info}")
        
        print("-----------------------------------")

# --------------------------
# Felhasználói Interfész
# --------------------------
def interactive_menu(controller):
    """
    Interaktív parancssori menü a rendszer vezérléséhez.
    """
    while True:
        print("\n===== Okos Otthon Vezérlő =====")
        print("1. Eszközök listázása")
        print("2. Eszköz vezérlése")
        print("3. Automatizálások listázása")
        print("4. Új automatizálás hozzáadása")
        print("5. Monitorozás indítása")
        print("6. Monitorozás leállítása")
        print("7. Szimuláció indítása (teszt)")
        print("8. Kilépés")
        print("==============================")
        
        choice = input("Válassz egy opciót (1-8): ")
        
        if choice == "1":
            print("\nElérhető eszközök:")
            for idx, (device_id, device) in enumerate(controller.devices.items(), 1):
                status = device.get("status", device.get("value", "N/A"))
                print(f"{idx}. {device['name']} ({device_id}) - Állapot: {status}")
        
        elif choice == "2":
            print("\nVálassz egy eszközt a vezérléshez:")
            devices = list(controller.devices.items())
            for idx, (device_id, device) in enumerate(devices, 1):
                print(f"{idx}. {device['name']} ({device_id})")
            
            try:
                device_idx = int(input("Eszköz száma: ")) - 1
                if 0 <= device_idx < len(devices):
                    device_id, device = devices[device_idx]
                    
                    if "sensor" in device["type"]:
                        print("A szenzorok nem vezérelhetők közvetlenül.")
                        continue
                    
                    if device["type"] in ["light", "fan", "ac"]:
                        status = input("Állapot (be/ki): ").lower() in ["be", "on", "1", "true", "igen", "yes"]
                        command = {"status": status}
                        
                        if device["type"] == "fan" and status:
                            speed = int(input("Sebesség (1-3): "))
                            command["speed"] = max(1, min(3, speed))
                        elif device["type"] == "ac" and status:
                            temp = int(input("Hőmérséklet (18-30): "))
                            command["temp"] = max(18, min(30, temp))
                        
                        controller.control_device(device_id, command)
                        print(f"Eszköz vezérlése: {device['name']} - {command}")
                    else:
                        print(f"Az eszköztípus ({device['type']}) nem támogatott.")
                else:
                    print("Érvénytelen eszközszám!")
            except ValueError:
                print("Érvénytelen bemenet!")
        
        elif choice == "3":
            print("\nBeállított automatizálások:")
            for idx, routine in enumerate(controller.routines, 1):
                trigger = routine["trigger"]
                trigger_text = f"{trigger['device_id']} {trigger['condition']} {trigger['value']}"
                action_count = len(routine["actions"])
                print(f"{idx}. {routine['name']} - Ha {trigger_text}, akkor {action_count} művelet")
        
        elif choice == "4":
            # Egyszerűsített verzió - csak előre definiált típusokkal
            print("\nÚj automatizálás hozzáadása:")
            name = input("Automatizálás neve: ")
            
            print("\nVálassz egy szenzort kiváltó okként:")
            sensors = [(device_id, device) for device_id, device in controller.devices.items() if "sensor" in device["type"]]
            for idx, (device_id, device) in enumerate(sensors, 1):
                print(f"{idx}. {device['name']} ({device_id})")
            
            try:
                sensor_idx = int(input("Szenzor száma: ")) - 1
                if 0 <= sensor_idx < len(sensors):
                    sensor_id, sensor = sensors[sensor_idx]
                    
                    print("\nVálassz egy feltételt:")
                    print("1. Felett (above)")
                    print("2. Alatt (below)")
                    print("3. Egyenlő (equal)")
                    condition_choice = input("Feltétel száma: ")
                    
                    conditions = ["above", "below", "equal"]
                    if condition_choice in ["1", "2", "3"]:
                        condition = conditions[int(condition_choice) - 1]
                        
                        value = input("Érték: ")
                        if sensor["type"] == "temp_sensor":
                            value = float(value)
                        elif value.lower() in ["true", "igen", "yes"]:
                            value = True
                        elif value.lower() in ["false", "nem", "no"]:
                            value = False
                        
                        print("\nVálassz egy eszközt a művelethez:")
                        actuators = [(device_id, device) for device_id, device in controller.devices.items() 
                                     if "sensor" not in device["type"]]
                        for idx, (device_id, device) in enumerate(actuators, 1):
                            print(f"{idx}. {device['name']} ({device_id})")
                        
                        actuator_idx = int(input("Eszköz száma: ")) - 1
                        if 0 <= actuator_idx < len(actuators):
                            actuator_id, actuator = actuators[actuator_idx]
                            
                            status = input("Állapot (be/ki): ").lower() in ["be", "on", "1", "true", "igen", "yes"]
                            command = {"status": status}
                            
                            # Automatizálás létrehozása
                            controller.add_routine(
                                name=name,
                                trigger={
                                    "type": "sensor", 
                                    "device_id": sensor_id, 
                                    "condition": condition, 
                                    "value": value
                                },
                                actions=[{"device_id": actuator_id, "command": command}]
                            )
                        else:
                            print("Érvénytelen eszközszám!")
                    else:
                        print("Érvénytelen feltétel!")
                else:
                    print("Érvénytelen szenzorszám!")
            except ValueError:
                print("Érvénytelen bemenet!")
        
        elif choice == "5":
            controller.start_monitoring()
        
        elif choice == "6":
            controller.stop_monitoring()
        
        elif choice == "7":
            print("\nSzimuláció indítása...")
            # Szimuláció futtatása
            simulation_test(controller)
        
        elif choice == "8":
            print("Kilépés...")
            controller.stop_monitoring()
            break
        
        else:
            print("Érvénytelen választás, próbáld újra!")

def simulation_test(controller):
    """
    Egyszerű szimulációs teszt a rendszer működésének bemutatására.
    """
    print("\n=== Szimuláció indítása ===")
    
    # Monitorozás indítása
    controller.start_monitoring()
    
    try:
        # 1. Emeljük a hőmérsékletet 26 fokra (a hűtési automatizálás teszteléséhez)
        print("\n1. Teszt: Hőmérséklet emelése 26 fokra")
        temp_sensor_id = next((device_id for device_id, device in controller.devices.items() 
                              if device["type"] == "temp_sensor"), None)
        if temp_sensor_id:
            controller.pt_interface.device_registry[temp_sensor_id]["value"] = 26.0
            print(f"Hőmérséklet beállítva: 26.0°C")
            time.sleep(3)  # Várunk, hogy az automatizálás lefusson
        
        # 2. Teszteljük a mozgásérzékelőt
        print("\n2. Teszt: Mozgás szimulálása")
        motion_sensor_id = next((device_id for device_id, device in controller.devices.items() 
                                if device["type"] == "motion_sensor"), None)
        if motion_sensor_id:
            controller.pt_interface.device_registry[motion_sensor_id]["value"] = True
            print("Mozgás érzékelve")
            time.sleep(3)  # Várunk, hogy az automatizálás lefusson
            controller.pt_interface.device_registry[motion_sensor_id]["value"] = False
            print("Mozgás megszűnt")
        
        # 3. Teszteljük a füstérzékelőt
        print("\n3. Teszt: Füst érzékelése")
        smoke_sensor_id = next((device_id for device_id, device in controller.devices.items() 
                               if device["type"] == "smoke_sensor"), None)
        if smoke_sensor_id:
            controller.pt_interface.device_registry[smoke_sensor_id]["value"] = True
            print("Füst érzékelve - vészhelyzet!")
            time.sleep(3)  # Várunk, hogy az automatizálás lefusson
            controller.pt_interface.device_registry[smoke_sensor_id]["value"] = False
            print("Füst megszűnt")
        
        # 4. Állítsuk vissza a normál hőmérsékletet
        print("\n4. Teszt: Hőmérséklet visszaállítása normál értékre")
        if temp_sensor_id:
            controller.pt_interface.device_registry[temp_sensor_id]["value"] = 22.0
            print(f"Hőmérséklet visszaállítva: 22.0°C")
        
        time.sleep(3)  # Várjunk még egy kicsit az utolsó állapotjelentésre
        
    finally:
        # Monitorozás leállítása
        controller.stop_monitoring()
    
    print("\n=== Szimuláció befejezve ===")

# --------------------------
# Főprogram
# --------------------------
def main():
    print("=== Okos Otthon Vezérlő Python Program ===")
    print("Ez a program a Cisco Packet Tracer-rel együttműködve")
    print("vezérli az okos otthon eszközöket")
    print("=======================================\n")
    
    # Packet Tracer interfész létrehozása
    pt_interface = PacketTracerInterface()
    
    # Smart Home vezérlő létrehozása
    controller = SmartHomeController(pt_interface)
    
    # Rendszer inicializálása
    if controller.initialize():
        print(f"Rendszer inicializálva, {len(controller.devices)} eszköz felderítve")
        
        # Interaktív menü indítása
        interactive_menu(controller)
    else:
        print("Nem sikerült inicializálni a rendszert!")
    
    # Kapcsolat lezárása
    pt_interface.close()

if __name__ == "__main__":
    main()