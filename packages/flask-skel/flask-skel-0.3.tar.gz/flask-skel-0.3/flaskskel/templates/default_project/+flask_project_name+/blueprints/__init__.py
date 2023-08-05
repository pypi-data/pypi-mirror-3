from .home import home_bp

def register_blue_prints(app):
    app.register_blueprint(home_bp)