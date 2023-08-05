#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# $Id: elatom.py 439 2011-07-13 12:03:05Z maury $
#
# Author : Olivier Maury
# Creation Date : 2009-04-24 12:49:49CEST
# Last Revision : $Date: 2011-07-13 14:03:05 +0200 (mer. 13 juil. 2011) $
# Revision : $Rev: 439 $
#
# tested on WinXP with Python 3.2.1

__revision__ = "$Rev: 439 $"
__author__ = "Olivier Maury"

import collections
import gettext
import configparser
import locale
from optparse import OptionGroup, OptionParser
import os
import platform
import re
import random
import sys
import time
import threading
try:
    import tkinter
    from tkinter.scrolledtext import ScrolledText
    import tkinter.filedialog as tkFileDialog
    import tkinter.simpledialog as tkSimpleDialog
    import tkinter.messagebox as tkMessageBox
    tkinter_available = True
except ImportError:
    tkinter_available = False
    class tkSimpleDialog:
        class Dialog:
            pass

    class tkinter:
        class Frame:
            pass

import urllib.request
from xml.etree.ElementTree import ElementTree
from xml.parsers.expat import ExpatError

if 'DISPLAY' not in os.environ or platform.system() == 'Windows':
    # Curses is not available on Windows
    cli = False
else:
    import curses
    cli = True

start_download = False

###########
#         #
# Gettext #
#         #
###########
current_locale, encoding = locale.getdefaultlocale()
# Hack to get the locale directory
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
localedir = os.path.join(basepath, "locale")
domain = "elatom"             # the translation file is elatom.mo

# Set up Python's gettext
if current_locale != None:
    mytranslation = gettext.translation(domain, localedir, [current_locale], fallback=True)
    mytranslation.install()
    n_ = mytranslation.ngettext
else:
    def _(text):
        return text
    def n_(singular, plural, number):
        if number < 2:
            return singular
        else:
            return plural

########
#      #
# Help #
#      #
########
usage = _("usage: %prog [options]")
parser = OptionParser(usage=usage)
group_ui = OptionGroup(parser, _("Interface"), _("Interface for launching the application."))
group_ui.add_option("-c", "--cli",
        action="store_true", dest="cli", default=False,
        help=_("Use the command line interface instead of the graphic interface (TkInter)."))
group_ui.add_option("-q", "--quiet",
        action="store_true", dest="quiet", default=False,
        help=_("Silent download, do not use any UI."))
parser.add_option_group(group_ui)
group_pod = OptionGroup(parser, _("Feeds management"), _("Manage the list of podcasts using the CLI"))
group_pod.add_option("-a", "--add",
        action="store_true", dest="add", default=False,
        help=_("Add a podcast"))
group_pod.add_option("-d", "--delete",
        action="store_true", dest="delete",
        help=_("Delete a podcast"))
group_pod.add_option("-A", "--activate",
        action="store_true", dest="activate",
        help=_("Activate a podcast"))
group_pod.add_option("-i", "--inactivate",
        action="store_true", dest="inactivate",
        help=_("Inactivate a podcast"))
group_pod.add_option("-l", "--list",
        action="store_true", dest="list",
        help=_("List all podcasts"))
group_pod.add_option("-u", "--url",
        type="string", dest="url",
        help=_("Podcast URL to manage"))
group_pod.add_option("-n", "--name",
        type="string", dest="name",
        help=_("Podcast name to manage"))
parser.add_option_group(group_pod)
(options, args) = parser.parse_args()


# http://www.voidspace.org.uk/python/articles/urllib2.shtml#error-codes
# Table mapping response codes to messages; entries have the
# form {code: (shortmessage, longmessage)}.
HTTPResponses = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
          'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
}

##########
#        #
# Config #
#        #
##########

