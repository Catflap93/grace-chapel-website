#!/usr/bin/env python3
"""Fetch public channel videos using YouTube Data API v3. Requires YOUTUBE_API_KEY.
For historical backfill, paginate playlistItems; quotas apply. Does not require channel login.
"""
import os,json,re,urllib.parse,urllib.request,datetime,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
KEY=os.getenv('YOUTUBE_API_KEY'); HANDLE=os.getenv('YOUTUBE_HANDLE','goodnews4folkestone')
if not KEY: sys.exit('Set YOUTUBE_API_KEY (Google Cloud YouTube Data API v3).')
def api(path,**params):
    url='https://www.googleapis.com/youtube/v3/'+path+'?'+urllib.parse.urlencode(dict(params,key=KEY))
    with urllib.request.urlopen(url,timeout=30) as r:return json.load(r)
def classify(title,description):
    text=title+' '+description
    books=['1 Corinthians','2 Corinthians','1 Thessalonians','2 Thessalonians','1 Timothy','2 Timothy','1 Peter','2 Peter','1 John','2 John','3 John','Genesis','Exodus','Leviticus','Numbers','Deuteronomy','Joshua','Judges','Ruth','1 Samuel','2 Samuel','1 Kings','2 Kings','1 Chronicles','2 Chronicles','Ezra','Nehemiah','Esther','Job','Psalms','Psalm','Proverbs','Ecclesiastes','Song of Solomon','Isaiah','Jeremiah','Lamentations','Ezekiel','Daniel','Hosea','Joel','Amos','Obadiah','Jonah','Micah','Nahum','Habakkuk','Zephaniah','Haggai','Zechariah','Malachi','Matthew','Mark','Luke','John','Acts','Romans','Galatians','Ephesians','Philippians','Colossians','Titus','Philemon','Hebrews','James','Jude','Revelation']
    book=next((b for b in books if re.search(r'(?<!\w)'+re.escape(b)+r'\b',title,re.I)),None)
    if not book and re.search(r'Gospel of John',text,re.I):book='John'
    # Capture named preacher after explicit attribution; otherwise leave blank.
    match=re.search(r'\b(?:preached\s+by|preached\s+at\b[^.]{0,150}?\bby|preacher\s*:?\s*|speaker\s*:?\s*|(?:ministry|message|sermon|preaching)\s+by)\s+(?:(?:Pastor|Rev\.?|Elder|Deacon)\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b',description,re.I)
    preacher=match.group(1) if match else None
    if preacher:
        preacher=re.split(r'\s+(?:on|at|and|the|with|from|in|for|Hymn)\b',preacher,maxsplit=1,flags=re.I)[0].strip()
        preacher=re.sub(r'^(?:Pastor|Rev\.?|Ptr|Elder|Deacon)\s+','',preacher,flags=re.I)
    dm=re.search(r'\b(?:Sunday\s+(?:the\s+)?)?(\d{1,2})(?:st|nd|rd|th)?\s+(?:of\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d\d|19\d\d)\b',description,re.I)
    preached=None
    if dm:
        try:preached=datetime.datetime.strptime(f'{dm.group(1)} {dm.group(2)} {dm.group(3)}','%d %B %Y').date().isoformat()
        except ValueError:pass
    return book,preacher,preached
channel=api('channels',part='contentDetails',forHandle=HANDLE).get('items',[])
if not channel:sys.exit('YouTube channel not found; check handle.')
playlist=channel[0]['contentDetails']['relatedPlaylists']['uploads']
ids=[];token=None
while True:
    args=dict(part='contentDetails',playlistId=playlist,maxResults=50)
    if token:args['pageToken']=token
    page=api('playlistItems',**args)
    ids += [i['contentDetails']['videoId'] for i in page.get('items',[]) if i.get('contentDetails',{}).get('videoId')]
    token=page.get('nextPageToken')
    if not token:break
records=[]
for offset in range(0,len(ids),50):
    page=api('videos',part='snippet,status',id=','.join(ids[offset:offset+50]),maxResults=50)
    for video in page.get('items',[]):
        if video.get('status',{}).get('privacyStatus')!='public':continue
        s=video['snippet'];title=s.get('title','Untitled sermon');description=s.get('description','')
        book,preacher,preached=classify(title,description)
        records.append(dict(id=video['id'],title=title,book=book,preacher=preacher,preached=preached,series=None,description=description,uploaded=s.get('publishedAt',''),source='youtube'))
# Preserve editor-curated overrides (keyed by YouTube ID).
overrides_file=ROOT/'data'/'sermon-overrides.json'
if overrides_file.exists():
    overrides=json.loads(overrides_file.read_text())
    for item in records:item.update(overrides.get(item['id'],{}))
records.sort(key=lambda x:x.get('preached') or x.get('uploaded') or '',reverse=True)
(ROOT/'data'/'sermons.json').write_text(json.dumps({'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sermons':records},indent=2,ensure_ascii=False)+'\n')
print('Saved',len(records),'public videos')
