=====
YDOWN
=====

ydown is a complete library for getting information about or downloading youtube videos. It can show all the videos information:
For example it shows:
*Author
*Title
*Likes and Dislikes
*Views
*Related Videos
*Description

It also have a good download function that shows you the download status. 

YDOWNLIB
========

ydownlib is the library that download a video. This is an example of the use::

    import time
    from ydown import ydownlib
    
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

YDATALIB
========

ydatalib is the library that show you the video's informations. This is an example of the use::

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

USAGE OF YDOWNLIB
=================

Using ydownlib is very simple:

* FIRST CREATE A yvideo OBJECT

    form ydown import ydownlib
    video=ydownlib.yvideo("YOUTUBE URL")

* NOW YOU CAN USE ALL THE ydownlib FUNCTION

USAGE OF YDATALIB
=================

Using ydatalib is very simple:

* FIRST CREATE A ydata OBJECT

    form ydown import ydatalib
    video=ydatalib.ydata("YOUTUBE URL")

* NOW YOU CAN USE ALL THE ydatalib FUNCTION

FUNCTIONS
=========

YDOWNLIB
--------
This is the complete function list:

``getTitle()`` this function return the name of the yvideo object loaded
``getUrl()`` this function return the file's url of the yvideo object loaded
``download()`` this function start the download in another thread
``isStarted()`` return true if the download is started
``getPercent()`` return the current download percent
``getTotalSize()`` return the total file size of the video in bytes
``getDownloaded()`` return the downloaded part of file in bytes

YDATALIB
--------
This is the complete function list:

``getTitle()`` this function return the name of the ydata object loaded
``getFileUrl()`` this function return the file's url of the ydata object loaded
``getAuthor()`` this function return the video's author
``getLikes()`` this function return the video's likes
``getDislikes()`` this function return the video's dislikes
``getRelates()`` this function return a list with related videos
``getDescription()`` this function return the video's description

Visit the sourceforge page https://sourceforge.net/projects/ydown/