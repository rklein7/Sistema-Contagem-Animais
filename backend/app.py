from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-mude-em-producao'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///animal_counter.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)

# ========== MODELOS DO BANCO DE DADOS ==========

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat()
        }

class Count(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    device_id = db.Column(db.String(36), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    animal_type = db.Column(db.String(50), default='desconhecido')
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'count': self.count,
            'animal_type': self.animal_type,
            'timestamp': self.timestamp.isoformat()
        }

class Device(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), default='Não especificado')
    status = db.Column(db.String(20), default='ativo')
    registered_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'status': self.status,
            'registered_at': self.registered_at.isoformat(),
            'last_seen': self.last_seen.isoformat()
        }

# ========== INICIALIZAR BANCO DE DADOS ==========

def init_db():
    with app.app_context():
        db.create_all()
        print("Banco de dados inicializado!")

# ========== DECORADOR DE AUTENTICAÇÃO ==========

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token não fornecido'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(username=data['username']).first()
            
            if not current_user:
                return jsonify({'message': 'Usuário não encontrado'}), 401
                
        except Exception as e:
            return jsonify({'message': 'Token inválido', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username e password são obrigatórios'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Usuário já existe'}), 400
    
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuário cadastrado com sucesso'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao cadastrar usuário', 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Username e password são obrigatórios'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Credenciais inválidas'}), 401
    
    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': token,
        'username': username
    }), 200

@app.route('/api/verify', methods=['GET'])
@token_required
def verify(current_user):
    return jsonify({
        'message': 'Token válido',
        'username': current_user.username
    }), 200

# ========== ROTAS DE CONTAGEM DE ANIMAIS ==========

@app.route('/api/counts', methods=['GET'])
@token_required
def get_counts(current_user):
    counts = Count.query.order_by(Count.timestamp.desc()).all()
    return jsonify({
        'counts': [count.to_dict() for count in counts],
        'total': len(counts)
    }), 200

@app.route('/api/counts/today', methods=['GET'])
@token_required
def get_today_counts(current_user):
    today = datetime.datetime.now().date()
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_end = datetime.datetime.combine(today, datetime.time.max)
    
    today_counts = Count.query.filter(
        Count.timestamp >= today_start,
        Count.timestamp <= today_end
    ).order_by(Count.timestamp.desc()).all()
    
    total_animals = sum(count.count for count in today_counts)
    
    return jsonify({
        'counts': [count.to_dict() for count in today_counts],
        'total_today': total_animals,
        'records': len(today_counts)
    }), 200

@app.route('/api/counts/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    now = datetime.datetime.now()
    today = now.date()
    today_start = datetime.datetime.combine(today, datetime.time.min)
    week_ago = now - datetime.timedelta(days=7)
    month_ago = now - datetime.timedelta(days=30)
    
    all_counts = Count.query.all()
    total_animals = sum(count.count for count in all_counts)
    
    today_counts = Count.query.filter(Count.timestamp >= today_start).all()
    today_total = sum(count.count for count in today_counts)
    
    week_counts = Count.query.filter(Count.timestamp >= week_ago).all()
    week_total = sum(count.count for count in week_counts)
    
    month_counts = Count.query.filter(Count.timestamp >= month_ago).all()
    month_total = sum(count.count for count in month_counts)
    
    return jsonify({
        'total_animals': total_animals,
        'total_records': len(all_counts),
        'today': today_total,
        'this_week': week_total,
        'this_month': month_total
    }), 200

@app.route('/api/count', methods=['POST'])
def add_count():
    data = request.get_json()
    
    device_id = data.get('device_id', 'unknown')
    count_value = data.get('count', 0)
    animal_type = data.get('animal_type', 'desconhecido')
    
    count_entry = Count(
        id=str(uuid.uuid4()),
        device_id=device_id,
        count=count_value,
        animal_type=animal_type
    )
    
    try:
        db.session.add(count_entry)
        db.session.commit()
        
        return jsonify({
            'message': 'Contagem registrada com sucesso',
            'data': count_entry.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao registrar contagem', 'error': str(e)}), 500

# ========== ROTAS DE GERENCIAMENTO DE DISPOSITIVOS RASP ==========

@app.route('/api/devices', methods=['GET'])
@token_required
def get_devices(current_user):
    devices = Device.query.all()
    return jsonify({
        'devices': [device.to_dict() for device in devices],
        'total': len(devices)
    }), 200

@app.route('/api/devices/register', methods=['POST'])
@token_required
def register_device(current_user):
    data = request.get_json()
    
    device_name = data.get('name', 'Raspberry Pi')
    location = data.get('location', 'Não especificado')
    device_id = str(uuid.uuid4())
    
    device = Device(
        id=device_id,
        name=device_name,
        location=location,
        status='ativo'
    )
    
    try:
        db.session.add(device)
        db.session.commit()
        
        return jsonify({
            'message': 'Dispositivo registrado com sucesso',
            'device': device.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao registrar dispositivo', 'error': str(e)}), 500

@app.route('/api/devices/<device_id>/heartbeat', methods=['POST'])
def device_heartbeat(device_id):
    device = Device.query.get(device_id)
    
    if not device:
        return jsonify({'message': 'Dispositivo não encontrado'}), 404
    
    device.last_seen = datetime.datetime.utcnow()
    device.status = 'ativo'
    
    try:
        db.session.commit()
        return jsonify({'message': 'Heartbeat registrado'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao atualizar dispositivo', 'error': str(e)}), 500

@app.route('/api/devices/<device_id>', methods=['DELETE'])
@token_required
def delete_device(current_user, device_id):
    device = Device.query.get(device_id)
    
    if not device:
        return jsonify({'message': 'Dispositivo não encontrado'}), 404
    
    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Dispositivo removido com sucesso'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Erro ao remover dispositivo', 'error': str(e)}), 500

# ========== ROTA DE TESTE ==========

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({
        'message': 'Servidor funcionando!',
        'timestamp': datetime.datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    init_db()  
    app.run(debug=True, host='0.0.0.0', port=5000)