class Config:
    _config = None
    _configfilename = None
    _downloaded = None
    _logfilename = None
    def __init__(self):
        self._configfilename = os.path.join(os.path.expanduser('~'), '.config', 'elatom', 'elatom.conf')
        self._logfilename = os.path.join(os.path.expanduser('~'), '.config', 'elatom', 'podcasts.log')
        directory = os.path.dirname(self._configfilename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(self._logfilename):
            f = open(self._logfilename, "w")
            f.write("")
            f.close()
        self._config = configparser.ConfigParser()
        if os.path.exists(self._configfilename):
            f = open(self._configfilename, 'r', encoding='utf-8')
            self._config.readfp(f)
    def addFeed(self, name, url):
        if not self._config.has_section(name):
            self._config.add_section(name)
        self._config.set(name, 'url', url)
        self._config.set(name, 'active', 'True')
        self.save()
        return name
    def _getNameFromUrl(self, url):
        feeds = self.feeds(False)
        for name in feeds:
            if feeds[name][0] == url:
                return url
    def deleteFeed(self, name=None, url=None):
        if url != None:
            name = self._getNameFromUrl(url)
        if name != None and self._config.has_section(name):
            #self._config._sections.pop(name)
            self._config.remove_section(name)
            self.save()
            return name

    def activateFeed(self, name=None, url=None, state=True):
        if url != None:
            name = self._getNameFromUrl(url)
        if name != None and self._config.has_section(name):
            self._config.set(name, "active", state)
            self.save()
            return name

    def inactivateFeed(self, name=None, url=None):
        return self.activateFeed(name, url, False)

    def feeds(self, only_active=True):
        feeds = collections.OrderedDict()
        sections = self._config.sections()
        sections.sort()
        for section in sections:
            if section == 'elatom.py':
                continue
            active = self._config.get(section, 'active')
            if only_active and active == 'False':
                continue
            feeds[section] = [self._config.get(section, 'url'), active]
        return feeds

    def isDownloaded(self, url):
        if self._downloaded == None:
            f = open(self._logfilename)
            self._downloaded = f.read().split('\n')
            f.close()
        if url in self._downloaded:
            return True
        return False

    def memory(self, url):
        if url in self._downloaded:
            return
        self._downloaded.append(url)
        f = open(self._logfilename, "a+")
        f.write(url + "\n")
        f.close()

    def save(self):
        self._sort()
        with open(self._configfilename, 'w', encoding='utf-8') as configfile:
            self._config.write(configfile)

    def _sort(self):
        old = self._config._sections.copy()
        sections = self._config.sections()
        sections.sort()
        for section in sections:
            self._config.remove_section(section)
            self._config._sections[section] = old[section]

    def downloadDirectory(self, directory=None):
        section = 'elatom.py'
        option = 'download_directory'
        if not self._config.has_section(section):
            self._config.add_section(section)
        if not self._config.has_option(section, option) or directory != None:
            if directory == None:
                directory = os.path.join(os.path.expanduser('~') , _('Downloads'), _('Podcasts'))
            self._config.set(section, option, directory)
            self.save()
            return directory
        return self._config.get(section, option)

class Download(threading.Thread):
    def __init__(self, url, filename, group=None, target=None, name=None, verbose=None):
        self._url = url
        self._filename = filename
        self.isEnded = False
        self.size = None
        self.downloaded = 0
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
        self._stopevent = threading.Event()
        threading.Thread.__init__(self, group=group, target=target, name=name, verbose=verbose)
    def run(self):
        try:
            user_agent = "elatom.py/%s" % __revision__[6:-1]
            headers = {'User-Agent': user_agent}
            req = urllib.request.Request(self._url, None, headers)
            h = urllib.request.urlopen(req)
            self.size = h.info().get('Content-Length')
            if self.size == None:
                self.size = 1
            else:
                self.size = int(self.size)
            local_file = open(self._filename + '.part', 'wb')
            #local_file.write(h.read())
            chunk_size = 8192
            while 1:
                chunk = h.read(chunk_size)
                self.downloaded += len(chunk)
                if not chunk:
                    self.isEnded = True
                    break
                local_file.write(chunk)
                # Stop downloading
                if self._stopevent.isSet():
                    self.downloaded = 0
                    os.unlink(self._filename + '.part')
                    return
            #
            local_file.close()
            if os.path.exists(self._filename + '.part'):
                os.rename(self._filename + '.part', self._filename)
                self.isEnded = True
        except urllib.error.HTTPError as e:
            self.log('HTTP Error: ' +self._url + " " + HTTPResponses[e.code][0])
        except urllib.error.URLError as e:
            try:
                self.log("URL Error: " + self._url + HTTPResponses[e.code][0])
            except AttributeError:
                self.log("URL Error2: %s %s" % (self._url, e.reason))
        except IOError as e:
            self.log("IOError : %s %s" % (self._url, e.strerror))
    def stop(self):
        self._stopevent.set()
    def log(self, text):
        print("TODO : " + text)
    def getUrl(self):
        return self._url

class FeedReader(threading.Thread):
    """
    Read from RSS:
    - the title from channel/title
    - the enclosures from item/enclosure

    From Atom (to be done):
    http://www.ibm.com/developerworks/xml/library/x-atom10/index.html
    - the title from title
    - the enclosures from entry/link[rel=enclosure]
    """
    _info = {
        "url": None,
        "pubDate": None,
        "title": None,
        "type": None,
        "length": None
        }
    def __init__(self, url, group=None, target=None, name=None, verbose=None):
        self.isEnded = False
        self.title = ""
        self._url = url
        self._urls = []
        threading.Thread.__init__(self, group=group, target=target, name=name, verbose=verbose)
    def getUrls(self):
        return self._urls

    def log(self, text):
        pass

    @staticmethod
    def parseFeed(tree:ElementTree):
        # RSS 2
        results = __class__.parseRSS2(tree)
        if results != None:
            return results
        # Atom 10
        results = __class__.parseAtom10(tree)
        if results != None:
            return results
        return None

    @staticmethod
    def parseAtom10(tree:ElementTree):
        title = tree.find('{http://www.w3.org/2005/Atom}title')
        if title == None:
            return None
        result = {"title": title.text, "files": []}
        items = tree.findall('{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}link')
        for item in items:
            if "rel" in item.attrib and item.attrib["rel"] == "enclosure":
                info = __class__._info.copy()
                for (attr,info_attr) in (("href","url"), ("title","title"), ("type","type"), ("length","length")):
                    if attr in item.attrib:
                        info[info_attr] = item.attrib[attr]
                result["files"].append(info)
        return result

    @staticmethod
    def parseRSS2(tree:ElementTree):
        title = tree.find('channel/title')
        if title == None:
            return None
        result = {"title": title.text, "files": []}
        items = tree.findall("channel/item")
        for item in items:
            enclosure = item.find('enclosure')
            if enclosure == None:
                continue
            info = __class__._info.copy()
            for attr in ("title", "pubDate"):
                tag = item.find(attr)
                if tag != None:
                    info[attr] = tag.text
            for attr in ("url", "type", "length"):
                if attr in enclosure.attrib:
                    info[attr] = enclosure.attrib[attr]
            result["files"].append(info)
        return result

    def run(self):
        try:
            f = urllib.request.urlopen(self._url)
            tree = ElementTree()
            tree.parse(f)
            results = __class__.parseFeed(tree)
            if results == None:
                self.isEnded = True
                return
            self.title = results["title"]
            for info in results["files"]:
                self._urls.append((info["url"], info["pubDate"], info["title"]))
        except urllib.error.HTTPError as e:
            self.log('HTTP Error: ' +self._url + " " + HTTPResponses[e.code][0])
        except urllib.error.URLError as e:
            self.log(self._url + " " + e.reason.strerror)
        except KeyError as e:
            self.log("KeyError: " + self._url + " " + e.reason)
        except ExpatError as e:
            self.log("ExpatError: %s (%s)"  % (self._url, e.code))
        self.isEnded = True

#####################
#                   #
# Podcast retriever #
#                   #
#####################

class Elatom(threading.Thread):
    def __init__(self, app):
        self._config = Config()
        self._app = app
        self._stopevent = threading.Event()
        threading.Thread.__init__(self)
        self._app.setElatom(self)
    def run(self):
        # get feed URLs, and set a progress bar on feed progress
        feedReaders = {}
        feeds = self._config.feeds()
        for name in feeds:
            self._app.addFeedInfo(name, 0)
            url = feeds[name][0]
            feedReaders[name] = FeedReader(url)

        # waiting
        while 1:
            time.sleep(1)
            if not start_download:
                # Stop ?
                if self._stopevent.isSet():
                    self._app.stop()
                    return
                self._app.waitingLaunch()
                continue
            break

        for name in feeds:
            feedReader = feedReaders[name]
            feedReader.start()

        # progress
        urls = {}
        i = 0
        total = len(feeds)
        while i < total:
            for name in feeds:
                feedReader = feedReaders[name]
                if feedReader.isEnded and not name in urls:
                    urls[name] = []
                    nb = 0
                    for (url, pubdate, title) in feedReader.getUrls():
                        # clean the URL
                        url = self._cleanUrl(url)
                        # if downloaded, ignore
                        if self._config.isDownloaded(url):
                            continue
                        urls[name].append((url, pubdate, title))
                        nb += 1
                    self._app.updateFeedInfo(name, n_("%d file", "%d files", nb) % nb, 0, nb)
                    i += 1
                    continue
                time.sleep(0.2)
            # Stop ?
            if self._stopevent.isSet():
                self._app.stop()
                return

        # nothing to download, exit
        if sum([len(urls[name]) for name in urls]) == 0:
            self._app.status(_("No new files to download.") + " " + _("Bye"), 0, 0)
            time.sleep(2)
            self._app.stop()
            return

        # set the download threads
        downloadThreads = {}
        downloaded = {}
        sizes = {}
        total = 0
        for name in urls:
            if len(urls[name]) ==  0:
                continue
            downloadThreads[name] = []
            sizes[name] = {"total": 0, "urls": []}
            downloaded[name] = 0
            feed_title = feedReaders[name].title
            # clean the title
            feed_title = __class__.formatTitle(feed_title)
            for (url, pubdate, title) in urls[name]:
                # format the date
                pubdate = __class__.formatDate(pubdate)
                # clean the title
                title = title.replace(feedReaders[name].title, '')
                title = __class__.formatTitle(title)
                # filename
                ext = os.path.splitext(url)[1]
                filename = os.path.join(self._config.downloadDirectory(), pubdate + '_' + feed_title + "_" + title + ext)
                # download, and set a progress bar on each feed for file progress
                d = Download(url, filename)
                downloadThreads[name].append(d)
                d.start()
                total += 1

        # update the progress bars
        ## with the total size
        i = 0
        while i < total:
            for name in downloadThreads:
                for downloadThread in downloadThreads[name]:
                    if downloadThread.size != None and not downloadThread.getUrl() in sizes[name]["urls"]:
                        sizes[name]["urls"].append(downloadThread.getUrl())
                        sizes[name]["total"] += downloadThread.size
                        i += 1
        for name in sizes:
            nb = len(sizes[name]["urls"])
            if nb > 0:
                self._app.updateFeedInfo(name,
                        ((n_("%d file", "%d files", nb) % nb) + " (" + \
                            # TRANSLATORS: mega-bytes
                            _("%.2f Mb") + ")") % (sizes[name]["total"]/1024/1024.),
                        0, sizes[name]["total"])
        ## during download
        downloaded_urls = []
        i = 0
        while i < total:
            for name in downloadThreads:
                downloaded[name] = 0
                nb = len(sizes[name]["urls"])
                for downloadThread in downloadThreads[name]:
                    if downloadThread.isEnded:
                        # tell the frontends, one more is downloaded
                        if not downloadThread.getUrl() in downloaded_urls:
                            downloaded_urls.append(downloadThread.getUrl())
                            i = len(downloaded_urls)
                        downloaded[name] += downloadThread.size
                        # save
                        self._config.memory(downloadThread.getUrl())
                    elif downloadThread.downloaded != None:
                        downloaded[name] += downloadThread.downloaded
                if sizes[name]["total"] == downloaded[name]:
                    self._app.updateFeedInfo(name, (n_("%d downloaded file", "%d downloaded files", nb) + " (" + _("%.2f Mb") + ")") % (nb, sizes[name]["total"]/1024/1024.), downloaded[name])
                else:
                    self._app.updateFeedInfo(name, (n_("Downloading %d file", "Downloading %d files", nb) + " (" + _("%.2f Mb") + ")") % (nb, sizes[name]["total"]/1024/1024.), downloaded[name])
                time.sleep(0.2)
            # Stop ?
            if self._stopevent.isSet():
                for name in downloadThreads:
                    for downloadThread in downloadThreads[name]:
                        if not downloadThread.isEnded:
                            downloadThread.stop()
                return

        # stop the frontends
        self._app.status(_("All files are downloaded.") + " " +_("Bye"), 1, 1)
        time.sleep(2)
        self._app.stop()

    def stop(self):
        self._stopevent.set()

    def _cleanUrl(self, url):
        # patch pour http://logi3.xiti.com/get/...&url=http://images.telerama.fr/...
        if 'url=' in url and 'telerama.fr' in url:
            url = url.split('url=')[1]
        return url

    @staticmethod
    def formatDate(pubdate):
        try:
            pubdate = time.strftime('%Y%m%d', time.strptime(pubdate, '%Y-%m-%dT%H:%M:%SZ'))
            return pubdate
        except:
            pass
        pubdate = pubdate.split()
        pubdate = pubdate[3] + '-' + pubdate[2] + '-' + pubdate[1]
        try:
            pubdate = time.strftime('%Y%m%d', time.strptime(pubdate, '%Y-%b-%d'))
        except:
            months = {'Jan': '01', 'Feb': '02', 'Fev': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
            for m in months:
                pubdate = pubdate.replace('-' + m + '-', months[m])
                splitted = pubdate.split('_')
                if len(splitted[0]) == 7:
                    splitted[0] = splitted[0][0:6] + '0' + splitted[0][6]
                    pubdate = '_'.join(splitted)
        return pubdate

    @staticmethod
    def formatTitle(title):
        pattern = re.compile('\W')
        title = re.sub(pattern, '', title)
        return title.replace('FranceInter', '').replace('FranceCulture', '').replace('Podcast', '').replace('podcast', '').strip()[0:20]

################
#              #
# Progress bar #
#              #
################

class BaseProgressBar:
    def __init__(self, minValue=0, maxValue=100, width=80):
        self._min = minValue
        self._max = maxValue
        self._percentDone = 0
        self._span = maxValue - minValue
        self._width = width
        self._value = minValue       # When value == max, we are 100% done
        self.setValue(minValue)           # Calculate progress

    def setMax(self, maxValue=100):
        self._max = float(maxValue)
        self._span = maxValue - self._min

    def setValue(self, value):
        """ Update the progress with the new value (with min and max
            values set at initialization; if it is over or under, it takes the
            min or max value as a default. """
        if value < self._min:
            value = self._min
        if value > self._max:
            value = self._max
        self._value = value

        # Figure out the new percent done, round to an integer
        diffFromMin = float(self._value - self._min)
        if self._max == self._min:
            self._percentDone = 100.0
        else:
            self._percentDone = (diffFromMin / float(self._span)) * 100.0
            self._percentDone = int(round(self._percentDone))

class ProgressBar(BaseProgressBar):
    """ Creates a text-based progress bar. Call the object with the `print'
    command to see the progress bar, which looks something like this:

    [=======>        22%                  ]

    You may specify the progress bar's width, min and max values on init.

        limit = 100
        width = 30
        prog = ProgressBar(0, limit, width)
        for i in range(limit+1):
            prog.setValue(i)
            print(prog, "\r", end="")
            time.sleep(0.20)

        http://code.activestate.com/recipes/168639-progress-bar-class/
    """

    def __init__(self, minValue=0, maxValue=100, width=80):
        BaseProgressBar.__init__(self, minValue=minValue, maxValue=maxValue, width=width)
        self._progBar = "[]"   # This holds the progress bar string

    def setValue(self, value=0):
        """ Update the progress bar with the new value (with min and max
            values set at initialization; if it is over or under, it takes the
            min or max value as a default. """
        BaseProgressBar.setValue(self, value)

        # Figure out how many hash bars the percentage should be
        allFull = self._width - 2
        numHashes = (self._percentDone / 100.0) * allFull
        numHashes = int(round(numHashes))

        # Build a progress bar with an arrow of equal signs; special cases for
        # empty and full
        if numHashes == 0:
            self._progBar = "[>%s]" % (' '*(allFull-1))
        elif numHashes == allFull:
            self._progBar = "[%s]" % ('='*allFull)
        else:
            self._progBar = "[%s>%s]" % ('='*(numHashes-1),
                                        ' '*(allFull-numHashes))
        # figure out where to put the percentage, roughly centered
        percentPlace = int(len(self._progBar) / 2) - len(str(self._percentDone))
        percentString = str(self._percentDone) + "%"

        # slice the percentage into the bar
        self._progBar = ''.join([self._progBar[0:percentPlace], percentString,
                                self._progBar[percentPlace+len(percentString):]
                                ])

    def __str__(self):
        return str(self._progBar)

class TkProgressBar(BaseProgressBar, tkinter.Frame):
    '''
    A simple progress bar widget.
    Inspired from klappnase http://www.velocityreviews.com/forums/t329218-need-a-progress-bar-meter-for-tkinter.html#1753710
    '''
    def __init__(self, master, fillcolor='orchid1', minValue=0, maxValue=100, width=150, text='', **kw):
        tkinter.Frame.__init__(self, master, bg='white', width=width, height=20)
        self.configure(width=width, **kw)

        self._canvas = tkinter.Canvas(self, bg=self['bg'], width=self['width'], height=self['height'],  highlightthickness=0, relief='flat', bd=0)
        self._canvas.pack(fill='x', expand=1)
        self._r = self._canvas.create_rectangle(0, 0, 0, int(self['height']), fill=fillcolor, width=0)
        self._t = self._canvas.create_text(int(self['width'])/2, int(self['height'])/2, text='')

        BaseProgressBar.__init__(self, minValue=minValue, maxValue=maxValue, width=width)
        self.setValue(minValue, text)

    def setValue(self, value=0.0, text=None):
        BaseProgressBar.setValue(self, value)
        #make the value failsafe:
        if text == None:
            #if no text is specified get the default percentage string:
            text = str(int(self._percentDone)) + ' %'
        self._canvas.coords(self._r, 0, 0, int(self['width']) * (value / self._max) , int(self['height']))
        self._canvas.itemconfigure(self._t, text=text)

##############
#            #
# Interfaces #
#            #
##############

class BaseApp:
    _elatom = None
    def addFeedInfo(self, name, total):
        raise NotImplementedError()
    def setElatom(self, elatom):
        self._elatom = elatom
    def start(self):
        raise NotImplementedError()
    def status(self, text, progress, total):
        raise NotImplementedError()
    def stop(self):
        raise NotImplementedError()
    def updateFeedInfo(self, name, status, progress, total=False):
        raise NotImplementedError()
    def waitingLaunch(self):
        raise NotImplementedError()


class CursesApp(BaseApp):
    _screen = None
    _feeds = {}
    _code = None
    _prog_width = 18
    def __init__(self):
        # initialize library, and make a window:
        self._stdscr = curses.initscr()
        (self._scr_height, self._scr_width) = (self._stdscr.getmaxyx())
        self._stdscr.keypad(1)
        # Allow color and echo text.
        curses.echo()
        curses.start_color()
        # Set 'curses.color_pair(1)' to green text on black.
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        #
        self._screen = self._stdscr.subwin(self._scr_height, self._scr_width - 1, 0, 0)
        self._screen.box()
        self._screen.hline(2, 1, curses.ACS_HLINE, self._scr_width - 3)
        self._prog = ProgressBar(0, 10, 18)
        self.status("", 0, 0)
    def addFeedInfo(self, name, total):
        self._feeds[name] = {
                "name": name[0:50],
                "number": len(self._feeds),
                "total": total,
                "progress bar": ProgressBar(0, total, self._prog_width)
                }
        prog = self._feeds[name]["progress bar"]
        prog.setValue(0)

        self._screen.addstr(3 + self._feeds[name]["number"], 1, name, curses.color_pair(0))
        self._screen.addstr(3 + self._feeds[name]["number"], self._scr_width - self._prog_width - 2, str(prog), curses.color_pair(0))
    def status(self, text, progress, total):
        self._screen.addstr(1, 1, "elatom.py", curses.color_pair(1))
        self._screen.addstr(1, 8, text)
        self._screen.addstr(1, self._scr_width - 2 - 8, time.strftime("%H:%M:%S"))
        if total > 0:
            self._prog.setMax(total)
            self._prog.setValue(progress)
            self._screen.addstr(1, self._scr_width - 2 - 8 - self._prog_width - 2, str(self._prog))
        else:
            self._screen.addstr(1, self._scr_width - 2 - 8 - self._prog_width - 2, " " * 18)
        self._screen.refresh()
    def start(self):
        pass
    def stop(self):
        """ Set everything back to normal. """
        curses.nocbreak()
        self._stdscr.keypad(0)
        self._screen.keypad(False)
        curses.echo()
        curses.endwin()

    def updateFeedInfo(self, name, status, progress, total=False):
        prog = self._feeds[name]["progress bar"]
        if total != False:
            prog.setMax(total)
        prog.setValue(progress)
        self._screen.addstr(3 + self._feeds[name]["number"], self._scr_width - self._prog_width - 2, str(prog), curses.color_pair(1))
        self._screen.refresh()
    def waitingLaunch(self):
        """ Nothing, downloading begins at start. """
        global start_download
        start_download = True
        return
        name = ""
        while 1:
            self.status(_("Waiting..."), 0, 0)
            name = self._stdscr.getstr(6,6,20)
            if name == b'quit':
                break;
            if name == b'start':
                start_download = True
                break

class QuietApp(BaseApp):
    def __init__(self):
        pass
    def addFeedInfo(self, name, total):
        pass
    def status(self, text, progress, total):
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def updateFeedInfo(self, name, status, progress, total=False):
        pass
    def waitingLaunch(self):
        pass

# keep in global space the PhotoImage objects
gifsdict = {}

class TkApp(BaseApp):
    def __init__(self):
        self.feedInfos = {}
        self.root = tkinter.Tk()
        # window title text
        self.root.title("ElAtom")
        self.root.wm_title("Elatom")
        # application icon
        iconpath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "elatom.xbm")
        if os.path.exists(iconpath):
            iconpath = "@" + iconpath
            self.root.iconbitmap(iconpath)
            self.root.wm_iconbitmap(iconpath)
        # frames
        buttonframe = tkinter.Frame(self.root)
        buttonframe.pack()
        self.feedframe = tkinter.Frame(self.root)
        self.feedframe.pack()
        # buttons
        tkinter.Button(buttonframe, text=_("Settings"), command=self.onShowConfig).pack(side=tkinter.LEFT)
        tkinter.Button(buttonframe, text=_("About"), command=self.onShowAbout).pack(side=tkinter.LEFT)
        # TRANSLATORS: Used in a button: a verb.
        tkinter.Button(buttonframe, text=_("Start"), command=self._start).pack(side=tkinter.LEFT)
        tkinter.Button(buttonframe, text=_("Quit"), command=self.stop).pack(side=tkinter.LEFT)
        self._prog = TkProgressBar(buttonframe, minValue=11, maxValue=99, width=150)
        self._prog.pack(side=tkinter.LEFT)
        self._prog.setValue(0)
        # variable
        self.vtext = tkinter.StringVar()
        self.vtext.set("ok")
        self.text = tkinter.Label(self.root, width=(40 + 35 + 10), textvariable=self.vtext, bd=1, relief=tkinter.SUNKEN, anchor='w')
        self.text.pack(side=tkinter.BOTTOM)
    def waitingLaunch(self):
        self.vtext.set(_("Waiting.") + time.strftime("%H:%M:%S"))
    def addFeedInfo(self, name, total):
        # variables
        ## To correct this exception on another Python 3.1.2 with Tk 8.5.8, value must be set at instanciation
        ## Exception _tkinter.TclError: 'can\'t unset "PY_VAR1": no such variable'
        ## In case of error
        ## _tkinter.TclError: out of stack space (infinite loop?)
        ## dev-lang/tk must be recompiled with threads enabled
        self.feedInfos[name] = [
                tkinter.StringVar(master=self.root, value=_("Beginning")),  # status
                tkinter.DoubleVar(master=self.root, value=0.0),         # progress
                tkinter.StringVar(master=self.root, value="0.0%"),      # progress text
                tkinter.DoubleVar(master=self.root, value=total),       # total
                0, 0
        ]
        # widgets
        frame = tkinter.Frame(master=self.feedframe)
        frame.pack(side=tkinter.TOP)
        ## label
        label = tkinter.Label(frame, width=40, height=1, text=name)
        label.pack(side=tkinter.LEFT)
        ## status
        self.feedInfos[name][4] = tkinter.Label(frame, width=35, textvariable=self.feedInfos[name][0], bd=1, relief=tkinter.SUNKEN, anchor='w')
        self.feedInfos[name][4].pack(side=tkinter.LEFT)
        ## progress text
        self.feedInfos[name][5] = tkinter.Label(frame, width=10, textvariable=self.feedInfos[name][2], bd=1, relief=tkinter.SUNKEN, anchor='w')
        self.feedInfos[name][5].pack(side=tkinter.LEFT)
    
    def onShowAbout(self):
        TkAbout(self.root)

    def onShowConfig(self):
        TkConfig(self.root)

    def updateFeedInfo(self, name, status, progress, total=False):
        if total != False:
            self.feedInfos[name][3].set(total)
        else:
            total = self.feedInfos[name][3].get()
        if total == 0:
            progresstext = "-"
        else:
            progresstext = "%.2f%%" % (progress / total * 100.)
        self.feedInfos[name][0].set(status)
        self.feedInfos[name][1].set(progress)
        self.feedInfos[name][2].set(progresstext)
        # status
        total = 0
        progress = 0
        for feed in self.feedInfos:
            progress += self.feedInfos[feed][1].get()
            total += self.feedInfos[feed][3].get()
        if progress >= total:
            self.vtext.set(_("All feeds are downloaded."))
        else:
            text = _("Downloading:") + " %.2f%%" % (progress / total * 100.)
            self.status(text, progress, total)

    def status(self, text, progress, total):
        self.vtext.set(text)
        if total > 0:
            self._prog.setMax(total)
            self._prog.setValue(progress)
    def start(self):
        self.root.mainloop()
    def stop(self):
        self._elatom.stop()
        time.sleep(0.2)
        self.root.quit()
        sys.exit()

    def _start(self):
        global start_download
        start_download = True
        self.vtext.set(_("Downloading the files.") + time.strftime("%H:%M:%S"))

class TkAbout(tkSimpleDialog.Dialog):
    """ Display the About dialog : it reads the README.txt file. """

    def __init__(self, parent):
        """ Create and display window. """
        tkSimpleDialog.Dialog.__init__(self, parent, _('Podcasts'))
    
    def body(self, master):
        """ Create dialog body """
        readme_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "README.txt")
        f = open(readme_path, 'r')
        text = ScrolledText(master)
        text.insert(tkinter.END, f.read())
        text.configure(state=tkinter.DISABLED)
        text.pack()
        f.close()

    def buttonbox(self):
        """ Create custom buttons """
        tkinter.Button(self, text=_('Close'), width=10, command=self.ok, default=tkinter.ACTIVE).pack(side=tkinter.RIGHT)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

