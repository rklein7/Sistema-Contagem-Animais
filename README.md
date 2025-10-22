# 🐄 Sistema de Contagem de Animais

Sistema automatizado de contagem de animais utilizando Raspberry Pi com sensor ultrassônico, integrado a um dashboard web em tempo real.

## 📋 Sobre o Projeto

Este sistema foi desenvolvido para automatizar a contagem de animais em propriedades rurais, utilizando tecnologia IoT de baixo custo. O projeto integra hardware (Raspberry Pi com sensores), backend (Flask + SQLite) e frontend (React) para fornecer uma solução completa de monitoramento.

### 🎯 Funcionalidades

- ✅ Detecção automática de animais via sensor ultrassônico
- ✅ Feedback visual (LED) e sonoro (Buzzer) em tempo real
- ✅ Dashboard web responsivo com estatísticas
- ✅ Armazenamento persistente em banco de dados
- ✅ Monitoramento de múltiplos dispositivos Raspberry Pi
- ✅ Relatórios diários, semanais e mensais
- ✅ Sistema de autenticação de usuários
- ✅ Atualização automática do dashboard a cada 5 segundos

## 🏗️ Arquitetura

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Raspberry Pi   │─────>│ Flask API    │<─────│  React App      │
│  + Sensor HC-SR04│ HTTP │ + SQLite DB  │ HTTP │  (Dashboard)    │
│  + LED + Buzzer │      │              │      │                 │
└─────────────────┘      └──────────────┘      └─────────────────┘
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados
- **Flask-CORS** - Gerenciamento de CORS
- **PyJWT** - Autenticação via tokens JWT
- **Werkzeug** - Hash de senhas

### Frontend
- **React** - Biblioteca JavaScript
- **Tailwind CSS** - Framework CSS
- **Fetch API** - Comunicação HTTP

### Hardware
- **Raspberry Pi** (qualquer modelo com GPIO)
- **Sensor Ultrassônico HC-SR04**
- **LED 5mm**
- **Buzzer Ativo 5V**
- **Resistores** (330Ω, 1kΩ, 2kΩ)

## 📦 Instalação

### Pré-requisitos

- Python 3.7+
- Node.js 14+
- Raspberry Pi com Raspberry Pi OS
- Componentes eletrônicos listados acima

### 1️⃣ Backend (Servidor Flask)

```bash
# Clone o repositório
git clone https://github.com/rklein7/Sistema-Contagem-Animais.git
cd Sistema-Contagem-Animais

# Instale as dependências Python
pip install -r requirements.txt

# Crie o banco de dados
python manage_db.py create

# (Opcional) Crie um usuário de teste
python manage_db.py testuser

# Execute o servidor
python app.py
```

O servidor estará rodando em `http://localhost:5000`

### 2️⃣ Frontend (React)

```bash
# Entre na pasta do frontend
cd login-frontend

# Instale as dependências
npm install

# Execute o projeto
npm start
```

O frontend estará disponível em `http://localhost:3000`

### 3️⃣ Raspberry Pi

```bash
# Conecte-se via SSH
ssh pi@IP_DA_RASPBERRY

# Instale dependências
sudo apt-get update
sudo apt-get install python3-rpi.gpio -y
pip3 install requests

# Transfira o script
scp raspberry_counter.py pi@IP_DA_RASPBERRY:/home/pi/

# Configure o IP do servidor no script
nano raspberry_counter.py
# Altere: API_URL = "http://SEU_IP:5000/api"

# Execute
python3 raspberry_counter.py
```

## 🔌 Diagrama de Conexão

### Sensor Ultrassônico HC-SR04
```
HC-SR04          Raspberry Pi
--------         ------------
VCC       --->   5V (Pino 2)
TRIG      --->   GPIO 23 (Pino 16)
ECHO      --->   GPIO 24 (Pino 18) *via divisor de tensão*
GND       --->   GND (Pino 6)
```

**⚠️ IMPORTANTE:** O pino ECHO emite 5V, mas o GPIO aceita apenas 3.3V. Use um divisor de tensão:
```
ECHO --> Resistor 1kΩ --> GPIO 24
                       |
                  Resistor 2kΩ --> GND
```

