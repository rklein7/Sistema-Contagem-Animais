import RPi.GPIO as GPIO
import requests
import time
import uuid
from datetime import datetime
import json

# ========== CONFIGURAÇÕES ==========

API_URL = "http://127.0.0.1:5000/api"  # TROCAR PELO IP DO SEU SERVIDOR
DEVICE_ID = str(uuid.uuid4())  # ID único do dispositivo
DEVICE_NAME = "Raspberry Pi - Porteira Principal"
DEVICE_LOCATION = "Entrada do Pasto"

# Pinos GPIO (BCM)
TRIG_PIN = 23        # Pino TRIG do sensor ultrassônico
ECHO_PIN = 24        # Pino ECHO do sensor ultrassônico
LED_PIN = 17         # Pino do LED
BUZZER_PIN = 27      # Pino do Buzzer

# Configurações de detecção
DISTANCE_THRESHOLD = 15  # Distância em cm para detectar presença
COOLDOWN_TIME = 3        # Tempo em segundos entre detecções (evita contar o mesmo animal)
ANIMAL_TYPE = "bovino"   # Tipo de animal sendo monitorado

# ========== CONFIGURAÇÃO DO GPIO ==========

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.setup(BUZZER_PIN, GPIO.OUT)
    
    GPIO.output(TRIG_PIN, False)
    GPIO.output(LED_PIN, False)
    GPIO.output(BUZZER_PIN, False)
    
    print("✅ GPIO configurado com sucesso!")

# ========== FUNÇÕES DO SENSOR ==========

def measure_distance():

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  
    GPIO.output(TRIG_PIN, False)
    
    pulse_start = time.time()
    pulse_end = time.time()
    timeout = time.time() + 0.1  
    
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None
    
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  
    distance = round(distance, 2)
    
    return distance

# ========== FUNÇÕES DE FEEDBACK ==========

def trigger_alert():
    GPIO.output(LED_PIN, True)
    
    for _ in range(3):
        GPIO.output(BUZZER_PIN, True)
        time.sleep(0.1)
        GPIO.output(BUZZER_PIN, False)
        time.sleep(0.1)
    
    time.sleep(1.8)
    GPIO.output(LED_PIN, False)

# ========== FUNÇÕES DE COMUNICAÇÃO COM API ==========

def send_heartbeat():
    try:
        response = requests.post(
            f"{API_URL}/devices/{DEVICE_ID}/heartbeat",
            timeout=5
        )
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❤️  Heartbeat enviado")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Erro no heartbeat: {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro ao enviar heartbeat: {e}")
        return False

def send_count(count=1, animal_type=ANIMAL_TYPE):
    try:
        data = {
            "device_id": DEVICE_ID,
            "count": count,
            "animal_type": animal_type
        }
        
        response = requests.post(
            f"{API_URL}/count",
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Contagem enviada: {count} {animal_type}(s)")
            return True
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Erro ao enviar: {response.status_code}")
            print(f"    Resposta: {response.text}")
            return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro na comunicação: {e}")
        return False

def register_device():
    try:
        print(f"[INFO] Device ID: {DEVICE_ID}")
        print(f"[INFO] Para registrar, use o frontend ou API com token")
    except Exception as e:
        print(f"[INFO] Registro manual necessário: {e}")

# ========== LOOP PRINCIPAL ==========

class AnimalCounter:
    def __init__(self):
        self.running = False
        self.total_count = 0
        self.last_detection_time = 0
        
    def start(self):
        self.running = True
        print("\n" + "="*60)
        print("🐄 SISTEMA DE CONTAGEM DE ANIMAIS - RASPBERRY PI")
        print("="*60)
        print(f"Device ID: {DEVICE_ID}")
        print(f"Servidor: {API_URL}")
        print(f"Distância de detecção: {DISTANCE_THRESHOLD}cm")
        print(f"Cooldown: {COOLDOWN_TIME}s")
        print("="*60 + "\n")
        
        setup_gpio()
        register_device()
        
        print("🚀 Sistema iniciado! Aguardando detecções...\n")
        
        last_heartbeat = time.time()
        
        try:
            while self.running:
                if time.time() - last_heartbeat > 60:
                    send_heartbeat()
                    last_heartbeat = time.time()
                
                distance = measure_distance()
                
                if distance is not None:
                    if distance < DISTANCE_THRESHOLD:
                        current_time = time.time()
                        
                        if current_time - self.last_detection_time > COOLDOWN_TIME:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🎯 DETECÇÃO! Distância: {distance}cm")
                            
                            trigger_alert()
                            
                            if send_count(1, ANIMAL_TYPE):
                                self.total_count += 1
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Total contado hoje: {self.total_count}")
                            
                            self.last_detection_time = current_time
                            print()  
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Sistema interrompido pelo usuário")
            self.stop()
        except Exception as e:
            print(f"\n\n❌ Erro fatal: {e}")
            self.stop()
    
    def stop(self):
        self.running = False
        GPIO.cleanup()
        print(f"\n📊 Total de animais contados nesta sessão: {self.total_count}")
        print("✅ GPIO limpo. Sistema encerrado.\n")

# ========== MODO DE TESTE ==========

def test_mode():
    print("\n🔧 MODO DE TESTE")
    print("="*60)
    
    setup_gpio()
    
    print("\n1. Testando LED...")
    GPIO.output(LED_PIN, True)
    time.sleep(1)
    GPIO.output(LED_PIN, False)
    print("   ✅ LED OK")
    
    print("\n2. Testando Buzzer...")
    GPIO.output(BUZZER_PIN, True)
    time.sleep(0.5)
    GPIO.output(BUZZER_PIN, False)
    print("   ✅ Buzzer OK")
    
    print("\n3. Testando Sensor Ultrassônico...")
    for i in range(5):
        distance = measure_distance()
        if distance:
            print(f"   Medição {i+1}: {distance}cm")
        else:
            print(f"   Medição {i+1}: Erro")
        time.sleep(0.5)
    print("   ✅ Sensor OK")
    
    print("\n4. Testando alerta completo...")
    trigger_alert()
    print("   ✅ Alerta OK")
    
    GPIO.cleanup()
    print("\n✅ Todos os testes concluídos!\n")

# ========== EXECUÇÃO ==========

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_mode()
    else:
        counter = AnimalCounter()
        counter.start()