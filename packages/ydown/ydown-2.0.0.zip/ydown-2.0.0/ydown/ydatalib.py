import urllib
class ydata():
    def __init__(self,url):
        self.page=urllib.urlopen(url).read()
    def getTitle(self):
        titolip=self.page.split("<")
        #FIND THE TITLE OF THE VIDEO
        for ppp in titolip:
            if 'meta name="title" content=' in ppp:
                tit=ppp.split('"')
                title=tit[3]
                return title
    def getFileUrl(self):
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
    def getViews(self):
        pezzi=self.page.split("<span")
        for pezzo in pezzi:
            if 'watch-view-count' in pezzo:
                sp=pezzo.split(">")
                fin=sp[2]
                fin=fin.replace("</strong","")
                return int(fin)
    def getLikes(self):
        pezzi=self.page.split("<span")
        for pezzo in pezzi:
            if 'class="likes"' in pezzo:
                sp=pezzo.split(">")
                fin=sp[1]
                fin=fin.replace("</span","")
                return int(fin)
    def getDislikes(self):
        pezzi=self.page.split("<span")
        for pezzo in pezzi:
            if 'class="dislikes"' in pezzo:
                sp=pezzo.split(">")
                fin=sp[1]
                fin=fin.replace("</span","")
                return int(fin)
    def getAuthor(self):
        pezzi=self.page.split("<a")
        for pezzo in pezzi:
            if 'yt-user-name author' in pezzo:
                sp=pezzo.split(">")
                fin=sp[1]
                fin=fin.replace("</a","")
                return fin
    def getDescription(self):
        pezzi=self.page.split('div')
        for pezzo in pezzi:
            if 'watch-description-text' in pezzo:
                fin=pezzo
                fin=fin.replace('id="watch-description-text">','')
                fin=fin.replace(' <p id="eow-description" >','')
                fin=fin.replace("&quot;",'"')
                return fin
    def getRelated(self):
        pezzi=self.page.split("<a")
        rel=[]
        for pezzo in pezzi:
            if 'related-video yt-uix-contextlink ' in pezzo:
                sp=pezzo.split('"')
                fin=sp[1]
                fin=fin.replace("&amp;","&")
                fin="http://youtube.com"+fin
                rel.append(fin)
        return rel
