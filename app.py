from flask import Flask, send_from_directory, jsonify, request, session
from werkzeug.exceptions import NotFound
import requests
import os
import time
import threading
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")

TMDB_TOKEN = os.getenv("TMDB_TOKEN")

headers = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}


TMDB_CACHE_TTL = 600
_tmdb_cache = {}
_cache_lock = threading.Lock()


def tmdb_request(endpoint):
    now = time.time()

    with _cache_lock:
        cached = _tmdb_cache.get(endpoint)

    if cached and now - cached["time"] < TMDB_CACHE_TTL:
        return cached["data"]

    url = "https://api.themoviedb.org/3/" + endpoint

    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            with _cache_lock:
                _tmdb_cache[endpoint] = {"data": data, "time": time.time()}

            return data

        except requests.RequestException:
            if attempt < 2:
                time.sleep(0.6 * (attempt + 1))

    with _cache_lock:
        cached = _tmdb_cache.get(endpoint)

    if cached:
        return cached["data"]

    return {"error": "Unable to retrieve data from TMDB."}


def warm_cache():
    for endpoint in (
        "trending/all/day",
        "movie/popular",
        "tv/popular",
        "genre/movie/list",
        "genre/tv/list",
    ):
        tmdb_request(endpoint)


def get_db():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5433"),
        dbname=os.getenv("DB_NAME", "screenmasala"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD"),
        row_factory=dict_row
    )


def create_database():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
        """)

        db.execute("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id)
                    ON DELETE CASCADE,
                tmdb_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                poster TEXT,
                media_type TEXT NOT NULL DEFAULT 'movie',
                UNIQUE (user_id, tmdb_id, media_type)
            )
        """)


create_database()

threading.Thread(target=warm_cache, daemon=True).start()


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


ALLOWED_EXTENSIONS = {
    ".html", ".css", ".js",
    ".png", ".jpg", ".jpeg", ".webp", ".svg", ".ico", ".gif"
}


@app.route("/<path:filename>")
def files(filename):
    extension = os.path.splitext(filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise NotFound()

    return send_from_directory(".", filename)


@app.route("/api/trending")
def trending():
    return jsonify(tmdb_request("trending/all/day"))


@app.route("/api/movies")
def movies():
    return jsonify(tmdb_request("movie/popular"))


@app.route("/api/tv")
def tv():
    return jsonify(tmdb_request("tv/popular"))


@app.route("/api/genres")
def genres():
    item_type = request.args.get("type", "movie")
    if item_type not in ("movie", "tv"):
        return jsonify({"error": "Type must be movie or tv."}), 400
    return jsonify(tmdb_request(f"genre/{item_type}/list"))


@app.route("/api/genre")
def genre_titles():
    item_type = request.args.get("type", "movie")
    genre_id = request.args.get("genre_id", "")
    page = request.args.get("page", "1")

    if item_type not in ("movie", "tv"):
        return jsonify({"error": "Type must be movie or tv."}), 400
    if not genre_id.isdigit():
        return jsonify({"error": "A valid genre ID is required."}), 400
    if not page.isdigit() or int(page) < 1:
        return jsonify({"error": "A valid page is required."}), 400

    endpoint = f"discover/{item_type}?with_genres={genre_id}&page={page}&sort_by=popularity.desc"
    return jsonify(tmdb_request(endpoint))


@app.route("/api/search")
def search():
    query = request.args.get("query", "").strip()

    if not query:
        return jsonify({"results": []})

    return jsonify(
        tmdb_request(
            "search/multi?query=" + requests.utils.quote(query)
        )
    )


@app.route("/api/details")
def details():
    item_id = request.args.get("id")
    item_type = request.args.get("type", "movie")

    if not item_id or item_type not in ("movie", "tv"):
        return jsonify({"error": "Invalid movie or TV show ID/type."}), 400

    if not item_id.isdigit():
        return jsonify({"error": "Invalid ID."}), 400

    return jsonify(tmdb_request(f"{item_type}/{item_id}"))


@app.route("/api/similar")
def similar():
    item_id = request.args.get("id")
    item_type = request.args.get("type", "movie")

    if not item_id or not item_id.isdigit():
        return jsonify({"error": "A valid ID is required."}), 400

    if item_type not in ("movie", "tv"):
        return jsonify({"error": "Type must be movie or tv."}), 400

    result = tmdb_request(
        f"{item_type}/{item_id}/similar"
    )

    return jsonify(result)


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Please fill all fields."
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must be at least 8 characters."
        }), 400

    try:
        with get_db() as db:
            db.execute(
                """
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password, method="pbkdf2:sha256")
                )
            )

        return jsonify({
            "success": True,
            "message": "Account created successfully."
        })

    except psycopg.errors.UniqueViolation:
        return jsonify({
            "success": False,
            "message": "Email already registered."
        }), 409


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    with get_db() as db:
        user = db.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        ).fetchone()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    session.clear()
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]

    return jsonify({
        "success": True,
        "name": user["name"]
    })


@app.route("/api/logout")
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/user")
def user():
    if "user_id" not in session:
        return jsonify({"logged_in": False})

    with get_db() as db:
        account = db.execute(
            "SELECT name, email, created_at FROM users WHERE id = %s",
            (session["user_id"],)
        ).fetchone()

    if not account:
        session.clear()
        return jsonify({"logged_in": False})

    return jsonify({
        "logged_in": True,
        "name": account["name"],
        "email": account["email"],
        "member_since": (
            account["created_at"].strftime("%Y")
            if account["created_at"] else "N/A"
        )
    })


@app.route("/api/watchlist", methods=["GET", "POST", "DELETE"])
def watchlist():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    user_id = session["user_id"]

    if request.method == "GET":
        with get_db() as db:
            items = db.execute(
                "SELECT * FROM watchlist WHERE user_id = %s ORDER BY id DESC",
                (user_id,)
            ).fetchall()

        return jsonify(items)

    data = request.get_json(silent=True) or {}

    if request.method == "POST":
        try:
            tmdb_id = int(data.get("tmdb_id"))
        except (TypeError, ValueError):
            return jsonify({
                "success": False,
                "message": "A valid movie ID is required."
            }), 400

        title = data.get("title", "").strip()
        poster = data.get("poster", "")
        media_type = data.get("media_type", "movie")

        if not title or media_type not in ("movie", "tv"):
            return jsonify({
                "success": False,
                "message": "Invalid title or media type."
            }), 400

        with get_db() as db:
            existing = db.execute(
                """
                SELECT id FROM watchlist
                WHERE user_id = %s AND tmdb_id = %s AND media_type = %s
                """,
                (user_id, tmdb_id, media_type)
            ).fetchone()

            if existing:
                return jsonify({
                    "success": False,
                    "message": "Already in watchlist."
                }), 409

            db.execute(
                """
                INSERT INTO watchlist
                (user_id, tmdb_id, title, poster, media_type)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, tmdb_id, title, poster, media_type)
            )

        return jsonify({"success": True})

    try:
        item_id = int(data.get("id"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "A valid watchlist item ID is required."
        }), 400

    with get_db() as db:
        db.execute(
            "DELETE FROM watchlist WHERE id = %s AND user_id = %s",
            (item_id, user_id)
        )

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
    