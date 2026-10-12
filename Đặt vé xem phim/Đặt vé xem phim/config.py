import os
from urllib.parse import quote_plus

DB = os.path.join(os.path.dirname(__file__), 'database.db')
PRICE = 90000
SEATS = [f"{row}{num}" for row in "ABCDEF" for num in range(1, 9)]
SEAT_TYPES = {
    'single': {'label': 'Ghế đơn', 'price': 90000, 'rows': 'ABC'},
    'double': {'label': 'Ghế đôi', 'price': 150000, 'rows': 'DE'},
    'vip': {'label': 'Ghế VIP', 'price': 120000, 'rows': 'F'},
}


def trailer(title, video_id):
    return f'https://www.youtube.com/embed/{video_id}?rel=0'

MOVIE_DATA = [
    ('Dune: Part Two','Khoa học viễn tưởng',166,'https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg','Paul Atreides tiếp tục hành trình giữa sa mạc Arrakis và cuộc chiến bảo vệ gia tộc.','Đang chiếu','Way9Dexny3w'),
    ('The Batman','Hành động',176,'https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg','Batman điều tra một chuỗi bí ẩn và những âm mưu đen tối trong thành phố Gotham.','Đang chiếu','mqqft2x_Aa4'),
    ('Inside Out 2','Hoạt hình',96,'https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg','Riley bước vào tuổi mới lớn với những cảm xúc mới và nhiều thay đổi bất ngờ.','Đang chiếu','LEjhY15eCx0'),
    ('Oppenheimer','Tiểu sử · Chính kịch',180,'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg','Câu chuyện về nhà khoa học và dự án nghiên cứu đã làm thay đổi lịch sử thế giới.','Đang chiếu','bK6ldnjE3Y0'),
    ('Avatar: The Way of Water','Phiêu lưu · Kỳ ảo',192,'https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg','Gia đình Sully trở về với đại dương Pandora trong một hành trình đầy kỳ thú.','Đang chiếu','d9MyW72ELq0'),
    ('Spider-Man: Across the Spider-Verse','Hoạt hình · Hành động',140,'https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg','Miles Morales gặp những Spider-Man khác và đối mặt với một lựa chọn khó khăn.','Đang chiếu','cqGjhVJWtEg'),
    ('Godzilla x Kong: The New Empire','Hành động · Kỳ ảo',115,'https://wikizilla-images.s3.us-east-va.perf.cloud.ovh.us/6/61/GxKTNE_DarkPoster.png','Hai quái vật khổng lồ cùng đối đầu một mối đe dọa mới dưới lòng đất.','Đang chiếu','lV1OOlGwExM'),
    ('Kung Fu Panda 4','Hoạt hình · Hài',94,'https://images.contentstack.io/v3/assets/blt13adb7e2033fcee5/blt1e1cf5d611f2c0b1/692babb5ea1ba383ac47d99d/KungFuPanda4_keyart_desktop_2000x3000.jpg?width=2560','Po chuẩn bị cho một nhiệm vụ mới và gặp gỡ những người bạn đặc biệt.','Đang chiếu','_inKs4eeHiI'),
    ('Deadpool & Wolverine','Hành động · Hài',128,'https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg','Một cuộc gặp đầy bất ngờ đưa Deadpool và Wolverine vào chuyến phiêu lưu xuyên vũ trụ.','Đang chiếu','uJMCNJP2ipI'),
    ('Wicked','Nhạc kịch · Kỳ ảo',160,'https://image.tmdb.org/t/p/w500/n3Z0VF6LhtbgG6mgZnd6wDRdXHN.jpg','Tình bạn và những lựa chọn khác biệt của hai cô gái tại vùng đất Oz.','Đang chiếu','F1dvX9Vs0ns'),
    ('Avatar: Fire and Ash','Khoa học viễn tưởng',190,'https://lumiere-a.akamaihd.net/v1/images/47_coral3_payoff_1sht_uk_ea714d86.jpeg?region=0%2C0%2C743%2C1100','Một chương mới mở ra trên Pandora với những vùng đất và thử thách chưa từng biết.','Sắp chiếu','nb_fFj_0rq8'),
    ('Toy Story 5','Hoạt hình · Gia đình',100,'https://lumiere-a.akamaihd.net/v1/images/g_movies_toystory5_homeentannounce_poster_d124485b.jpeg?region=0%2C0%2C1300%2C730','Những món đồ chơi quen thuộc trở lại trong một cuộc phiêu lưu mới.','Sắp chiếu','c51ND9Hdbw0'),
    ('Moana 2','Hoạt hình · Phiêu lưu',100,'https://image.tmdb.org/t/p/w500/hwmwTFtMbzxAWbIOp1RyyiOCyx0.jpg','Moana lên đường thực hiện một nhiệm vụ mới trên đại dương rộng lớn.','Sắp chiếu','hDZ7y8RP5HE'),
    ('Interstellar','Khoa học viễn tưởng · Chính kịch',169,'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg','Suất chiếu đặc biệt đưa khán giả trở lại hành trình vượt qua không gian và thời gian.','Suất chiếu đặc biệt','zSWdZVtXT7E'),
    ('The Lord of the Rings: The Fellowship of the Ring','Phiêu lưu · Kỳ ảo',178,'https://image.tmdb.org/t/p/w500/tIeluhaXHU5oZivBA5pNx1oW1WS.jpg','Suất chiếu đặc biệt dành cho khán giả yêu thích thế giới Trung Địa.','Suất chiếu đặc biệt','V75dMMIW2B4'),
]
MOVIES = []
for i,(title,genre,duration,poster,description,status,video_id) in enumerate(MOVIE_DATA,1):
    MOVIES.append({'id':i,'title':title,'genre':genre,'duration':duration,'poster':poster,'description':description,'status':status,'trailer':trailer(title, video_id),'trailer_id':video_id})

