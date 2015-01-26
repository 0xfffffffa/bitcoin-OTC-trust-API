import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from json import loads, dumps, JSONEncoder, JSONDecoder
from MySQLdb import escape_string
import collections
import sys,os
import sqlite3


define("port", default=8000, help="run on the given port", type=int)


class OTC:
	def getLevel2Ratings(self,sourcenick, destnick):
		db = liteDB()
		cursor = db.connect()
		sourcenick = sourcenick.replace('|','||').replace('_','|_').replace('%','|%')
		destnick = destnick.replace('|','||').replace('_','|_').replace('%','|%')
		cursor.execute("""SELECT ratings1.rating, ratings2.rating
                    FROM users as users1, users as users2, ratings as ratings1, ratings as ratings2 WHERE
                    users1.nick LIKE ? ESCAPE '|' AND
                    ratings1.rater_user_id = users1.id AND
                    users2.nick LIKE ? ESCAPE '|' AND
                    ratings2.rated_user_id = users2.id AND
                    ratings2.rater_user_id = ratings1.rated_user_id""", (sourcenick,destnick,))
		l2ratings = cursor.fetchall()
		if len(l2ratings) == 0:
			return (0,0,)
		trustlinks = []
		for row in l2ratings:
			if row[0] > 0 and row[1] > 0:
				trustlinks.append(min(row))
			elif row[0] > 0 and row[1] < 0:
				trustlinks.append(-min(row[0],abs(row[1])))
			elif row[0] < 0:
				trustlinks.append(0)
		return (sum(trustlinks), len(trustlinks),)

	def _gettrust(self,sourcenick, destnick):
 	 	"""Get a list of tuples for l1,l2... trust levels and number of associated
 	 	connections. To be used from other plugins for trust checks.
 		 """
 	 	result = []
 	 	l1 = self.getRatingDetail(sourcenick, destnick)
 	 	if len(l1) > 0:
 	 		result.append((l1[0][1], 1,))
 	 	else:
 	 		result.append((0, 0,))
 	 	l2 = self.getLevel2Ratings(sourcenick, destnick)
 	 	if l2[0] is None:
 	 		result.append((0,0,))
 	 	else:
 	 		result.append(l2)
 	 	return result
 
	def getRatingDetail(self,sourcenick, targetnick):
		db = liteDB()
		cursor = db.connect()
		sourcenick = sourcenick.replace('|','||').replace('_','|_').replace('%','|%')
		targetnick = targetnick.replace('|','||').replace('_','|_').replace('%','|%')
		cursor.execute("""SELECT ratings.created_at, ratings.rating, ratings.notes
                          FROM ratings, users, users as users2 WHERE
                          users.nick LIKE ? ESCAPE '|' AND
                          users2.nick LIKE ? ESCAPE '|' AND
                          ratings.rater_user_id = users.id AND
                          ratings.rated_user_id = users2.id""",
                       (sourcenick, targetnick))
		return cursor.fetchall()

class liteDB:
	def __init__(self):
		self.filename = "./RatingSystem.db"
		self.db = None
		self.connect()
				
	def commit(self):
		for i in xrange(10):
			try:
				self.db.commit()
			except:
				time.sleep(1)

	def close(self):
		self.db.close()
	
	def connect(self):
		if os.path.exists(self.filename):
			db = sqlite3.connect(self.filename, check_same_thread = False)
			return db.cursor()

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Nothing here')

class get_trust(tornado.web.RequestHandler):
    def post(self):
		from_nick = escape_string(self.get_argument('from_nick'))
		to_nick = escape_string(self.get_argument('to_nick'))
		otc = OTC()
		trust = otc._gettrust(from_nick,to_nick)

		objects_list = []
		d = collections.OrderedDict()
		d['result'] = "success"
		d['from_nick'] = from_nick
		d['to_nick'] = to_nick
		d['L1'] = trust[0][0]
		d['L2'] = trust[1][0]
		d['connections'] = trust[1][1]
		objects_list.append(d)
		j = dumps(objects_list)
		print "%s" % j
		self.write("%s" % (j))


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler),(r"/gettrust",get_trust)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



