import songs
import pyglet
import random
import sys
import time
import getopt

def usage():
    use = '''python Radio.py [options]
    --help, -h : Print this usage documentation
    --comment wiki/basic/none, -c wiki/basic/none: Type of commentary
    '''
    print use

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", "comment="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    supportedExtensions = ['.mp3']
    player = songs.PlayerMod('./Music/',supportedExtensions)
    songstack = songs.Songs.songlist

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-c', '--comment'):
            if arg == 'wiki':
                while songstack != []:
                    working_song = songstack[random.randint(0, len(songstack) - 1)]
                    working_song.queue_with_wpcomm(player)
                    songstack.remove(working_song)
            elif arg == 'basic':
                while songstack != []:
                    working_song = songstack[random.randint(0, len(songstack) - 1)]
                    working_song.queue_with_bpcomm(player)
                    songstack.remove(working_song)
            elif arg == 'none':
                while songstack != []:
                    working_song = songstack[random.randint(0, len(songstack) - 1)]
                    working_song.queue_song(player)
                    songstack.remove(working_song)
            else:
                print '''Please specify comment type: 'wiki', 'basic', or 'none'.\n'''
                sys.exit(2)
    if opts == []:
        print '''Playing with wiki commentary.\n'''
        while songstack != []:
            working_song = songstack[random.randint(0, len(songstack) - 1)]
            working_song.queue_with_wpcomm(player)
            songstack.remove(working_song)
        player.play()
        pyglet.app.run()
            
    


if __name__ == '__main__':
    main(sys.argv[1:])