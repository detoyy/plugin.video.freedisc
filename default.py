__scriptname__ = "Freedisc.pl"
__author__ = "detoyy"
__url__ = ""
__scriptid__ = "plugin.video.freedisc"
__credits__ = "Pillager"
__version__ = "1.1.1"

import urllib,urllib2,re
import xbmc,xbmcplugin,xbmcgui,sys
import cookielib
import xbmcaddon,os
import requests
import json

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

addon = xbmcaddon.Addon('plugin.video.freedisc')
home = addon.getAddonInfo('path')
search_icon = xbmc.translatePath(os.path.join(home, 'icons', 'search.png'))




def _get_keyboard(default="", heading="", hidden=False):
        """ shows a keyboard and returns a value """
        keyboard = xbmc.Keyboard(default, heading, hidden)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
                return unicode(keyboard.getText(), "utf-8")
        return default


def CATEGORIES():
        INDEX2('http://freedisc.pl/start')


def INDEX(url,query,page):
        addDir('Search','blabla',3,search_icon,'','')

        link = getHtml_2(query,page)
        #print link

        parsed_json = json.loads(link)
        hits = parsed_json['response']['data_files']['hits']
        if hits > 25 :
                hits = 25
                #page = page + 1
        #print hits
        tablica = {}
        katalogi = {}
        users = {}
        for i in range(hits):
                name = parsed_json['response']['data_files']['data'][i]['name_url']
                f_id = parsed_json['response']['data_files']['data'][i]['id']
                user_id = parsed_json['response']['data_files']['data'][i]['user_id']
                #print user_id
                nick_usera = parsed_json['response']['logins_translated'][str(user_id)]['url']
                root_dir_id = parsed_json['response']['logins_translated'][str(user_id)]['userRootDirID']
                #print nick_usera
                url = 'http://freedisc.pl/'+nick_usera+',f-'+f_id+','+name
                #print url
                thumb = 'http://img.freedisc.pl/photo/'+f_id+'/7/2/'+name+'.png'
                #print thumb
                id_katalogu_nadrzednego = parsed_json['response']['data_files']['data'][i]['parent_id']
                nazwa_katalogu = parsed_json['response']['directories_translated'][str(id_katalogu_nadrzednego)]['name_url']
                directory_url = 'http://freedisc.pl/'+nick_usera+',d-'+id_katalogu_nadrzednego+','+nazwa_katalogu
                #print directory_url
                users[nick_usera]=('http://freedisc.pl/'+nick_usera)#+',d-'+root_dir_id+','+nick_usera)
                katalogi[nazwa_katalogu]=(directory_url,nick_usera)
                #sortowanie wg key ( name)
                tablica[name] = (url,thumb,f_id) # dictionary of tuples tablica[key] = (value1,value2,value3) tablica[key](tuple)
                #addDownLink(name , url,5, thumb,f_id)
        for key in sorted(tablica):
                #print "tablica = %s: %s" % (key, tablica[key])
                addDownLink(key , tablica[key][0],4, tablica[key][1],tablica[key][2])  # posortowane linki
                #addDir(nazwa_katalogu,directory_url,1,'','','')
        for key in katalogi:
                addDir('Folder : '+key + ' ( user:'+katalogi[key][1] + ' )' ,katalogi[key][0],4,'','','')
                #print "katalogi = %s: %s" % (key, katalogi[key])
        for key in sorted(users):
                addDir('Katalog domowy : '+key,users[key],4,'','','')
                print users[key]
        current_page = parsed_json['response']['page']
        next_page_nr = current_page + 1
        #print str(next_page_nr) + " nrnr"
        addDir('Next Page','blabla',1,'',next_page_nr,query)

