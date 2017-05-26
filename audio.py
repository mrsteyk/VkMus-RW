from pprint import pprint
from getpass import getpass
import requests
from bs4 import BeautifulSoup
import html
class VKError(Exception):
    pass
def audio_get(cookie, query=None, offset=0, no_remixes=False):
    if query:
        params = {
            "q":query,
            "offset":offset,
            "act":"search"
        }
    else:
        params = {}
    r = requests.get("https://m.vk.com/audios0",
                     cookies={"remixsid":cookie},
                     params=params
                     )
    if r.status_code != 200:
        raise VKError("Сервер вконтакте вернул код, которыйй не 200:%s" % r.status_code)
    soup = BeautifulSoup(r.text, 'html5lib')
    tracks = []
    tracks_html = soup.find_all(class_="ai_info")
    i = 1
    for track in tracks_html:
        cover = track.find(class_="ai_play")["style"].split("background-image:url(")
        if len(cover) > 1:
            cover = cover[1].split(")")[0]
        else:
            cover = None
        tracks.append({
            "cover":cover,
            "duration":track.find(class_="ai_dur")["data-dur"],
            "artist":track.find(class_="ai_artist").text,
            "title":track.find(class_="ai_title").text,
            "url":track.input["value"],
            "number":i
        })
        i += 1
    if no_remixes:
        for track in tracks:
            if "remix" in track["title"].lower() or "remix" in track["artist"].lower():
                print("Found remix.")
                tracks.remove(track)
    return tracks

