#!/Users/jakubdudek/Projects/flask/StockWebApp/venv/bin python3.4
import os
from app import create_app
from flask.ext.script import Manager
from app import db
from app.models import User
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def adduser(email, username, admin=False):
    """Register a new user."""
    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt='Confirm: ')
    if password != password2:
        import sys
        sys.exit('Error: passwords do not match.')
    db.create_all()
    user = User(email=email, username=username, password=password,
                is_admin=admin)
    db.session.add(user)
    db.session.commit()
    print('User {0} was registered successfully.'.format(username))


if __name__ == '__main__':
    manager.run()

