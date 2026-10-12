from flask import Blueprint, request, session, jsonify
from database import get_db
import unicodedata, re

chatbot_bp = Blueprint('chatbot', __name__)

def norm(value):
    value = unicodedata.normalize('NFD', str(value or '').lower())
    value = ''.join(ch for ch in value if unicodedata.category(ch) != 'Mn')
    return re.sub(r'\s+', ' ', value.replace('đ', 'd')).strip()

def money(value):
    return f"{int(value or 0):,}".replace(',', '.') + 'đ'

def link(path, label):
    return f'<a href="{path}">{label}</a>'

@chatbot_bp.post('/api/chatbot')
def chatbot_reply():
    payload = request.get_json(silent=True) or {}
    message = str(payload.get('message', '')).strip()[:500]
    if not message:
        return jsonify({'answer': 'Bạn hãy nhập câu hỏi nhé.'})
    q = norm(message)
    conn = get_db()
    try:
        # If the user mentions a movie title, answer from the current database.
        movies = [dict(r) for r in conn.execute('SELECT * FROM movies ORDER BY title').fetchall()]
        mentioned = next((m for m in sorted(movies, key=lambda x: len(norm(x['title'])), reverse=True)
                          if norm(m['title']) in q), None)
        if mentioned and any(k in q for k in ['phim', 'noi dung', 'trailer', 'thoi luong', 'the loai', 'lich chieu', 'suat chieu', 'gio chieu', 'gia ve', 've phim']) or (mentioned and len(q.split()) <= 8):
            m = mentioned
            answer = f"🎬 <b>{m['title']}</b>\n• Trạng thái: {m['status']}\n• Thể loại: {m['genre']}\n• Thời lượng: {m['duration']} phút\n• Nội dung: {m['description'] or 'Chưa có mô tả.'}"
            if m['status'] == 'Sắp chiếu':
                answer += '\nPhim chưa ra rạp nên hiện chưa thể chọn suất chiếu.'
            else:
                sts = conn.execute("SELECT province,cinema,date,time,room,format,price FROM showtimes WHERE movie_id=? ORDER BY date,time LIMIT 5", (m['id'],)).fetchall()
                if sts:
                    answer += '\n📅 Suất chiếu đang được đăng trên hệ thống:'
                    for s in sts:
                        answer += f"\n• {s['date']} {s['time']} — {s['province']}, {s['cinema']}, {s['room']} ({s['format']}) — từ {money(s['price'])}"
                else:
                    answer += '\nHiện chưa có suất chiếu nào được đăng cho phim này.'
            answer += '\n' + link(f"/movie/{m['id']}", 'Xem chi tiết phim')
            if m['status'] != 'Sắp chiếu': answer += ' · ' + link(f"/showtimes?movie_id={m['id']}", 'Xem lịch chiếu')
            return jsonify({'answer': answer})

        if any(k in q for k in ['ve cua toi', 'ma ve', 'ten ve', 've da mua', 've toi', 'don hang cua toi', 'kiem tra ve']):
            if not session.get('user_id'):
                return jsonify({'answer': 'Bạn cần <a href="/login">đăng nhập</a> để mình tra cứu vé của chính tài khoản bạn nhé.'})
            rows = conn.execute('''SELECT t.ticket_code,t.ticket_name,t.seats,t.total,t.status,t.payment_status,
                                  m.title movie_title,s.date,s.time,s.cinema,s.province
                                  FROM tickets t LEFT JOIN movies m ON m.id=t.movie_id
                                  LEFT JOIN showtimes s ON s.id=t.showtime_id
                                  WHERE t.user_id=? ORDER BY t.id DESC LIMIT 5''', (session['user_id'],)).fetchall()
            if not rows:
                return jsonify({'answer': 'Tài khoản của bạn chưa có vé nào. Bạn có thể xem <a href="/showtimes">lịch chiếu</a> để đặt vé.'})
            answer = '🎟 <b>Các vé gần đây của bạn:</b>'
            for t in rows:
                answer += f"\n• <b>{t['ticket_code'] or 'Chưa có mã'}</b> — {t['ticket_name'] or ('Vé xem phim - ' + (t['movie_title'] or 'Phim'))}\n  Phim: {t['movie_title'] or 'Không rõ'} | Ghế: {t['seats']} | {t['date'] or ''} {t['time'] or ''}\n  Rạp: {t['cinema'] or 'Chưa rõ'} | Tổng tiền: {money(t['total'])} | Thanh toán: {t['payment_status']} | Trạng thái: {t['status']}"
            answer += '\nMở ' + link('/tickets', 'Vé của tôi') + ' để xem đầy đủ chi tiết.'
            return jsonify({'answer': answer})

        if any(k in q for k in ['lich chieu', 'suat chieu', 'gio chieu', 'hom nay chieu', 'chieu luc nao']):
            rows = conn.execute('''SELECT m.title,s.province,s.cinema,s.date,s.time,s.room,s.format,s.price,m.status
                                  FROM showtimes s JOIN movies m ON m.id=s.movie_id
                                  WHERE m.status!='Sắp chiếu' ORDER BY s.date,s.time LIMIT 8''').fetchall()
            if not rows:
                answer = 'Hiện chưa có suất chiếu nào được đăng cho các phim có thể đặt vé. Bạn hãy quay lại sau nhé.'
            else:
                answer = '📅 <b>Một số suất chiếu đang được đăng:</b>'
                for r in rows:
                    answer += f"\n• {r['title']} — {r['date']} {r['time']}\n  {r['province']} · {r['cinema']} · {r['room']} ({r['format']}) — từ {money(r['price'])}"
                answer += '\nXem đầy đủ và lọc theo phim/rạp tại ' + link('/showtimes', 'Lịch chiếu') + '.'
            return jsonify({'answer': answer})

        if any(k in q for k in ['rap', 'dia chi', 'co nhung rap', 'rap nao', 'chi nhanh', 'tinh thanh', 'thanh pho']):
            rows = conn.execute("SELECT province,cinema,COUNT(*) n FROM showtimes GROUP BY province,cinema ORDER BY province,cinema").fetchall()
            if rows:
                answer = '🏢 <b>Các rạp có lịch chiếu trên hệ thống:</b>'
                for r in rows[:15]: answer += f"\n• {r['province']} — {r['cinema']} ({r['n']} suất chiếu đã đăng)"
                answer += '\nBạn xem thêm tại ' + link('/cinemas', 'trang Rạp') + '.'
            else: answer = 'Hiện chưa có rạp nào có suất chiếu được đăng. Vui lòng quay lại sau nhé.'
            return jsonify({'answer': answer})

        if any(k in q for k in ['gia ve', 'bao nhieu tien', 'gia ghe', 'gia ghe don', 'gia ghe doi', 'ghe vip', 'vip', 'ghe doi', 'ghe don', 'gia ca']):
            rows = conn.execute("SELECT single_price,double_price,vip_price FROM showtimes ORDER BY id DESC LIMIT 1").fetchone()
            if rows:
                answer = f"💺 Giá ghế theo suất chiếu gần nhất được đăng: ghế đơn {money(rows['single_price'])}, ghế đôi {money(rows['double_price'])}, ghế VIP {money(rows['vip_price'])}. Giá có thể khác giữa các suất/rạp; hãy chọn suất chiếu để xem giá chính xác."
            else: answer = 'Chưa có dữ liệu giá vé. Bạn hãy chọn một suất chiếu để xem giá hiện tại.'
            answer += '\n' + link('/showtimes', 'Xem lịch chiếu')
            return jsonify({'answer': answer})

        if any(k in q for k in ['khuyen mai', 'voucher', 'ma giam', 'giam gia', 'ma uu dai', 'coupon']):
            rows = conn.execute('SELECT code,type,value,label FROM vouchers WHERE active=1 ORDER BY code').fetchall()
            if not rows: answer = 'Hiện chưa có mã khuyến mãi nào đang hoạt động.'
            else:
                answer = '🎁 <b>Mã khuyến mãi đang hoạt động:</b>'
                for r in rows:
                    val = f"{r['value']}%" if r['type']=='percent' else money(r['value'])
                    answer += f"\n• <b>{r['code']}</b> — {r['label']} ({val})"
                answer += '\nNhập mã ở bước đặt vé nếu mã còn hiệu lực.'
            answer += '\n' + link('/promotions', 'Xem khuyến mãi')
            return jsonify({'answer': answer})

        if any(k in q for k in ['combo', 'bap', 'nuoc', 'do an', 'popcorn']):
            rows = conn.execute('SELECT name,description,price FROM combos WHERE active=1 ORDER BY price').fetchall()
            if not rows: answer = 'Hiện chưa có combo nào đang được bán.'
            else:
                answer = '🍿 <b>Combo và đồ ăn đang có:</b>'
                for r in rows: answer += f"\n• {r['name']} — {money(r['price'])}" + (f" ({r['description']})" if r['description'] else '')
                answer += '\nBạn có thể chọn combo trong bước đặt vé.'
            return jsonify({'answer': answer})

        if any(k in q for k in ['thanh toan', 'qr', 'the ngan hang', 'vi dien tu', 'momo', 'zalo pay', 'chuyen khoan']):
            return jsonify({'answer': '💳 Website demo hỗ trợ các phương thức hiển thị ở bước thanh toán như QR, thẻ và ví điện tử. Đây là luồng mô phỏng phục vụ học tập; hãy kiểm tra trạng thái trên trang thanh toán và trong <a href="/tickets">Vé của tôi</a>. Không gửi số thẻ, mật khẩu hoặc OTP vào chatbot nhé.'})

        if any(k in q for k in ['dat ve', 'mua ve', 'cach dat', 'huong dan dat']):
            return jsonify({'answer': '🎟 Cách đặt vé:\n1. Đăng nhập tài khoản.\n2. Vào <a href="/showtimes">Lịch chiếu</a> và chọn phim, rạp, ngày giờ.\n3. Chọn ghế, điền họ tên và số điện thoại đúng định dạng.\n4. Chọn combo/mã giảm giá nếu có, rồi tiếp tục thanh toán.\n5. Sau khi hoàn tất, mở <a href="/tickets">Vé của tôi</a> để xem mã vé và tên vé.'})

        if any(k in q for k in ['phim dang chieu', 'dang chieu', 'phim sap chieu', 'sap chieu', 'suat chieu dac biet', 'phim nao']):
            groups = [('Đang chiếu', 'Đang chiếu'), ('Sắp chiếu', 'Sắp chiếu'), ('Suất chiếu đặc biệt', 'Suất chiếu đặc biệt')]
            answer = '🎬 <b>Danh sách phim hiện có:</b>'
            for label, status in groups:
                items = [m['title'] for m in movies if m['status'] == status]
                if items: answer += f"\n<b>{label}:</b> " + ', '.join(items[:12])
            answer += '\nMở <a href="/">Trang chủ</a> để xem poster và thông tin từng phim.'
            return jsonify({'answer': answer})

        if any(k in q for k in ['xin chao', 'hello', 'chao ban', 'ban la ai', 'giup toi', 'tro giup', 'help']):
            return jsonify({'answer': 'Chào bạn! Mình là trợ lý của Đặt Vé Xem Phim. Mình có thể tra cứu phim, nội dung/trailer, lịch chiếu, rạp, giá ghế, voucher, combo, cách đặt vé và vé của tài khoản bạn. Bạn có thể hỏi ví dụ: “Lịch chiếu Dune: Part Two”, “Giá ghế VIP bao nhiêu?” hoặc “Mã vé của tôi”.'})

        return jsonify({'answer': 'Mình chưa nhận diện chính xác câu hỏi này. Bạn thử hỏi về <b>phim và trailer</b>, <b>lịch chiếu</b>, <b>rạp</b>, <b>giá vé/loại ghế</b>, <b>voucher</b>, <b>combo</b>, <b>thanh toán</b> hoặc <b>vé của tôi</b> nhé.'})
    finally:
        conn.close()
