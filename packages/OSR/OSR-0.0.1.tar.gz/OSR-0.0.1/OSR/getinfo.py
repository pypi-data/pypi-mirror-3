'''

This module scrapes wikipedia for information about songs, albums or artists. It should
turn the infobox into a dictionary, and the text sections into plain text.

TODO
-Fix get_wiki_maintext.
-Finish get_wiki_score.
-Fix get_wiki_infobox.
-Fix make_speakable.

'''

import urllib2
import re
from bs4 import BeautifulSoup
import string

###########################################################################################
#### HTML regexes ####
# Comment
comment = re.compile(r'<!--.*?-->', re.DOTALL)

# Tagged elements to remove (tetr) - anything enclosed by left-right tags is also deleted.
tetr = ['ref', 'href']
tetr_re = []
for tag in tetr:
    tagre = re.compile(r'<{0}[^>]*>.*?</{0}[^>]*>'.format(tag), re.DOTALL)
    tetr_re.append(tagre)

# Tags to remove (ttr) - only the tags are deleted.
ttr = ['br', 'small', 'ref']
ttr_re = []
for tag in ttr:
    tagre_left = re.compile(r'<{0}[^>]*>'.format(tag))
    tagre_right = re.compile(r'</{0}[^>]*>'.format(tag))
    ttr_re.append(tagre_left)
    ttr_re.append(tagre_right)
    
# Leftover html entities
entities = ['nbsp', 'amp']
entities_re = []
for tag in entities:
    tagre = re.compile(r'&{0}'.format(tag))
    entities_re.append(tagre)
# Wiki links "["
links1 = re.compile(r'\[\[[^\]]*\]\]') #finds wikilinks
links2 = re.compile(r'[^\|]*\|') #finds separators

#Parenthesis
par = re.compile(r'\([^\)]*\)')

#TODO

# "{"'s
bra = re.compile(r'\{\{[^\}]*\}\}')

#Redirect
redirect = ['REDIRECT']
redirect_re = []
for tag in redirect:
    tagre = re.compile(r'#{0}[^\]]*\]'.format(tag),  re.IGNORECASE)
    redirect_re.append(tagre)
    
    
# Infobox #
infoboxr = ['infobox']
infobox_re = []
for tag in infoboxr:
    tagre = re.compile(r'\{\{%s(({.*?})|[^}])*\}\}' % tag, re.DOTALL | re.IGNORECASE)
    infobox_re.append(tagre)

# End infobox #
#### End HTML regexes ####
##################################################################################

def clean_html(text):
    '''Cleans text with the regexes listed above.
    '''
    for pattern in tetr_re:
        text = re.sub(pattern, "", text)  #tetr must happen before ttr!
    for pattern in ttr_re:
        text = re.sub(pattern, "", text)
    
    for pattern in entities_re:
        text = re.sub(pattern, "", text)

    done = 0
    while done != 1:
        par_match = re.search(par, text)
        if par_match == None:
            break
        text = string.replace(text, par_match.group(), "")
    while done != 1:
        bra_match = re.search(bra, text)
        if bra_match == None:
            break
        text = string.replace(text, bra_match.group(), "")
    while done != 1:
        link_match = re.search(links1, text)
        if link_match == None:
            break
        link2_match = re.search(links2, link_match.group())
        if link2_match != None:
            text = string.replace(text,link_match.group(), link2_match.group()[2:-1], 1)
            continue
        else:
            text = string.replace(text, link_match.group(), link_match.group()[2:-2], 1)
    
    
    
    return text

def get_wiki(titles):
    '''Gets a wikipedia article, returns tuple with full page, main text, and infobox.
    TODO:
    -Raise exception if page is not found or disambiguation page is reached (to be
    handled in Songs.py).
    -Make sure page is of the right type (artist, album, etc.) and not another page with
    the same title.
    '''
    titles = titles.replace(" ", "%20")
    params = { "format":"xml", "action":"query", "titles":titles, "prop":"revisions",
              "rvprop":"content", "rvsection":"0" }
    qs = "&".join("%s=%s" % (k, v)  for k, v in params.items())
    url = "http://en.wikipedia.org/w/api.php?%s" % qs
    wikisoup = BeautifulSoup(urllib2.urlopen(url))
    for pattern in redirect_re:
        match = re.search(pattern, str(wikisoup))
        if match:
            match = match.group()
            begin = match.find('[[')
            end = match.find(']]')
            titles = match[begin + 2:end]
            print 'Redirecting to {0}...\n'.format(titles)
            titles = titles.replace(" ", "%20")
            params = { "format":"xml", "action":"query", "titles":titles,
                      "prop":"revisions", "rvprop":"content", "rvsection":"0" }
            qs = "&".join("%s=%s" % (k, v)  for k, v in params.items())
            url = "http://en.wikipedia.org/w/api.php?%s" % qs
            wikisoup = BeautifulSoup(urllib2.urlopen(url))
    if str(wikisoup.find('pages')).find('page missing') != -1:
        print '''Page for "{0}" not found'''.format(titles.replace("%20", " "))
    else:
        wikipage = str(wikisoup.find('pages').text.encode('utf-8', 'ignore'))
        infobox = ''        
        for pattern in infobox_re:
            match = re.search(pattern, wikipage)
            if match:
                infobox = match.group()
                end = match.end()
        pagemaintext = wikipage[end:]
    
    return (wikipage, pagemaintext, infobox)
    


def get_wiki_score(titles):
    '''Gets album review scores from wiki and standardizes them to a 10 point scale.
    TODO!
    '''
    titles = titles.replace(" ", "%20")
    params = { "format":"xml", "action":"query", "titles":titles, "prop":"revisions",
              "rvprop":"content", "rvsection":"3" }
    q = "&".join("%s=%s" % (k, v)  for k, v in params.items())
    url = "http://en.wikipedia.org/w/api.php?%s" % q
    wikisoup = BeautifulSoup(urllib2.urlopen(url))
    if str(wikisoup.find('pages')).find('page missing') != -1:
        print '''Page for "{0}" not found'''.format(titles.replace("%20", " "))
    else:
        wikipage = str(wikisoup.find('pages').text.encode('ascii', 'ignore'))
        start = wikipage.find("rev1Score")
        end = wikipage.find("\n", start)
    print wikipage
    
    
def get_wiki_all(titles):
    return get_wiki(titles)[0]

def get_wiki_maintext(titles):
    '''Fetches only the prose part of wikipedia article 'titles' rvsection 0
    TODO:
    -Fix this (right now it only looks for '}}' to signal end of infobox.'''
    return get_wiki(titles)[1]
    
def get_wiki_infobox(titles):
    '''Creates a dictionary from the wikipedia infobox
    TODO!
    '''
    return get_wiki(titles)[2]
    '''print in_lines
    info_Dict = [line.replace("|", "") for line in in_lines
                 if line.startswith("|")]
    
    return info_Dict
    '''
    
def make_speakable(text):
    '''Removes all the markup &c that shouldn't be said by the announcer;
    TODO:
    -Limit the maximum length of text by cutting it off at the end of sentence
        or preferrably paragraph.
    '''
    return clean_html(text)

if __name__ == '__main__':
    print make_speakable(get_wiki_maintext("Sgt. Pepper"))
    #print clean_html(get_wiki_all("Sgt.%20Pepper's%20Lonely%20Hearts%20Club%20Band"))