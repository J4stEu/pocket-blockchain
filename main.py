from app import app
from app import migrate
import routes


if __name__ == '__main__':
    app.run(host='localhost')
    migrate.run()