class TkFeedWidget(tkinter.Frame):
    """ A widget to display the name, the url and the active box. """
    def __init__(self, master, name, url, active, width=150, text='', **kw):
        tkinter.Frame.__init__(self, master, width=width, height=20)
        self.configure(width=width, **kw)
        self.name = name
        self.url = url
        self.ckb_active = tkinter.IntVar()
        self.e_active = tkinter.Checkbutton(self, text="", variable=self.ckb_active).pack(side=tkinter.LEFT)
        if active == 'True':
            self.ckb_active.set(1)
        else:
            self.ckb_active.set(0)
        self.e_name = tkinter.Entry(self, width=40)
        self.e_name.insert(tkinter.END, name)
        self.e_name.pack(side=tkinter.LEFT)
        self.e_url = tkinter.Entry(self, width=40)
        self.e_url.insert(tkinter.END, url)
        self.e_url.pack(side=tkinter.LEFT)
        self.btn_delete = tkinter.Button(self, text="X", padx=0, pady=0, command=self.onDelete, borderwidth=0, relief=tkinter.FLAT)
        self.btn_delete.pack(side=tkinter.RIGHT)

    def onDelete(self):
        config = Config()
        config.deleteFeed(name=self.name)
        self.destroy()

class TkConfig(tkSimpleDialog.Dialog):
    """ Display the configuration dialog : feeds and download directory. """

    def __init__(self, parent):
        """ Create and display window. """
        tkSimpleDialog.Dialog.__init__(self, parent, _('Podcasts'))

    def addFeed(self):
        url = tkSimpleDialog.askstring(_("Add a podcast"), _("Podcast address"))
        if url:
            try:
                f = urllib.request.urlopen(url)
                tree = ElementTree()
                tree.parse(f)
                results = FeedReader.parseFeed(tree)
                title = results['title']
                name = self.config.addFeed(name=title, url=url)
                if name != None:
                    self.widgets[name] = TkFeedWidget(self.frame, name, name, 'True')
                    self.widgets[name].pack()
                    self.update()
            except urllib.error.HTTPError as e:
                tkMessageBox.showwarning("Yes", 'HTTP Error: ' + url + " " + HTTPResponses[e.code][0])
            except urllib.error.URLError as e:
                try:
                    self.log("URL Error: " + url + HTTPResponses[e.code][0])
                except AttributeError:
                    self.log("URL Error2: %s %s" % (url, e.reason))
            except IOError as e:
                self.log("Error: " + url + " " + e)

    def askDirectoryDownload(self):
        directory = tkFileDialog.askdirectory()
        if directory != "":
            self.download_directory.set(directory)

    def body(self, master):
        """ Create dialog body """
        self.master = master
        # podcasts
        tkinter.Label(master, text=_("Podcasts")).grid(row=0, column=0)
        # canvas + vscroll : container for the feeds
        self.canvas = tkinter.Canvas(master, width=650, height=500)
        self.canvas.grid(row=1, column=0, sticky='nswe')
        self.vscroll = tkinter.Scrollbar(master, orient=tkinter.VERTICAL, command=self.canvas.yview)
        self.vscroll.grid(row=1, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vscroll.set)
        self.frame = tkinter.Frame(self.canvas)
        self.frame.pack()
        self.config = Config()
        feeds = self.config.feeds(False)
        self.widgets = {}
        for name in feeds:
            self.widgets[name] = TkFeedWidget(self.frame, name, feeds[name][0], feeds[name][1])
            self.widgets[name].pack()
        # download directory
        self.frame_dd = tkinter.Frame(master)
        tkinter.Label(self.frame_dd, text=_("Download directory"), width=30).pack(side=tkinter.LEFT)
        self.download_directory = tkinter.StringVar()
        self.download_directory.set(self.config.downloadDirectory())
        tkinter.Entry(self.frame_dd, textvariable=self.download_directory, width=40).pack(side=tkinter.LEFT)
        open_image = tkinter.PhotoImage(format='gif', 
            data="R0lGODlhEAAQAIcAADFKY0L/QplnAZpoApxqBJ5sBqBuCKJwCqNxC6RyDKVzDad1D6x6FLB+GLOBG7WCHbeEH7qHIr2KJcaaGcaaGsKPKsiVMMmWMcuYM8yZNMmgIc+iJte4QNq/bOKzQ+LBUP3VcP/bdfDkev/kf5SlvZylvbe3t5ytxqW11qm92r3GxrnK5P/XhP/rhP/viffwif/4k///mf//nP//pcTExMXFxc3NzdHR0cbW69jh8efv9+vz//r7/P///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAMAAAEALAAAAAAQABAAAAiZAAMIHEiwoMGDBzNkwHDBAkKBGXpI5MGjAsKIMjJm7CEhAoQHDhoIxNBDo0mJEhncCHChB4yXMGPKWFBjgs2bOG1+aIGAxoQYJk3G6DCBhQGfQGPClPFiAogCNAL8dEG1KtUZGjwQiPpTxoivYEfM4LBhQFSpMUKoXatWBAUBNQROUECXboIDBgoQGGDCxkAbNAILHuz34cGAADs=")
        gifsdict['open_image'] = open_image
        tkinter.Button(self.frame_dd, image=open_image, command=self.askDirectoryDownload).pack(side=tkinter.LEFT)
        #tkinter.Button(self.frame_dd, text="?", command=self.askDirectoryDownload).pack(side=tkinter.LEFT)
        self.frame_dd.grid(row=2, column=0)

        self.update()

    def buttonbox(self):
        """ Create custom buttons """
        tkinter.Button(self, text=_('Add a podcast'), width=20, command=self.addFeed, default=tkinter.ACTIVE).pack(side=tkinter.LEFT)
        tkinter.Button(self, text=_('Save'), width=10, command=self.save, default=tkinter.ACTIVE).pack(side=tkinter.RIGHT)
        tkinter.Button(self, text=_('Cancel'), width=10, command=self.close, default=tkinter.ACTIVE).pack(side=tkinter.RIGHT)
        self.bind("<Return>", self.save)
        #self.bind("<Escape>", self.close) # bug

    def close(self):
        """ Close the windows. """
        self.frame.destroy()
        tkSimpleDialog.Dialog.ok(self)

    def save(self):
        """ Save the changes on name, url or activation. """
        config = Config()
        for name in self.widgets:
            if self.widgets[name].e_name.get() != name or self.widgets[name].e_url.get() != self.widgets[name].url:
                config.addFeed(name=self.widgets[name].e_name.get(), url=self.widgets[name].e_url.get())
                config.deleteFeed(name)
            if self.widgets[name].ckb_active.get() == 1:
                config.activateFeed(self.widgets[name].e_name.get())
            else:
                config.inactivateFeed(self.widgets[name].e_name.get())
        if self.download_directory.get() != self.config.downloadDirectory():
            self.config.downloadDirectory(self.download_directory.get())
        self.close()

    def update(self):
        self.frame.update()
        self.canvas.create_window(0, 0, window=self.frame, anchor=tkinter.NW)
        self.canvas.configure(scrollregion=self.canvas.bbox(tkinter.ALL))

