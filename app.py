import os
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    # Configuração de versão da aplicação
    # (Pode ser sobrescrita via variável de ambiente APP_VERSION)
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    APP_ENV = os.getenv("APP_ENV", "production")

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "service": "devops-python-api",
            "message": "DevOps Python API operacional!",
            "version": APP_VERSION,
            "status": "online"
        }), 200

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "version": APP_VERSION,
            "environment": APP_ENV
        }), 200

    @app.route("/api/v1/info", methods=["GET"])
    def info():
        return jsonify({
            "name": "devops-python-api",
            "description": "API REST Python com esteira CI/CD (GitHub Actions, Docker, AWS ECR e EC2)",
            "discipline": "Integração DevOps",
            "version": APP_VERSION,
            "environment": APP_ENV,
            "endpoints": [
                "/",
                "/health",
                "/api/v1/info",
                "/api/v1/version",
                "/api/v1/tools"
            ]
        }), 200

    @app.route("/api/v1/version", methods=["GET"])
    def version():
        return jsonify({
            "application": "devops-python-api",
            "version": APP_VERSION
        }), 200

    @app.route("/api/v1/tools", methods=["GET"])
    def tools():
        return jsonify({
            "tools": [
                {"name": "GitHub Actions", "role": "Automação de CI/CD"},
                {"name": "Docker", "role": "Containerização da aplicação"},
                {"name": "Amazon ECR", "role": "Registro seguro de imagens Docker"},
                {"name": "Amazon EC2", "role": "Hospedagem e execução dos contêineres"},
                {"name": "Pytest", "role": "Testes automatizados unitários e de integração"}
            ]
        }), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Recurso não encontrado",
            "status_code": 404
        }), 404

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
