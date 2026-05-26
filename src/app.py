from flask import Flask, request, jsonify, current_app
import sqlite3
import os
import time
import logging
from pythonjsonlogger import jsonlogger
from prometheus_client import CollectorRegistry, Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

app = Flask(__name__)
app.config["DB_PATH"] = os.environ.get("DB_PATH", "tasks.db")

METRICS_REGISTRY = CollectorRegistry()
REQUEST_COUNT = Counter(
    "todo_api_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
    registry=METRICS_REGISTRY,
)
REQUEST_LATENCY = Histogram(
    "todo_api_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
    registry=METRICS_REGISTRY,
)


def configure_logging():
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(logging.INFO)

    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)


configure_logging()


def get_db():
    conn = sqlite3.connect(current_app.config["DB_PATH"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with app.app_context():
        conn = get_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        app.logger.info(
            "database_initialized",
            extra={"event": "database_initialized", "db_path": app.config["DB_PATH"]},
        )


init_db()


@app.before_request
def before_request():
    request.start_time = time.time()
    app.logger.info(
        "request_started",
        extra={
            "event": "request_started",
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
        },
    )


@app.after_request
def after_request(response):
    duration = time.time() - getattr(request, "start_time", time.time())
    endpoint = request.endpoint or request.path
    REQUEST_LATENCY.labels(request.method, endpoint).observe(duration)
    REQUEST_COUNT.labels(request.method, endpoint, response.status_code).inc()
    app.logger.info(
        "request_completed",
        extra={
            "event": "request_completed",
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        },
    )
    return response


@app.route("/", methods=["GET"])
def index():
    return jsonify(
        {
            "name": "To-Do API",
            "version": "1.0.0",
            "endpoints": ["/tasks", "/health", "/metrics"],
        }
    )


@app.route("/health", methods=["GET"])
def health():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        return jsonify({"status": "ok"}), 200
    except sqlite3.Error as exc:
        app.logger.error(
            "health_check_failed",
            extra={"event": "health_check_failed", "error": str(exc)},
        )
        return jsonify({"status": "unhealthy", "error": str(exc)}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(METRICS_REGISTRY), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/tasks", methods=["GET"])
def list_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(t) for t in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    
    # Validate request data
    if not data or "title" not in data:
        app.logger.warning(
            "create_task_missing_title",
            extra={"event": "validation_error", "reason": "missing_title"},
        )
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400
    
    title = data["title"].strip() if isinstance(data["title"], str) else None
    description = data.get("description", "").strip() if isinstance(data.get("description"), str) else ""
    
    # Validate title constraints
    if not title or len(title) < 1:
        return jsonify({"error": "El campo 'title' no puede estar vacío"}), 400
    
    if len(title) > 255:
        return jsonify({"error": "El campo 'title' no puede exceder 255 caracteres"}), 400
    
    if len(description) > 1000:
        return jsonify({"error": "El campo 'description' no puede exceder 1000 caracteres"}), 400

    try:
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description),
        )
        task_id = cursor.lastrowid
        conn.commit()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        
        app.logger.info(
            "task_created",
            extra={"event": "task_created", "task_id": task_id},
        )
        return jsonify(dict(task)), 201
    except sqlite3.Error as exc:
        app.logger.error(
            "create_task_failed",
            extra={"event": "database_error", "error": str(exc)},
        )
        return jsonify({"error": "Error al crear la tarea"}), 500


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos"}), 400

    try:
        conn = get_db()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if task is None:
            conn.close()
            app.logger.warning(
                "update_task_not_found",
                extra={"event": "not_found", "task_id": task_id},
            )
            return jsonify({"error": "Tarea no encontrada"}), 404

        # Get and validate fields
        title = data.get("title", task["title"])
        description = data.get("description", task["description"])
        completed = data.get("completed", task["completed"])
        
        # Validate constraints
        if isinstance(title, str):
            title = title.strip()
            if not title or len(title) > 255:
                return jsonify({"error": "El campo 'title' debe tener entre 1 y 255 caracteres"}), 400
        
        if isinstance(description, str) and len(description) > 1000:
            return jsonify({"error": "El campo 'description' no puede exceder 1000 caracteres"}), 400

        conn.execute(
            "UPDATE tasks SET title=?, description=?, completed=? WHERE id=?",
            (title, description, completed, task_id),
        )
        conn.commit()
        task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        
        app.logger.info(
            "task_updated",
            extra={"event": "task_updated", "task_id": task_id},
        )
        return jsonify(dict(task))
    except sqlite3.Error as exc:
        app.logger.error(
            "update_task_failed",
            extra={"event": "database_error", "task_id": task_id, "error": str(exc)},
        )
        return jsonify({"error": "Error al actualizar la tarea"}), 500


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Tarea no encontrada"}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Tarea eliminada"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
