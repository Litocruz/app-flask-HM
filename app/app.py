import os
import redis
import json
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuración ---
# Lee las variables de entorno para la configuración
db_user = os.getenv("POSTGRES_USER", "user")
db_password = os.getenv("POSTGRES_PASSWORD", "password")
db_name = os.getenv("POSTGRES_DB", "portfolio_db")
db_host = os.getenv("DB_HOST", "postgres")
redis_host = os.getenv("REDIS_HOST", "redis")

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa la base de datos y Redis
db = SQLAlchemy(app)
cache = redis.Redis(host=redis_host, port=6379)


# --- Modelo de la Base de Datos ---
class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False) # Guardado como texto, separado por comas

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'summary': self.summary,
            'skills': [skill.strip() for skill in self.skills.split(',')]
        }

# --- Rutas de la Aplicación ---
@app.route('/')
def home():
    try:
        # 1. Intenta obtener los datos desde el caché de Redis
        cached_portfolio = cache.get('portfolio_data')
        if cached_portfolio:
            portfolio_data = json.loads(cached_portfolio)
            # Añadimos un indicador para saber que vino del caché
            portfolio_data['source'] = 'cache'
            return render_template('index.html', portfolio=portfolio_data)

        # 2. Si no está en caché, obtén los datos de la base de datos
        portfolio_item = Portfolio.query.first()
        if not portfolio_item:
            return "No portfolio data found. Run 'flask init-db' to initialize.", 404

        portfolio_data = portfolio_item.to_dict()

        # 3. Guarda los datos en el caché para futuras peticiones (con expiración de 1 hora)
        cache.setex('portfolio_data', 3600, json.dumps(portfolio_data))

        # Añadimos un indicador para saber que vino de la base de datos
        portfolio_data['source'] = 'database'
        return render_template('index.html', portfolio=portfolio_data)

    except Exception as e:
        # Si hay un error (ej. la BD no está lista), muestra un mensaje amigable
        return render_template('error.html', message=str(e)), 500


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'uptime': 'running'})


# --- Comandos de CLI ---
@app.cli.command('init-db')
def init_db_command():
    """Crea las tablas de la base de datos y las inicializa con datos de ejemplo."""
    with app.app_context():
        db.create_all()
        # Limpia la caché al reiniciar la base de datos
        cache.delete('portfolio_data')
        # Verifica si ya existen datos para no duplicarlos
        if not Portfolio.query.first():
            # Datos de ejemplo
            sample_data = Portfolio(
                name="Roxs",
                title="Ingeniera DevOps & Cloud",
                summary="Apasionada por la automatización, la infraestructura como código y el despliegue continuo. Experta en crear pipelines de CI/CD robustos y escalables.",
                skills="Docker, Kubernetes, Terraform, Ansible, Jenkins, GitHub Actions, AWS, GCP"
            )
            db.session.add(sample_data)
            db.session.commit()
            print("Base de datos inicializada con datos de ejemplo y caché limpiada.")
        else:
            print("La base de datos ya contiene datos. No se han añadido nuevos.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)