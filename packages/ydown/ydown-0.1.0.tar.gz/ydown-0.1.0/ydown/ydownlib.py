import urllib
import threading
class yvideo:
	def __init__(self,url):
		self.page=""
		web = urllib.urlopen(url)
		self.page = web.read()
	def getTitle(self):
		titolip=self.page.split("<")
		#FIND THE TITLE OF THE VIDEO
		for ppp in titolip:
			if 'meta name="title" content=' in ppp:
				tit=ppp.split('"')
				title=tit[3]
                return title
	def getUrl(self):
		pezzi = self.page.split("script>")
		#YOUTUBE PAGE ANALIZING
		for pezzo in pezzi:
			if ('x-shockwave-flash' in pezzo) and ('movie_player' in pezzo):
				subpezzi=pezzo.split('"')
				varss=subpezzi[12].split(";")
				for var in varss:
					if 'url_encoded' in var:
						#REPLACE THE URL ENCODING
						finurl=var.replace("%252F","/")
						finurl=finurl.replace("%253D","=")
						finurl=finurl.replace("%2526","&")
						finurl=finurl.replace("%26","&")
						finurl=finurl.replace("%3D","=")
						finurl=finurl.replace("%253F","?")
						finurl=finurl.replace("%253A",":")
						finurl=finurl.replace("%25252C",",")
						finurl=finurl.replace("&quality","&&quality")
						finurl=finurl.replace("&fallback_host","&&fallback_host")
						pp = finurl.split("&type")
						spp = pp[0].replace("url_encoded_fmt_stream_map=url=","")
						finalurl = spp
						return finalurl
	def download(self):
		self.down=downloader()
		self.down.finalurl=self.getUrl()
		self.down.name=self.getTitle()+".mp4"
		self.down.start()
	def getPercent(self):
		return self.down.percent
	def getDownloaded(self):
		return self.down.downloaded
	def getTotalSize(self):
		return self.down.totalSize
	def isStarted(self):
		if self.down.downloading==True:
			return True
		else:
			return False
class downloader(threading.Thread):
	finalurl=""
	name=""
	downloading=False
	def run(self):
		urllib.urlretrieve(self.finalurl, self.name, reporthook=self.dlProgress)
	def dlProgress(self,count, blockSize, totalSiz):
		self.downloading=True
		self.percent = int(count*blockSize*100/totalSiz)
		self.downloaded=count*blockSize
		self.totalSize=totalSiz