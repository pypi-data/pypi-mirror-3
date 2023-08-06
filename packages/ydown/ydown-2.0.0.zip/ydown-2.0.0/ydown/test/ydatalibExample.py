from ydown import ydatalib

#OPEN YOUTUBE VIDEO
video=ydatalib.ydata("http://www.youtube.com/watch?v=1T__uN5xmC0")

#GET VIDEO INFORMATION
print "TITLE"
print video.getTitle()
print "VIEWS"
print video.getViews()
print "LIKES"
print video.getLikes()
print "DISLIKES"
print video.getDislikes()
print "DESCRIPTION"
print video.getDescription()
print "LIST OF RELATED VIDEO URL"
print video.getRelated()
