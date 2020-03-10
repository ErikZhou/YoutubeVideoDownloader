from pytube import Playlist
import sys
#YouTube('http://youtube.com/watch?v=9bZkp7q19f0').streams.first().download()
#yt = YouTube('http://youtube.com/watch?v=9bZkp7q19f0')
#print(yt.streams)
#print(yt.streams.filter(subtype='mp4'))
#yt.streams.filter(progressive=True)
#print(yt.streams.filter(progressive=True).order_by('resolution').desc())

def main():
    url = sys.argv[1]
    print(url)
    #path = './videos/1.mp4'
    #YouTube(url).streams.first().download()
    #YouTube(url).streams.first().download(path)

    playlist = Playlist('https://www.youtube.com/playlist?list=PLynhp4cZEpTbRs_PYISQ8v_uwO0_mDg_X')
    print(playlist)
    for video in playlist:
        video = "'" + video + "'"
        print(video)
        yt = Playlist(video)
        yt.streams.get_highest_resolution().download()
    print('Done')

if __name__ == "__main__":
    #usage()    
    main()
