'''
This module describes the class Songs. Each instance of it keeps basic song
info and metadata as attributes, and has methods defined for queueing songs
with or without preceding basic/wiki commentary.

Also defines the class of players PlayerMod.

TODO:
-Allow for choice of voices in commentary creation.
-Allow for commentary before or after song.
-Add attributes to songs that draw from Wiki infoboxes.
'''

import os
import eyeD3
import time
import pyglet
import pyglet.media
import subprocess
import getinfo
pyglet.options['audio'] = ('openal', 'alsa')

PATH = os.getcwd()

class Songs():
    ''' A class that stores all the relevant data for the songs.'''
    number = 0
    songlist = []
    def __init__(self, filename):
        tag = eyeD3.Tag()
        tag.link(filename)
        self.filename = filename
        self.title = tag.getTitle()
        self.artist = tag.getArtist()
        self.album = tag.getAlbum()
        self.source = pyglet.media.load(filename)
        Songs.number += 1
        Songs.songlist.append(self)
        
    def __del__(self):
        print 'Song object ' + self.title + ' destroyed.'

    
    def queue_song(self, player):
        ''' Queues a song on player (an instance of pyglet.media.Player() that
        is assummed to exist.'''
        player.queue(self.source)
    
    def create_basic_prior_commentary(self):
        with open("basic_commentary.txt", "w") as txt:
            print >>txt, "Next up, we have the song {0} from {1}'s album {2}".format(self.title, self.artist, self.album)
        subprocess.call("say -v Alex -f {0}/basic_commentary.txt -o {0}/basic_prior_commentary.wav \
                        --data-format=LEI16@16000".format(PATH), shell=True)
    
    
    def create_wiki_commentary(self):
        with open("wiki_commentary.txt", "w") as txt:
            print >>txt, getinfo.make_speakable(getinfo.get_wiki_maintext(self.album))
        subprocess.call("say -v Alex -f {0}/wiki_commentary.txt  -o {0}/wiki_prior_commentary.wav \
                        --data-format=LEI16@16000".format(PATH), shell=True)
    
    def queue_with_bpcomm(self, player):
        self.create_basic_prior_commentary()
        player.queue(pyglet.media.load("{0}/basic_prior_commentary.wav".format(PATH)))
        player.queue(self.source)
    
    def queue_with_wpcomm(self, player):
        self.create_wiki_commentary()
        player.queue(pyglet.media.load("{0}/wiki_prior_commentary.wav".format(PATH)))
        player.queue(self.source)
        
class PlayerMod(pyglet.media.Player):
    def __init__(self, directory, extensionList):
        pyglet.media.Player.__init__(self)
        self.read_in_songs(directory, extensionList)
    def read_in_songs(self, directory, extensionList):
        fileList = [os.path.normcase(f)
                for f in os.listdir(directory)]           
        fileList = [os.path.join(directory, f) 
                   for f in fileList
                if os.path.splitext(f)[1] in extensionList]
        fileDict = [(os.path.splitext(os.path.basename(f))[0].replace(' ', '_'), f) for f in fileList]
        for item in fileDict:
            item_helper2 = '''self.{0} = Songs("{1}")'''.format(*item)
            exec(item_helper2)
    def get_info(self):
        return dir(self)


