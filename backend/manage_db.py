"""
Script para gerenciar o banco de dados
"""
from app import app, db, User, Count, Device
import sys

def create_database():
    """Cria todas as tabelas do banco de dados"""
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados criado com sucesso!")

def drop_database():
    """Remove todas as tabelas do banco de dados"""
    with app.app_context():
        db.drop_all()
        print("✅ Banco de dados removido com sucesso!")

def reset_database():
    """Reseta o banco de dados (remove e cria novamente)"""
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("✅ Banco de dados resetado com sucesso!")

def show_users():
    """Mostra todos os usuários cadastrados"""
    with app.app_context():
        users = User.query.all()
        print(f"\n📊 Total de usuários: {len(users)}\n")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Username: {user.username}")
            print(f"Criado em: {user.created_at}")
            print("-" * 50)

def show_counts():
    """Mostra todas as contagens registradas"""
    with app.app_context():
        counts = Count.query.all()
        print(f"\n📊 Total de contagens: {len(counts)}\n")
        total_animals = sum(count.count for count in counts)
        print(f"Total de animais contados: {total_animals}\n")
        
        for count in counts[:10]:  # Mostra apenas os 10 primeiros
            print(f"ID: {count.id}")
            print(f"Dispositivo: {count.device_id}")
            print(f"Quantidade: {count.count}")
            print(f"Tipo: {count.animal_type}")
            print(f"Data: {count.timestamp}")
            print("-" * 50)

def show_devices():
    """Mostra todos os dispositivos registrados"""
    with app.app_context():
        devices = Device.query.all()
        print(f"\n📊 Total de dispositivos: {len(devices)}\n")
        for device in devices:
            print(f"ID: {device.id}")
            print(f"Nome: {device.name}")
            print(f"Localização: {device.location}")
            print(f"Status: {device.status}")
            print(f"Último sinal: {device.last_seen}")
            print("-" * 50)

def create_test_user():
    """Cria um usuário de teste"""
    with app.app_context():
        from werkzeug.security import generate_password_hash
        
        username = "admin"
        password = "admin123"
        
        # Verificar se já existe
        if User.query.filter_by(username=username).first():
            print(f"❌ Usuário '{username}' já existe!")
            return
        
        user = User(
            username=username,
            password=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Usuário de teste criado!")
        print(f"Username: {username}")
        print(f"Password: {password}")

def show_help():
    """Mostra menu de ajuda"""
    print("\n" + "="*60)
    print("GERENCIADOR DE BANCO DE DADOS - Sistema de Contagem de Animais")
    print("="*60)
    print("\nComandos disponíveis:\n")
    print("  create       - Cria o banco de dados")
    print("  drop         - Remove o banco de dados")
    print("  reset        - Reseta o banco de dados")
    print("  users        - Mostra todos os usuários")
    print("  counts       - Mostra todas as contagens")
    print("  devices      - Mostra todos os dispositivos")
    print("  testuser     - Cria um usuário de teste (admin/admin123)")
    print("  help         - Mostra esta mensagem")
    print("\nExemplo de uso:")
    print("  python manage_db.py create")
    print("  python manage_db.py testuser")
    print("  python manage_db.py users")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'create': create_database,
        'drop': drop_database,
        'reset': reset_database,
        'users': show_users,
        'counts': show_counts,
        'devices': show_devices,
        'testuser': create_test_user,
        'help': show_help
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ Comando '{command}' não reconhecido!")
        show_help()