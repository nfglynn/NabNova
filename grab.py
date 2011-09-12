import datetime, urllib, re, os, sys, traceback
current = datetime.date(2011,5,29)
current = current + datetime.timedelta(7)1~
until = datetime.date(2011,9,11)
while current != until:
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
        wavfile = "%04_%02d_%02d.wav" % (current.year, current.month, current.day)
        mplayercmdtemplate = "mplayer %(rtsp)s -ao pcm:file=%(wavfile)s -vc null -vo null"
        mplayercmd = mplayercmdtemplate % {"wavfile": wavfile, "rtsp": rtsp}
        print mplayercmd
        os.system(mplayercmd)
        # Lame Command
        mp3file = wavfile.replace('.wav', '.mp3')
        os.system("lame %s %s" % (wavfile, mp3file))
        # Delete Temp Files
        if not os.path.exists(mp3file):
            print "bollocks"
            sys.exit(-1)
        os.system("rm " + wavfile)
        # Publish Command
        print "Publishing %s to nglynn.com/nova" % mp3file
        os.system("mv %s /var/www/nova/%s" % (mp3file, mp3file))
        os.system("chmod 755 /var/www/nova/*.mp3")
    except:
        traceback.print_exc()
        print "An error occurred processing %s" % mp3file
    finally:
        current = current + datetime.timedelta(7)

"""
* To Do* 
 - Make it check for new ones, cron?
 - Proper mp3 name.
 - Set ID3 Tags?
 - RSS?
"""
