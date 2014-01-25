import urllib2
import json

class LinkObject(object):
	def __init__(self, url, title, subreddit):
		self.url = url
		self.title = title
		self.subreddit = subreddit

class Reddit(object):
	def __init__(self, user_agent):
		self.user_agent = user_agent
	
	def get_subreddit(self, subreddit, top = 1):
		headers = {'User-Agent' : self.user_agent}
		req = urllib2.Request('http://www.reddit.com/r/%s/hot.json?limit=%d' % (subreddit, top), None, headers)
		response = urllib2.urlopen(req)
		data = json.loads(response.read(), "ISO-8859-1")
		objects = []

		for i in data['data']['children']:
			info = i['data']
			objects.append(LinkObject(info['permalink'], info['title'], info['subreddit']))
		return objects


def main():
	r = Reddit('hello')
	for i in ('technology', 'askreddit', 'iama'):
		print r.get_subreddit(i, 20)


if __name__ == '__main__':
	main()