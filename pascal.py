#!/usr/bin/python
# This file is part of RSS Generator Feed.
#
# Copyright(c) 2017 Andrea Draghetti
# https://www.andreadraghetti.it
#
# This file may be licensed under the terms of of the
# GNU General Public License Version 3 (the ``GPL'').
#
# Software distributed under the License is distributed
# on an ``AS IS'' basis, WITHOUT WARRANTY OF ANY KIND, either
# express or implied. See the GPL for the specific language
# governing rights and limitations.
#
# You should have received a copy of the GPL along with this
# program. If not, go to http://www.gnu.org/licenses/gpl.html
# or write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import sys
import pytz
import Config
import datetime
import requests
from bs4 import BeautifulSoup
from podgen import Podcast, Episode, Media

# User Agent MSIE 11.0 (Win 10)
headerdesktop = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; MATBJS; rv:11.0) like Gecko",
                 "Accept-Language": "it"}
timeoutconnection = 120
risorseaudioarray = []

rssfile = Config.outputpath + "pascal.xml"


def genero_feed(puntateList):
    if puntateList:
        # Creo un nuovo podcast
        p = Podcast()

        p.name = "Pascal Rai Radio 2"
        p.description = "Pascal un programma di Matteo Caccia in onda su Radio2 che racconta storie di vita. Episodi grandi o piccoli, stravolgenti o minuti, momenti che hanno modificato per sempre la nostra vita o che, anche se di poco, l'hanno indirizzata. Storie che sono il termometro della temperatura di ognuno di noi e che in parte raccontano chi siamo. "
        p.website = "http://www.raiplayradio.it/programmi/pascal/"
        p.explicit = True
        p.image = "https://rss.draghetti.it/pascal_image.jpg"
        p.feed_url = "https://rss.draghetti.it/pascal.xml"
        p.copyright = "Rai Radio 2"
        p.language = "it-IT"

        for puntata in puntateList:
            episode = Episode()

            episode.title = puntata[0].encode("ascii", "ignore")
            episode.link = puntata[1]

            # La dimensione del file e approssimativa
            episode.media = Media(puntata[3], puntata[4])

            if puntata[2]:
                episode.publication_date = datetime.datetime(int(puntata[2].split("/")[2]),
                                                             int(puntata[2].split("/")[1]),
                                                             int(puntata[2].split("/")[0]), 20,
                                                             00, tzinfo=pytz.utc)
            else:
                episode.publication_date = pytz.utc.localize(datetime.datetime.utcnow())

            p.episodes.append(episode)

        # Print to stdout, just as an example
        p.rss_file(rssfile, minimize=False)


def main():
    # Definisco una lista delle puntate
    puntateList = []

    # Analizzo tutte le puntante pubblicate sul sito per individuarne di nuove
    urlpuntante = "https://www.raiplayradio.it/programmi/pascal/archivio/puntate/"

    response = requests.get(urlpuntante, headers=headerdesktop, timeout=timeoutconnection)
    soup = BeautifulSoup(response.text, "html.parser")

    for div in soup.find_all("div", attrs={"class": "row listaAudio "}):

        if div.get("data-mediapolis"):
            risorsaaudio = div.get("data-mediapolis")

            # Ottengo il titolo e url di riferimento della nuova puntata
            puntataTitolo = div.find("a", href=True).text.strip()
            puntataLink = "https://www.raiplayradio.it%s" % div.find("a", href=True).get("href")

            # Ottengo la data della puntata
            puntataData = div.find("span", attrs={"class": "canale"}).text

            # Ottengo l'URL del MP3
            response = requests.get(risorsaaudio, headers=headerdesktop, timeout=timeoutconnection)
            if response.status_code is 200:
                puntataMp3 = response.url
                puntataSize = response.headers["Content-length"]

                # Appendo alla lista la nuova puntanta
                puntateList.append([puntataTitolo, puntataLink, puntataData, puntataMp3, puntataSize])

    genero_feed(puntateList)


if __name__ == "__main__":
    main()
