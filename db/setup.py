from db.models import init_db

if __name__ == "__main__":
    print("Inicializando banco de dados...")
    session = init_db()
    print("Banco de dados inicializado com sucesso!")
    session.close()