##########################

if __name__ == "__main__":
    if options.add:
        config = Config()
        name = config.addFeed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is added.""") % name)
        sys.exit()
    if options.delete:
        config = Config()
        name = config.deleteFeed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is deleted.""") % name)
        sys.exit()
    if options.activate:
        config = Config()
        name = config.activateFeed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is activated.""") % name)
        sys.exit()
    if options.inactivate:
        config = Config()
        name = config.inactivateFeed(name=options.name, url=options.url)
        if name != None:
            print(_("""The feed "%s" is inactivated.""") % name)
        sys.exit()
    if options.list:
        config = Config()
        feeds = config.feeds(False)
        line = "%s :\n   %s"
        head = _("Active feeds")
        print(head)
        print("=" * len(head))
        print()
        for name in feeds:
            if feeds[name][1] == 'True':
                print(line % (name, feeds[name][0]))
        print()
        head = _("Inactive feeds")
        print(head)
        print("=" * len(head))
        print()
        for name in feeds:
            if feeds[name][1] == 'False':
                print(line % (name, feeds[name][0]))

        sys.exit()
    if options.quiet:
        start_download = True
        app = QuietApp()
    elif cli and options.cli:
        app = CursesApp()
    elif tkinter_available:
        app = TkApp()
    else:
        start_download = True
        app = QuietApp()
    elatom = Elatom(app)
    elatom.start()
    app.start()

