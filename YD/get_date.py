import requests
from bs4 import BeautifulSoup as bs # importing BeautifulSoup
from dateutil import parser
import sys, traceback

# sample youtube video url
#video_url = "https://www.youtube.com/watch?v=IuDEvWjHTXo"

def get_date(url):
    dt = parser.parse("Jan 1 2000 12:00AM") 
    #print(url)
    try:
    # download HTML code
        content = requests.get(url)
    # create beautiful soup object to parse HTML
        soup = bs(content.content, "html.parser")
        #print(soup)
        # write all HTML code into a file
        open("video.html", "w", encoding='utf8').write(content.text)
    # initialize the result
        result = {}
        pub = result['date_published'] = soup.find("strong", attrs={"class": "watch-time-text"})
        if pub is None:
            print('pub is None')
            return dt

        result['date_published'] = soup.find("strong", attrs={"class": "watch-time-text"}).text
        date_str = result['date_published']
        #print(date_str)
        date_str = parser.parse(date_str[13:]) 
        dt = parser.parse(str(date_str)) 
    except Exception:
        print("An exception occurred")
        traceback.print_exc(file=sys.stdout)
    return dt

def main():
    url = sys.argv[1]
    dt = get_date(url) 
    print(dt)


if __name__ == "__main__":
    main()