def INDEX3(url):
        addDir('Search','blabla',3,search_icon,'','')

        link = getHtml(url)
        print link
                              
        matchurl = re.compile('class=\'name text-ellipsis\'><a href="/(.+?)" title="').findall(link)
        matchthumb = re.compile('class=\'img_fs\' width="69" height="49" src="(.+?)" alt="').findall(link)

        for url,thumb in zip( matchurl, matchthumb):
                x,y,name = url.split(',')
                uzytkownik,fileid,filename = url.split(',')
                fileid = fileid.replace('f-','')
                url='http://freedisc.pl/' + url +'?ref=deman'
                thumb = thumb.replace("/18/2/", "/7/2/")
                addDownLink(name , url,4, thumb,fileid)
                #addDir(name,url,2,thumb)
        matchdir = re.compile('<div class="CssTreeValue"><a href="/(.+?)" title="(.+?)" >').findall(link)
        for folderurl,title in  matchdir:
                folderurl='http://freedisc.pl/' + folderurl
                title = title
                addDir('Folder : '+title,folderurl,4,'','','')
                             


def INDEX2(url):
        addDir('Search','blabla',3,'','','')


def SEARCHVIDEOS(url):
        searchUrl = 'http://freedisc.pl/search/get'
        vq = _get_keyboard(heading="Enter the query")
        # if blank or the user cancelled the keyboard, return
        if (not vq): return False, 0
        # we need to set the title to our query
        title = urllib.quote_plus(vq)
        #searchUrl += title
        #print "Searching URL: " + searchUrl
        INDEX(searchUrl,title,'0')


def getHtml_2(query,page):
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'http://freedisc.pl',
        'Accept-Encoding':'gzip, deflate',
        'Accept': 'application/json, text/javascript, */*; q=0.01'
        }

        url = "http://freedisc.pl/search/get"
        postdata = {
        "search_phrase":query,
        "search_page": page,
        "search_type":"movies",
        "search_saved":0,
        "pages":0,
        "limit":0
        }
        content = requests.post(url, json=postdata, headers=headers)
        return content.text

def getHtml(url):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        # Add our headers
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
        
        urllib2.install_opener(opener)

        #data = ''  # nic bo nic nie ma do wyslania narazie

        # Build our Request object (dodanie do url ",data" makes it a POST)
        req = urllib2.Request(url)
      
        # Make the request and read the response
        resp = urllib2.urlopen(req)
        data = resp.read()
        resp.close()
        return data


def getParams():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?','')
                if (params[len(params)-1] == '/'):
                        params = params[0:len(params)-2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]

        return param


def addDownLink(name,url,mode,iconimage,fileid):
        #print 'adddownloadlink '+url
        #print name
        #print iconimage + ' thumb'
        #print fileid
        u = 'http://stream.freedisc.pl/video/' + fileid + '/' + name
        print u + ' url filmu'
        #getHtml(referer)
        #urlzrefem = u + '|referer='+referer
        #print urlzrefem
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png",
                               thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                         url=u + '|referer=http://freedisc.pl/static/player/v612/jwplayer.flash.swf', listitem=liz, isFolder=False)
        return ok


def addDir(name,url,mode,iconimage,page,query):
        u = (sys.argv[0] +
             "?url=" + urllib.quote_plus(url) +
             "&mode=" + str(mode) +
             "&name=" + urllib.quote_plus(name)+
             "&page=" + str(page) +
             "&query=" + urllib.quote_plus(query))
            
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png",
                               thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={ "Title": name })
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                         url=u, listitem=liz, isFolder=True)
        return ok


params = getParams()
url = None
name = None
mode = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass
try:                          
        page=int(params["page"])   # we use int here because we want a number instead of a string
except:
        pass
try:                          
        query=urllib.unquote_plus(params["query"])
except:
        pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url)<1:
        print ""
        CATEGORIES()

elif mode == 1:
        print "" + url
        INDEX(url,query,page)

elif mode == 3:
        print mode
        SEARCHVIDEOS(url)
elif mode == 2:
        print mode
        INDEX2(url)
elif mode == 4:
        print mode
        INDEX3(url)


xbmcplugin.endOfDirectory(int(sys.argv[1]))
