import datetime, urllib, re, os, sys, traceback
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
import PyRSS2Gen

PUBLISH_PATH = "/var/www/nova"
current = datetime.date(2011,1,9)

while current <= datetime.date.today():
    try:
        # Download smil
        smiltemplate = "http://dynamic.rte.ie/quickaxs/209-lyrc-nova-%(year)s-%(month)s-%(day)s.smil"
        smil = smiltemplate % {"year": current.year,
                               "month": current.month,
                               "day": current.day}
        # Extract ra link
        filename, headers = urllib.urlretrieve(smil)
        smilfile= open(filename)
        content = smilfile.read()
        smilfile.close()
        os.system("rm " + filename)
        rtsp = re.findall("rtsp://.*", content)[0].rstrip('"')
        print "Grabbing NOVA for %s" % repr(current)
        # Mplayer Command
        wavfile = "LyricFM_Nova_%04d%02d%02d.wav" % (current.year, current.month, current.day)
        if os.path.exists(os.path.join(PUBLISH_PATH, wavfile.replace('.wav', '.mp3'))):
            print "Episode downloaded before, moving on..."
            continue
        mplayercmdtemplate = "mplayer %(rtsp)s -ao pcm:file=%(wavfile)s -vc null -vo null"
        mplayercmd = mplayercmdtemplate % {"wavfile": wavfile, "rtsp": rtsp}
        print mplayercmd
        os.system(mplayercmd)
        # Lame Command
        mp3file = wavfile.replace('.wav', '.mp3')
        os.system("lame --preset fast extreme %s %s" % (wavfile, mp3file))
        # ID3 Tags
        mp3 = MP3(mp3file, ID3=EasyID3)
        try:
            mp3.add_tags(ID3=EasyID3)
        except error:
            pass
        mp3['title'] = ("Nova - %04d%02d%02d.wav" % (current.year, current.month, current.day))
        mp3['artist'] = "Bernard Clarke"
        mp3['album'] = "Lyric FM - Nova"
        mp3.tags.add(APIC(encoding=3, # 3 is for utf-8
                          mime='image/jpeg', # image/jpeg or image/png
                          type=3, # 3 is for the cover image
                          desc=u'Cover',
                          data=open('nova.jpeg').read()))
        mp3.save()

        # Delete Temp Files
        if not os.path.exists(mp3file):
            print "bollocks"
            sys.exit(-1)
        os.system("rm " + wavfile)
        # Publish Command
        print "Publishing %s to nglynn.com/nova" % mp3file
        os.system("mv %s %s" % (mp3file, os.path.join(PUBLISH_PATH, mp3file)))
        os.system("chmod 755 %s/*.mp3" % PUBLISH_PATH)
    except:
        traceback.print_exc()
        print "An error occurred processing %s" % mp3file
    finally:
        current = current + datetime.timedelta(7)

# Create Podcast
mp3s = sorted([e for e in os.listdir(PUBLISH_PATH) if e.endswith('.mp3')])
rss = PyRSS2Gen.RSS2(title = "Nova (LyricFM) via nglynn.com/nova",
                     link = "http://www.nglynn.com/nova",
                     description = "Nova (Bernard Clarke on RTE Lyric FM)",
                     lastBuildDate = datetime.datetime.now(),
                     items = [PyRSS2Gen.RSSItem(title = mp3,
                                                link = "http://www.nglynn.com/nova/"+mp3,
                                                description = "Nova (RTE Lyric FM) presented by Bernard Clarke (%s)" % mp3.split('_')[-1],
                                                pubDate = datetime.datetime.fromtimestamp(os.path.getmtime(x)),
                                                enclosure = PyRSS2Gen.Enclosure("http://www.nglyn.com/nova/%s" % mp3, os.path.getsize(os.path.join(PUBLISH_PATH, mp3)),"audio/mpeg"),
                                                categories = [PyRSS2Gen.Category("Experimental")],
                                                guid = PyRSS2Gen.Guid("http://www.nglynn.com/nova/"+ mp3)) for x in mp3s])
rss.write_xml(open(os.path.join(PUBLISH_PATH, "podcast.xml"), "w"))
os.system("chmod 755 %s" % os.path.join(PUBLISH_PATH, "podcast.xml"))
print "Published Podcast"

"""
* To Do* 
 - Make it check for new ones, cron?
"""
