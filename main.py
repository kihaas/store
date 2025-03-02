import os
from website import create_app
from website.extensions import db

app = create_app()

with app.app_context():
   os.makedirs(os.path.join(os.getcwd(), 'instance'), exist_ok=True)
   db.create_all()

if __name__ == '__main__':
   app.run(debug=True)
