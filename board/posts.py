from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from board.database import get_pg_db_conn

bp = Blueprint("posts", __name__)

@bp.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        # Ambil data form
        author = request.form.get("author") or "Anonymous"
        message = request.form.get("message")

        if message:
            conn = get_pg_db_conn()
            cur = conn.cursor()

            # Gunakan placeholder %s (untuk psycopg2/PostgreSQL)
            cur.execute(
                "INSERT INTO post (author, message) VALUES (%s, %s)",
                (author, message),
            )

            conn.commit()
            cur.close()
            conn.close()

            # Redirect ke halaman daftar posts
            return redirect(url_for("posts.posts"))

    return render_template("posts/create.html")


@bp.route("/posts")
def posts():
    conn = get_pg_db_conn()
    cur = conn.cursor()

    # Ambil semua post, urutkan dari yang terbaru
    cur.execute("SELECT author, message, created FROM post ORDER BY created DESC")
    posts = cur.fetchall()

    cur.close()
    conn.close()

    # Kirim hasil query ke template
    return render_template("posts/posts.html", posts=posts)
