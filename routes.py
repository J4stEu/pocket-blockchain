from app import app


@app.route('/')
def index():
    return "<p>Blockchain application</p>"
