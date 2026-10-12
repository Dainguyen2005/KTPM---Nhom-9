from flask import Blueprint, render_template, request, session
from helpers import all_movies, all_showtimes, find_movie, active_vouchers
from database import get_db
from config import MOVIES

main_bp = Blueprint('main', __name__)

@main_bp.app_context_processor
def inject_user():
    return {'current_user': session.get('user_name'), 'is_admin': session.get('role') == 'admin', 'poster_defaults': {m['id']: m['poster'] for m in MOVIES}}

@main_bp.route('/')
def index():
    q = request.args.get('q', '').strip()
    genre = request.args.get('genre', '').strip()
    movies = all_movies()
    if q:
        movies = [m for m in movies if q.lower() in m['title'].lower() or q.lower() in m['genre'].lower()]
    if genre:
        movies = [m for m in movies if m['genre'] == genre]
    all_db_movies = all_movies()
    return render_template(
        'index.html', movies=movies,
        genres=sorted({m['genre'] for m in all_db_movies}), q=q, genre=genre,
        now_showing=[m for m in all_db_movies if m['status'] == 'Đang chiếu'],
        upcoming=[m for m in all_db_movies if m['status'] == 'Sắp chiếu'],
        special=[m for m in all_db_movies if m['status'] == 'Suất chiếu đặc biệt'],
        vouchers=active_vouchers(),
    )

@main_bp.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie = find_movie(movie_id)
    if not movie:
        return 'Không tìm thấy phim', 404
    return render_template('movie.html', movie=movie, showtimes=all_showtimes(movie_id=movie_id))

@main_bp.route('/showtimes')
def showtimes():
    movie_id = request.args.get('movie_id', type=int)
    date = request.args.get('date', '')
    cinema = request.args.get('cinema', '')
    province = request.args.get('province', '')
    data = all_showtimes(movie_id, date or None, cinema or None, province or None)
    conn = get_db()
    provinces = [r[0] for r in conn.execute("SELECT DISTINCT province FROM showtimes WHERE province!='' ORDER BY province")]
    cinemas = [r[0] for r in conn.execute('SELECT DISTINCT cinema FROM showtimes ORDER BY cinema')]
    dates = [r[0] for r in conn.execute('SELECT DISTINCT date FROM showtimes ORDER BY date')]
    conn.close()
    return render_template('showtimes.html', showtimes=data, movies=all_movies(), cinemas=cinemas, dates=dates,
                           provinces=provinces, movie_id=movie_id, date=date, cinema=cinema, province=province)

@main_bp.route('/cinemas')
def cinemas():
    conn = get_db()
    rows = conn.execute('SELECT province,cinema,COUNT(*) showtime_count FROM showtimes GROUP BY province,cinema ORDER BY province,cinema').fetchall()
    conn.close()
    return render_template('cinemas.html', cinemas=rows)

@main_bp.route('/promotions')
def promotions():
    return render_template('promotions.html', vouchers=active_vouchers())
