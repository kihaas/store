import os
from website import create_app
from website.extensions import db


# Создаем приложение
app = create_app()

# Создаем базу данных, если она не существует
with app.app_context():
    os.makedirs(os.path.join(os.getcwd(), 'instance'), exist_ok=True)
    db.create_all()


# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
