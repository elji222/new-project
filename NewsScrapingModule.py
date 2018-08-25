import re
import io

from googletrans import Translator
import urllib
import urllib.request
from bs4 import BeautifulSoup

#pip install python-dateutil
import dateutil.parser

# Custom Modules:
from ImageCroppingModule import * 

################################################
############## Scraping Methods: ###############
################################################

# Example Link: http://www.bizportal.co.il/gazandoil/news/article/744262

class NewsScraper:
    def __init__(self, scrapedUrl=None):
        self.translator = Translator()
        self.ScrapeUrl(scrapedUrl)

    def ScrapeUrl(self, scrapedUrl):
        self.url = scrapedUrl
        self.soup = GetLinkContents(self.url) if scrapedUrl is not None else None
        # Original:
        self.title = GetTitle(self.soup)
        self.publicationDetails = GetPublicationDetails(self.soup)
        self.description = GetDescription(self.soup)
        # Translated: 
        self.englishTitle = self.TranslateText(self.title)
        self.englishPublicationDetails = self.TranslateText(self.publicationDetails)
        self.englishDescription = self.TranslateText(self.description)
        # Image:
        self.imageSource = GetThumbnailSource(self.soup)

    def GetScrapedImage(self, size):
        return GetImageFromURL(self.imageSource,size)

    def TranslateText(self, text, target = "en"):
        if not text:
            return None

        translated = self.translator.translate(text, target)
        return translated.text

    def IsScrapeSuccessful(self):
        return self.soup is not None

def GetLinkContents(url):
    if not ValidateURL(url):
        return None
    else:
        try:
            thepage = urllib.request.urlopen(url)
            soup = BeautifulSoup(thepage, "html.parser")
            return soup
        except:
            return None

def ValidateURL(url):
    if not url:
        return False
        
    regex = re.compile(
    r'^(?:http|ftp)s?://' # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def GetPublication(soup):
    if soup is None:
        return None

    publication = soup.find("meta",  property="og:site_name")
    return publication["content"] if publication else None

def GetTitle(soup):
    if soup is None:
        return None
        
    title = soup.find("meta",  property="og:title")
    return title["content"] if title else None

def GetDescription(soup):
    if soup is None:
        return "The provided source is invalid."
        
    description = soup.find("meta", {"name":"description"})
    description = description if description else soup.find("meta",  property="og:description")
    return description["content"] if description else None

def GetPublishDate(soup):
    if soup is None:
        return None
        
    date = soup.find("meta", {"name":"publish-date"})
    date = date if date else soup.find("meta", {"name":"article_created"})
    date = date if date else soup.find("meta", {"name":"iso-8601-publish-date"})
    date = date if date else soup.find("meta", property="article:published_time")
    date = date if date else soup.find(itemprop="datePublished")

    dateRaw = date["content"] if date else None
    #return dateutil.parser.parse(dateRaw).strftime("%Y-%m-%d %H:%M:%S") if dateRaw else ""
    return dateutil.parser.parse(dateRaw).strftime("%Y-%m-%d") if dateRaw else ""

def GetPublicationDetails(soup):
    publication = GetPublication(soup)
    publishDate = GetPublishDate(soup)
    pub = publication if publication else ""
    date = publishDate if publishDate else ""
    return pub + ((" | " if publishDate else "") + date)

def GetThumbnailSource(soup):
    if soup is None:
        return None
        
    image = soup.find("meta", property="og:image")
    return image["content"] if image else None

def GetImageFromURL(imgUrl, size):
    if ValidateURL(imgUrl):
        raw_data = urllib.request.urlopen(imgUrl).read()
        image_file = io.BytesIO(raw_data)
        im = Image.open(image_file)
        #im.thumbnail(size) #The (100, 100) is (height, width)
        return ImageTk.PhotoImage(cropped_thumbnail(im, size))
    else:
        return None
