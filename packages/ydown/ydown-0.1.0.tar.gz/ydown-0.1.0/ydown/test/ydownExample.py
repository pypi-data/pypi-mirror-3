from ydown import ydownlib
import time

#THIS IS AN EXAMPLE OF THE USE OF ydownlib
#OPEN THE VIDEO
video=ydownlib.yvideo("http://www.youtube.com/watch?v=1T__uN5xmC0")

#DISPLAY THE VIDEO TITLE
print video.getTitle()

#DISPLAY THE FILE VIDEO URL
print video.getUrl()

#START DOWNLOAD IN ANOTHER THREAD
video.download()

#THIS WHILE DISPLAY THE DOWNLOAD STATUS
while(1):
	if video.isStarted(): #START TRACING WHEN THE DOWNLOAD IN STARTED
	
		#DISPLAY THE PERCENT
		print str(video.getPercent()) + "%"
		
		#DISPLAY DOWNLOADED AND TOTAl FILE SIZE
		print str(video.getDownloaded()) + "/" + str(video.getTotalSize())
		
		time.sleep(1) #SLEEP 1 SECOND AFTER EACH REPORT
		#IF THE DOWNLOAD IS FINISHED, QUIT
		if video.getPercent()==100:
			break