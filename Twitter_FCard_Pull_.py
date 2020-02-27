import wget
import os
from TwitterAPI import TwitterAPI
from TwitterAPI import TwitterPager
import sys, fitz

consumer_key = r''
consumer_secret = r''
access_token = r''
access_token_secret = r''

#declare api
api = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret, auth_type='oAuth1')

#declare TwitterPager object
TwitterPager = TwitterPager(api, 'statuses/user_timeline',
                         {'screen_name': 'chrisalbon', 'count': 200, 'trim_user': 'true', 'include_rts': 'false',
                          'tweet_mode': 'extended'})

#for ease of manipulation create list of dictionaries
Tweet_List= []
##TEMP
for item in TwitterPager.get_iterator(wait=5):
    Tweet_List.append(item)

#Extract Tweets with mention of Machine Learning URL
UrlMatrix = []
url_substring = 'https://machinelearningflashcards.com'
def Extract(list_in):
    for item in list_in:
        extract = item['entities'].get('urls')
        if extract and extract[0]['expanded_url'] == url_substring:
            UrlMatrix.append(item)
    return(UrlMatrix)
Extract(Tweet_List)

#Extract Media (Photo) URl from identified tweets and
ML_Urls = []
ML_Topic = []
def Get_Media_Url(list_in):
    for item in list_in:
        extract = item['entities'].get('media')
        if extract and extract[0]['type'] == 'photo':
            #Get Media URL
            ML_Urls.append(extract[0]['media_url'])

            #Extract Title of Associated Topic
            ML_Topic.append(item['full_text'].split(' http')[0].replace(' ', '_'))
    return(ML_Urls, ML_Topic)
Get_Media_Url(UrlMatrix)

#Declare directory to download photos to
Images_Localdir = 'Flashcard_Photos'
os.makedirs(Images_Localdir, exist_ok=True)

#download photos
def Get_Media(list_in1, list_in2):
    for item1, item2 in zip(list_in1, list_in2):
        wget.download(item1, out=f'Flashcard_Photos/{item2}.png')
Get_Media(ML_Urls, ML_Topic)

#Write all images to single PDF file
Images_Local = os.listdir(Images_Localdir)
imgdir = os.path.abspath('Flashcard_Photos')

doc = fitz.open()
for i, f in enumerate(Images_Local):
    img = fitz.open(imgdir + '\\' + f)
    rect = img[0].rect
    pdfbytes = img.convertToPDF()
    img.close()
    imgPDF = fitz.open("pdf", pdfbytes)
    page = doc.newPage(width = rect.width,
                       height = rect.height)
    page.showPDFpage(rect, imgPDF, 0)
doc.save("FlashCards_Agg.pdf")

