import sqlite3
import click
import psycopg2
from flask import current_app, g


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


@click.command("init-db")
def init_db_command():
    # GANTI: db = get_db()
    # DENGAN: conn = get_pg_db_conn()

    conn = get_pg_db_conn() # Gunakan koneksi PostgreSQL
    cur = conn.cursor()

    with current_app.open_resource("schema.sql") as f:
        # Gunakan cursor PostgreSQL untuk menjalankan skema
        cur.execute(f.read().decode("utf-8"))

    conn.commit()
    cur.close()
    conn.close()

    click.echo("You successfully initialized the PostgreSQL database!")

# === SQLite connection (legacy) ===
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db


# === PostgreSQL connection (active) ===
def get_pg_db_conn():
    # Ambil connection string penuh dari konfigurasi aplikasi
    # Kunci 'DATABASE' atau 'FLASK_DATABASE' harusnya sudah diisi dari .env
    db_url = current_app.config.get('DATABASE') 

    # Jika Anda menggunakan FLASK_DATABASE di .env, pastikan Anda juga mencoba kunci itu.
    if not db_url:
         db_url = current_app.config.get('FLASK_DATABASE')

    if not db_url:
        raise RuntimeError("PostgreSQL connection URL not found in Flask config.")

    # Psycopg2 secara otomatis dapat mem-parsing URL penuh ini
    conn = psycopg2.connect(db_url)
    return conn

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()