PROVINCES = ['Hà Nội','Hải Phòng','Đà Nẵng','TP. Hồ Chí Minh']
CINEMAS = {
    'Hà Nội':['Beta Giải Phóng','Beta Mỹ Đình','Beta Thanh Xuân'],
    'Hải Phòng':['Beta Lê Hồng Phong'],
    'Đà Nẵng':['Beta Đà Nẵng'],
    'TP. Hồ Chí Minh':['Beta Quang Trung','Beta Trần Quang Khải'],
}

SHOWTIMES = []
show_id = 1
for province, cinemas in CINEMAS.items():
    for ci, cinema in enumerate(cinemas):
        for offset, movie_id in enumerate([1,2,3,4,5,6,7,8,9,10]):
            SHOWTIMES.append({'id':show_id,'movie_id':movie_id,'province':province,'cinema':cinema,'date':f'2026-10-{1 + (offset % 5):02d}','time':['10:00','13:00','15:30','18:30','20:45'][offset % 5],'room':f'Phòng {ci+1}','format':'2D','price':90000}); show_id += 1
    
# Upcoming and special-event demo screenings
for province, cinemas in CINEMAS.items():
    cinema = cinemas[0]
    for movie_id, time in [(11,'19:00'),(12,'19:30'),(13,'20:00'),(14,'21:00'),(15,'21:15')]:
        SHOWTIMES.append({'id':show_id,'movie_id':movie_id,'province':province,'cinema':cinema,'date':'2026-10-05','time':time,'room':'Phòng 1','format':'2D','price':100000 if movie_id < 14 else 120000}); show_id += 1

VOUCHERS = {
    'MOVIE10': {'type':'percent','value':10,'label':'Giảm 10%'},
    'SAVE20': {'type':'percent','value':20,'label':'Giảm 20%'},
    'GIAM50K': {'type':'fixed','value':50000,'label':'Giảm 50.000đ'},
}
SECRET_KEY = os.getenv('FLASK_SECRET_KEY','dat-ve-xem-phim-demo-secret-2026')

COMBOS = [
    {'id':1,'name':'Combo Solo','description':'1 bắp rang + 1 nước ngọt','price':65000},
    {'id':2,'name':'Combo Couple','description':'1 bắp lớn + 2 nước ngọt','price':115000},
    {'id':3,'name':'Combo Family','description':'2 bắp lớn + 4 nước ngọt','price':190000},
    {'id':4,'name':'Bắp rang caramel','description':'1 hộp bắp rang caramel','price':45000},
    {'id':5,'name':'Nước ngọt','description':'1 ly nước ngọt','price':30000},
    {'id':6,'name':'Combo VIP','description':'1 bắp lớn + 1 nước ngọt','price':75000},
]
