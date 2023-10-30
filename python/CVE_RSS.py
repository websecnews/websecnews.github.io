import github
from github import Github
from github import Auth
import datetime
import os
import json
import re
import html
from feedgen.feed import FeedGenerator
import feedparser
import sys

def getEnDescription(json):
    for lang in json:
        if lang["lang"] == "en": return lang["value"]
    return "No english description"

def addItemToRSS(fe, CVEdata):
    CVEid = CVEdata["cveMetadata"]["cveId"]
    link = "https://www.cve.org/CVERecord?id=" + CVEid
    CVEdescr = getEnDescription(CVEdata["containers"]["cna"]["descriptions"]).strip()
    CVEdescr = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\U00010000-\U0010FFFF]+', '', CVEdescr)
    if "title" in CVEdata["containers"]["cna"]: CVEtitle = html.escape(CVEdata["containers"]["cna"]["title"])
    else:
        maxLen = 140
        if len(CVEdescr) > maxLen:
            CVEtitle = CVEdescr[:140] + "..."
        else:
            CVEtitle = CVEdescr[:140]

    
    fe.title(CVEid + ' | ' + CVEtitle)
    fe.link(href=link)
    fe.description(CVEdescr)
    if link in knownURLs:
        pubdate = getCVEdate(CVEid)
    else:
        pubdate = datetime.datetime.now(tz=datetime.timezone.utc)
    
    fe.pubDate(pubdate)
    
    return

def getCVEdate(CVEid):
    for entry in rss.entries:
        if entry['links'][0]['href'] == 'https://www.cve.org/CVERecord?id=' + CVEid:
            return entry['published']

def getVendor(affected):
    lvList = []
    for item in affected:
        if "vendor" in item:
            vendor = item['vendor']
            if vendor not in lvList:
                lvList.append(vendor)

    return ",".join(lvList)

def getNewCVE(files):
    result = []
    for fl in files:
        if (fl.status == 'added' and re.match(r"cves[/\d/x]+/CVE-[\d]+-[\d]+\.json", fl.filename)):
            result.append(fl)
    return result

githubToken = sys.argv[1]

auth = Auth.Token(githubToken)
g = Github(auth=auth, per_page=100)

repo = g.get_repo("CVEProject/cvelistV5")

fg = FeedGenerator()
fg.title('New CVE from cve.org feed')
fg.subtitle('Last 2 days CVE feed!')
fg.link( href='https://github.com/test.xml', rel='self' )
fg.language('en')


RSS_FEED = "./cve_rss.xml"
daysAgo = datetime.datetime.combine(datetime.datetime.utcnow().date() - datetime.timedelta(days = 2), datetime.datetime.min.time())
print(daysAgo)

knownURLs = []
if not os.path.exists(RSS_FEED):
    hasNewItem = True
else:
    hasNewItem = False
    rss = feedparser.parse(RSS_FEED)
    for entry in rss.entries:
        knownURLs.append(entry['links'][0]['href'])

new_commits = repo.get_commits(since=daysAgo)
print(new_commits.totalCount)

for commit in new_commits:
    if "(0 new |" in commit.commit.message:
        continue
    newFiles = getNewCVE(commit.files)
    for fileCVE in newFiles:
        CVEdata = json.loads(repo.get_contents(fileCVE.filename).decoded_content.decode())
        CVEURL = "https://www.cve.org/CVERecord?id=" + CVEdata["cveMetadata"]["cveId"]
        if (CVEdata['cveMetadata']['state'].lower() != 'PUBLISHED'.lower()):
            continue
        if (not hasNewItem and CVEURL not in knownURLs):
            hasNewItem = True
        fe = fg.add_entry(order='append')
        addItemToRSS(fe, CVEdata)
if (hasNewItem):
    print("New CVE in feed!")
    fg.rss_file(RSS_FEED)
        
