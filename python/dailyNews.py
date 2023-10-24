import feedparser
import json
import requests
from datetime import datetime
from time import mktime
import html
import telebot
import dateparser
import os
import sys
import argparse



class Feeds:
    def __init__(self, filePath, newsJsonPath = None):
        self.filePath = filePath
        self.sources = self.readSources(self.filePath)
        if newsJsonPath:
            self.newInfo = self.jsonFileToNews(newsJsonPath)
        else:
            self.newInfo = {}

    def jsonFileToNews(self, newsJsonPath):
        with open(newsJsonPath) as file:
            content = json.load(file)
            
        return content
    
    def readSources(self, sourceFile):
        with open(sourceFile) as file:
            feeds = json.loads(file.read())

        return feeds

    def getSources(self, withEmpty = False):
        sources = []
        for src in self.sources:
            lowerSrc = src.lower()
            if (includeFeeds and (lowerSrc not in includeFeeds)):
                continue
            elif (excludeFeeds and (lowerSrc in excludeFeeds)):
                continue
            if withEmpty: sources.append(src)
            else:
                if len(self.sources[src]) > 0:
                    sources.append(src)
        return sources

    def getFeedsOfSource(self, source):
        if (source in self.sources and len(self.sources[source]) > 0):
            return self.sources[source]
        else:
            return None

    def getFeed(self, source, feedName):
        rssURL = self.sources[source][feedName]['rss']
        rss = feedparser.parse(rssURL)

        return rss

    def parseEntry(self, entry):
        allowed = ['title', 'link']
        clearEntry = {}
        for item in entry:
            if item.lower() in allowed:
                clearEntry[item] = entry[item]
        return clearEntry

    def getDate(self, entry):
        if hasattr(entry, 'published_parsed'):
            pubDate = datetime.fromtimestamp(mktime(entry.published_parsed))
        elif hasattr(entry, 'updated_parsed'):
            pubDate = datetime.fromtimestamp(mktime(entry.updated_parsed))
        else:
            pubDate = dateparser.parse(entry.updated_date)
            
        return pubDate
        
    def isNewEntry(self, title, entry):
        for item in self.newInfo[title]:
            if item['entry']['link'] == entry['link']:
                return False
        return True
    
    def getNewInfo(self, timeBorder):
        runAt = datetime.utcnow()
        for src in self.getSources():
            for feed in self.getFeedsOfSource(src):
                title = self.sources[src][feed]['title']
                empty = not title in self.newInfo
                try:
                    feedInfo = self.getFeed(src, feed)
                except Exception as e:
                    print(e)
                    continue
                if not empty:
                    feedInfo.entries.reverse()
                for entry in feedInfo.entries:
                    pubDate = self.getDate(entry)
                    if (pubDate > timeBorder):
                        currentEntry = self.parseEntry(entry)
                        if empty:
                            self.newInfo[title] = []
                            self.newInfo[title].append({"entry": currentEntry, "fetchDate": runAt})
                            empty = False
                        else:
                            isNewEntry = self.isNewEntry(title, currentEntry)
                            if isNewEntry:
                                self.newInfo[title].insert(0, {"entry": currentEntry, "fetchDate": runAt})
                            else:
                                continue
        return self.newInfo

    def saveNewsToJson(self, newsJsonPath):
        with open(newsJsonPath, "w") as outfile:
            json.dump(self.newInfo, outfile, indent=4, sort_keys=True, default=str)

        return True
            
    def generateTgView(self):
        result = ""
        tgView = "<b>[{}]</b>\n\n{}"
        detailTemplate = "<a href='{}'>{}</a>\n"
        if self.newInfo:
            for feedName in self.newInfo:
                detail = ""
                for item in self.newInfo[feedName]:
                    detail += detailTemplate.format(item['entry']['link'], html.escape(item['entry']['title']))
                detail += "\n"
                result += tgView.format(feedName, detail)
            return result
        else:
            return None


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--feed', required=True, help="Feed file path")
parser.add_argument('-o', '--output', type=str, default=None, help="Part of output filename pattern")
group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-i', '--include', type=str, default=None, help="Include all except this feeds. Ex.: CVE,Hackerone")
group.add_argument('-e', '--exclude', type=str, default=None, help="Exclude all except this feeds. Ex.: CVE")


args = parser.parse_args()

feedFilePath = args.feed.strip()

if args.output:
    outName = args.output.strip()
    stateFile = outName + '_state.json'
    todayFilename = outName + '_today.json'
    yesterdayFilename = outName + '_yesterday.json'
else:
    stateFile = 'state.json'
    todayFilename = 'today.json'
    yesterdayFilename = 'yesterday.json'

if args.include: includeFeeds = [i.strip().lower() for i in args.include.split(',')]
else: includeFeeds = []

if args.exclude: excludeFeeds = [i.strip().lower() for i in args.exclude.split(',')]
else: excludeFeeds = []

print(os.getcwd() + stateFile)
print(todayFilename)
print(yesterdayFilename)
print(includeFeeds)
print(excludeFeeds)
exit()

if not os.path.isfile(stateFile):
    nowTime = datetime.utcnow()
    print(nowTime)
    with open(stateFile, "w") as file:
        json.dump({"lastRun": str(nowTime.date())}, file)
    feedConfig = Feeds(feedFilePath)
    feedConfig.getNewInfo(datetime.strptime(nowTime.strftime("%m-%d-%Y"), '%m-%d-%Y'))
    feedConfig.saveNewsToJson(todayFilename)
else:
    nowTime = datetime.utcnow()
    with open(stateFile) as file:
        jsonData = json.load(file)
    lastRun = dateparser.parse(jsonData['lastRun'])
    print(lastRun)
    if lastRun.date() < datetime.now().date():
        print("Oh...new day!")
        os.replace(todayFilename, yesterdayFilename)
        with open(stateFile, "w") as file:
            json.dump({"lastRun": str(nowTime.date())}, file)
        feedConfig = Feeds(feedFilePath)
        feedConfig.getNewInfo(datetime.strptime(nowTime.strftime("%m-%d-%Y"), '%m-%d-%Y'))
        feedConfig.saveNewsToJson(todayFilename)
    else:
        print("Same day, updating...!")
        with open(stateFile, "w") as file:
            json.dump({"lastRun": str(nowTime.date())}, file)
        feedConfig = Feeds(feedFilePath, todayFilename)
        feedConfig.getNewInfo(datetime.strptime(nowTime.strftime("%m-%d-%Y"), '%m-%d-%Y'))
        feedConfig.saveNewsToJson(todayFilename)
    









