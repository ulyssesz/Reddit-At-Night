from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.api import users

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
import datetime
import reddit
import json

class User(db.Model):
	email = db.StringProperty()
	subreddits = db.StringProperty()
	name = db.StringProperty()
	start = db.TimeProperty()
	end = db.TimeProperty()
	iden = db.StringProperty()

class Link(db.Model):
	url = db.StringProperty()
	subreddit = db.StringProperty()
	title = db.StringProperty()
	start = db.DateTimeProperty()
	end = db.DateTimeProperty()
	ended = db.BooleanProperty()
	
class SendHandler(webapp.RequestHandler):
	def get(self):
		
		users = User.all()
		currTime = datetime.datetime.now() - datetime.timedelta(minutes = 10)
		
		
		#users.filter('end <' currTime)
		for u in users:
			endTime = datetime.datetime(currTime.year, currTime.month, currTime.day, u.end.hour, u.end.minute, u.end.second)
			if currTime - endTime > datetime.timedelta(minutes = 10) or True:
				message = mail.EmailMessage()
				message.sender = "me@redditatnight.appspotmail.com"
				message.to = u.email
				message.body = 'See what you missed at redditatnight.appspot.com/getsub/%d' % (u.key().id())
				message.subject = "Message"
				logging.info("sending to %s" % message.body)
				message.send()
				u.iden = str(u.key().id())
				u.put()

class SubscribeHandler(webapp.RequestHandler):
	def post(self):

		from_addr = self.request.get("email")
		name = self.request.get('name')
		reddits = self.request.get('message')
		start = self.request.get('start')
		end = self.request.get('end')
		
		tz = int(self.request.get('tz'))


		logging.info("sending to %s %s %s %s %d" % (from_addr, reddits, start, end, tz))
		
		def guestbook_key(guestbook_name=None):
			return db.Key.from_path('User', guestbook_name or 'default_user')
		u = User(parent = guestbook_key('12934'))
		u.email = from_addr
		u.subreddits = '|'.join(reddits.split('\n'))
		u.name = name
		h,m = start.split(':')
		u.start = datetime.time((int(h)-tz) % 24, int(m), 0)
		h,m = end.split(':')
		u.end = datetime.time((int(h)-tz) % 24, int(m), 0)
		u.put()

	def get(self):
		logging.info("sdfasfdasfas Hello get")

class ScrapeHandler(webapp.RequestHandler):
	def get(self):
		logging.info('scrape')
		

		data = {}
		
		q = Link.all()
		q.filter('ended =', False)
		
		if q:
			for r in q:
				data[r.url] = r
			
		r = reddit.Reddit(user_agent='my_cool_application')
		
		def guestbook_key(guestbook_name=None):
			return db.Key.from_path('Link', guestbook_name or 'default_user')
		
		new_submissions = set()
		for subreddit in ('technology', 'askreddit', 'gaming', 'funny', 'todayilearned', 'music', 'math'):
			submissions = r.get_subreddit(subreddit, top = 25)
			for x in submissions:
				new_submissions.add(x.url)
				if x.url in data:
					continue
				else:
					l = Link(parent = guestbook_key('12934'))
					l.url = x.url
					l.subreddit = subreddit
					l.title = x.title
					l.start = datetime.datetime.now()
					l.ended = False
					l.put()
		for url in data:
			if url not in new_submissions:
				obj = data[url]
				obj.ended = True
				obj.end = datetime.datetime.now()
				obj.put()
			
class GetSubmissionHandler(webapp.RequestHandler):
	def get(self, key):
		self.response.headers.add_header('Access-Control-Allow-Origin', '*')
		logging.info('get submit')
				
		users = User.all()
		users.filter('iden =', key)
		u = users.get()

		if not u:
			self.response.out.write('No user found')
			return
			
		
		currTime = datetime.datetime.now()
		startTime = u.start
		endTime = u.end
		startTime = datetime.datetime(currTime.year, currTime.month, currTime.day, startTime.hour, startTime.minute, startTime.second)
		endTime = datetime.datetime(currTime.year, currTime.month, currTime.day, endTime.hour, endTime.minute, endTime.second)
		if endTime.hour < startTime.hour:
			# Normal
			startTime -= datetime.timedelta(days = 1)
		logging.info(startTime)
		logging.info(endTime)
		
		q = Link.all()
		q.filter('ended =', True)
		q.filter('start >=', startTime)
		#q.filter('end <',endTime)
		
		data = []
		table_body = ''
		for l in q:
			logging.info(endTime)
			if l.end > endTime: continue
			new_row = ''
			new_row += '<td><a href = "http://www.reddit.com%s" target="_blank">%s</a></td>' % (l.url, l.title)
			new_row += "<td>%s</td>" % l.subreddit
			table_body+= '<tr>%s</tr>' % new_row
	
		with open('indextest.html') as infile:
			t = infile.read()
		t = t.replace('*********', table_body)
		return self.response.out.write(t)
	
	def post(self):
		logging.info('post submit')
		self.response.headers.add_header('Access-Control-Allow-Origin', '*')
		return 
		
		
		

def main():
	application = webapp.WSGIApplication([('/scrape', ScrapeHandler),
										('/send', SendHandler),
										('/getsub/(\d+)', GetSubmissionHandler),
										('/contact_me.py', SubscribeHandler)], debug=True)
	run_wsgi_app(application)


if __name__ == '__main__':
	main()