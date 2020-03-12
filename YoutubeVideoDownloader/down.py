from pytube import YouTube
import sys
#YouTube('http://youtube.com/watch?v=9bZkp7q19f0').streams.first().download()
#yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
#print(yt.streams)
#print(yt.streams.filter(subtype='mp4'))
#yt.streams.filter(progressive=True)
#print(yt.streams.filter(progressive=True).order_by('resolution').desc())

#url_list = 'https://www.youtube.com/watch?v=imq0Y9-6lno&list=UUZh0I81cEMmC6MOk4WM8foA'
def main():
    url = sys.argv[1]
    print(url)
    YouTube(url).streams.first().download()
    #path ='./videos/1.mp4'
    
    #YouTube(url).streams.first().download(path)
    #pl = YouTube(url)
    #for video in pl:
    #    video.streams.get_highest_resolution().download()
    #pl.download_all()
    # or if you want to download in a specific directory
    #pl.download_all('./videos/')
    print('Done')


if __name__ == "__main__":
    #usage()    
    main()
