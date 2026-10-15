# ScreenMasala

A movie & TV show browser built with a Flask backend, a TMDB-powered API layer and a
plain HTML/CSS/JavaScript frontend. Browse trending titles, explore by genre, search,
view details, and keep a personal watchlist backed by PostgreSQL.

## Features

- Trending, popular movies and popular TV shows
- Browse by genre (movies and TV)
- Live search across movies and TV shows
- Title details with similar-title recommendations
- User accounts (register / login / logout) with hashed passwords
- Personal watchlist stored in PostgreSQL
- Server-side caching + retry for TMDB requests
- Responsive dark UI with lazy-loaded posters

## Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Backend   | Flask, psycopg (PostgreSQL 3.x driver)  |
| Database  | PostgreSQL                              |
| Data      | TMDB API (v3, Bearer token)             |
| Frontend  | Vanilla HTML, CSS, JavaScript (`fetch`) |
| Config    | python-dotenv (`.env`)                  |

## Project Structure

```
Screenmasala/
├── app.py                 # Flask app: static serving + /api/* endpoints
├── requirements.txt
├── .env.example           # Template for required environment variables
├── index.html             # Home
├── movies.html            # Movies (genre browse)
├── tvshows.html           # TV shows (genre browse)
├── search.html            # Search results
├── details.html           # Title details + similar titles
├── watchlist.html         # Saved titles
├── login.html / register.html
├── profile.html           # Account info + logout
├── css/
│   └── style.css
├── js/
│   └── script.js          # All frontend logic
└── assets/
    └── images/
        └── logo.png
```

## Getting Started

### 1. Prerequisites

- Python 3.10+
- PostgreSQL running locally
- A TMDB account with an API read access token

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the environment

```bash
cp .env.example .env
```

Then edit `.env` and set `TMDB_TOKEN`, `FLASK_SECRET_KEY` and your PostgreSQL
credentials.

### 4. Create the database

Create an empty database (the app creates its tables automatically on startup):

```sql
CREATE DATABASE screenmasala;
```

### 5. Run

```bash
python app.py
```

Open http://localhost:5001

## API Endpoints

| Method | Endpoint                       | Purpose                          |
|--------|--------------------------------|----------------------------------|
| GET    | `/api/trending`                | Trending titles of the day       |
| GET    | `/api/movies`                  | Popular movies                   |
| GET    | `/api/tv`                      | Popular TV shows                 |
| GET    | `/api/genres?type=movie\|tv`   | Genre list                       |
| GET    | `/api/genre?type=&genre_id=`   | Titles in a genre                |
| GET    | `/api/search?query=`           | Search movies + TV               |
| GET    | `/api/details?id=&type=`       | Title details                    |
| GET    | `/api/similar?id=&type=`       | Similar titles                   |
| POST   | `/api/register`                | Create an account                |
| POST   | `/api/login`                   | Log in                           |
| GET    | `/api/logout`                  | Log out                          |
| GET    | `/api/user`                    | Current user + session status    |
| GET/POST/DELETE | `/api/watchlist`      | Read / add / remove watchlist    |

## Notes

- `.env` is **not** committed. Use `.env.example` as the template.
- User passwords are hashed with Werkzeug's security helpers before storage.