### LED
```
GPIO 17 (Pino 11) --> Resistor 330Ω --> LED (ânodo) --> GND (cátodo)
```

### Buzzer
```
GPIO 27 (Pino 13) --> Resistor 330Ω --> Buzzer (+) --> GND (-)
```

## 🚀 Uso

### Acessar o Sistema

1. Abra o navegador em `http://localhost:3000`
2. Faça login ou cadastre-se
3. Visualize o dashboard com estatísticas em tempo real

### Testar Componentes da Raspberry Pi

```bash
# Modo de teste (verifica sensor, LED e buzzer)
python3 raspberry_counter.py test
```

### Comandos do Gerenciador de BD

```bash
# Ver usuários cadastrados
python manage_db.py users

# Ver contagens registradas
python manage_db.py counts

# Ver dispositivos conectados
python manage_db.py devices

# Resetar banco de dados
python manage_db.py reset
```

## 📊 API Endpoints

### Autenticação
- `POST /api/register` - Cadastrar usuário
- `POST /api/login` - Fazer login
- `GET /api/verify` - Verificar token

### Contagens
- `GET /api/counts` - Listar todas as contagens (requer autenticação)
- `GET /api/counts/today` - Contagens do dia (requer autenticação)
- `GET /api/counts/stats` - Estatísticas gerais (requer autenticação)
- `POST /api/count` - Registrar contagem (público - para Raspberry Pi)

### Dispositivos
- `GET /api/devices` - Listar dispositivos (requer autenticação)
- `POST /api/devices/register` - Registrar dispositivo (requer autenticação)
- `POST /api/devices/<id>/heartbeat` - Atualizar status (público)
- `DELETE /api/devices/<id>` - Remover dispositivo (requer autenticação)

## ⚙️ Configuração

### Ajustar Distância de Detecção

Edite `raspberry_counter.py`:
```python
DISTANCE_THRESHOLD = 15  # Distância em cm
```

### Ajustar Cooldown

```python
COOLDOWN_TIME = 3  # Tempo em segundos entre detecções
```

### Alterar Tipo de Animal

```python
ANIMAL_TYPE = "bovino"  # ou "equino", "ovino", "caprino", etc.
```

### Configurar Inicialização Automática

```bash
# Criar serviço systemd
sudo nano /etc/systemd/system/animal-counter.service

# Habilitar e iniciar
sudo systemctl enable animal-counter.service
sudo systemctl start animal-counter.service
```

## 🐛 Solução de Problemas

### Sensor não responde
- Verifique as conexões físicas
- Confirme o divisor de tensão no pino ECHO
- Execute o modo de teste: `python3 raspberry_counter.py test`

### Não conecta no servidor
- Verifique o IP configurado no script
- Teste com ping: `ping IP_DO_SERVIDOR`
- Confirme que o Flask está rodando
- Verifique firewall

### LED ou Buzzer não funcionam
- Verifique a polaridade dos componentes
- Confirme os resistores corretos
- Teste os pinos individualmente

### Erro "GPIO já em uso"
```bash
# Limpe o GPIO
python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"
```

## 📁 Estrutura do Projeto

```
Sistema-Contagem-Animais/
├── app.py                      # Backend Flask com SQLAlchemy
├── manage_db.py                # Gerenciador do banco de dados
├── raspberry_counter.py        # Script para Raspberry Pi
├── requirements.txt            # Dependências Python
├── animal_counter.db           # Banco de dados SQLite
└── login-frontend/             # Frontend React
    ├── src/
    │   ├── App.js              # Componente principal
    │   ├── App.css             # Estilos (se usando CSS puro)
    │   ├── index.css           # Estilos globais com Tailwind
    │   └── index.js            # Entry point
    ├── public/
    │   └── index.html
    └── package.json
```

## 👥 Alunos participantes

- **Bruno da Motta Pasquetti** - 1334141
- **Gabriel Brocco de Oliveira** - 1135058
- **Pedro Henrique de Bortolli** - 1129494
- **Rafael Klein** - 1134873

## 🎓 Contexto Acadêmico

Este projeto foi desenvolvido como parte de um trabalho acadêmico da disciplina de Hardware, demonstrando a integração entre IoT, desenvolvimento web e banco de dados.
