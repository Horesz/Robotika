// IoT eszköz programozás Packet Tracerben - Példa egy lámpa vezérléséhez

// Változók
var deviceId = "Light1";
var status = false;  // false = kikapcsolva, true = bekapcsolva

function setup() {
  // IoT eszköz inicializálása
  IOT.setDeviceProperty("ipaddress", "192.168.1.100");
  IOT.setDeviceProperty("port", 80);
  IOT.setDeviceProperty("protocol", "TCP");
  
  // Eszköz azonosító beállítása
  IOT.setDeviceProperty("deviceId", deviceId);
  
  // Regisztráció a Home Gateway-en
  registerToGateway();
  
  // Kezdeti állapot beállítása
  updateStatus(status);
  
  // Eseménykezelő beállítása bejövő kapcsolatokhoz
  IOT.onConnection(handleConnection);
}

function registerToGateway() {
  // Regisztráljuk az eszközt a Home Gateway-en
  var gateway = {
    address: "192.168.1.1",
    port: 5000
  };
  
  // Eszköz adatok összeállítása
  var registrationData = {
    deviceId: deviceId,
    type: "light",
    name: "Smart Light",
    capabilities: ["on", "off"]
  };
  
  // Regisztrációs kérés küldése
  IOT.connect(gateway.address, gateway.port, function(success) {
    if (success) {
      IOT.send(JSON.stringify({
        command: "REGISTER",
        data: registrationData
      }));
    } else {
      console.log("Nem sikerült kapcsolódni a Gateway-hez");
    }
  });
}

function handleConnection(clientId) {
  // Eseménykezelő beállítása bejövő adatokhoz
  IOT.onData(clientId, function(data) {
    try {
      // A kapott parancs feldolgozása
      var command = JSON.parse(data);
      
      if (command.action === "SET_STATE") {
        // Állapot módosítása
        if (typeof command.state === "boolean") {
          status = command.state;
          updateStatus(status);
          
          // Válasz küldése
          IOT.send(clientId, JSON.stringify({
            status: "OK",
            deviceId: deviceId,
            state: status
          }));
        }
      } else if (command.action === "GET_STATE") {
        // Állapot lekérdezése
        IOT.send(clientId, JSON.stringify({
          status: "OK",
          deviceId: deviceId,
          state: status
        }));
      }
    } catch (e) {
      console.log("Hiba a parancs feldolgozása során: " + e);
      IOT.send(clientId, JSON.stringify({
        status: "ERROR",
        message: "Érvénytelen parancs"
      }));
    }
  });
}

function updateStatus(newStatus) {
  // Frissítjük a lámpa állapotát
  status = newStatus;
  
  // Fizikai állapot frissítése a Packet Tracerben
  if (status) {
    // Lámpa bekapcsolása
    IOT.setPowerState("ON");
    IOT.setColor(255, 255, 200);  // Meleg fehér
    IOT.setBrightness(100);
  } else {
    // Lámpa kikapcsolása
    IOT.setPowerState("OFF");
    IOT.setBrightness(0);
  }
}

// Program indítása
setup();