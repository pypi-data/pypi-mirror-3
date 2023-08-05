#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A command-line interface to cuevanaapi
"""

import os
import sys
import subprocess
from multiprocessing import Process

import plac

from . import __version__
import cuevanalib.cuevanaapi as cuevanaapi
from cuevanalib.downloaders import (megaupload, NotValidMegauploadLink,
                                    NotAvailableMegauploadContent,
                                    smart_urlretrieve)

from ConfigParser import SafeConfigParser

APP_DATA_DIR = os.path.join(os.path.expanduser("~"), '.cuevanalinks')
CONFIG_FILE = os.path.join(APP_DATA_DIR, 'config.ini')

@plac.annotations(
    title=("Look for a movie or show with this title or URL. "
           "If it's not an URL and `episode` is empty "
           "a movie is assummed", 'positional'),
    episode=('Specifies a season/episode of a show. \n'
             'Examples: S01 (a whole season), s02e04, 1x4 \n'
             'If `end` is given retrieve the slices including limits',
             'positional'),
    end=('Specifies the end of season/episode slices (including it). \n'
             'Examples: S01 (a whole season), s02e04, 1x4',
             'positional'),

    download=("Download the contents instead show links",
                "flag", 'd'),
    play = ("Play while download. This automatically buffer enough data "
            "before call the player. It's possible define the player command "
            "in the config file", 'flag', 'p'),
    subs=("Download subtitles (if available)", 'flag', 's'),
    language=("Define the language of subtitles. Default: 'es'", 'option',
            'l', str, ('es', 'en', 'pt'), '{es, en, pt}'),
    max_rate=("Max File transfer rate (in kbps)", 'option', 'r'))
def cli(title, subs, download, play, episode='', end='', language='es',
                                                    max_rate=None):

    config = get_config()
    format = config.get('main', 'file_format')

    if play:
        download = True

    def get_or_print(content):
        """auxiliar function to practice DRY principle"""

        if subs:
            try:
                smart_urlretrieve(content.subs[language],
                               content.filename(format=format), content.url)
            except KeyError:
                print 'There is not subtitles available (at least in this language)'

        if not download:
            print content.get_links()
        else:
            print "Found %s" % content.pretty_title
            #FIX ME . always the first one?
            mu_url = [link for link in content.sources if 'megaupload' in link][0]
            filename= content.filename(format=format, extension='mp4')

            if play:
                #prepare a subprocess callback to a player
                command_list = config.get('main', 'player').split()

                if '{file}' in command_list:
                    command_list[command_list.index('{file}')] = filename
                else:
                    command_list.append(filename)

                process = Process(target=background_process,
                                   args=(command_list,) )
                callback = process.start
            else:
               #no callback
               callback = process = None

            try:
                megaupload(mu_url, filename, callback, max_rate=max_rate)
                if process: process.join()
            except KeyboardInterrupt:
                #TODO clean up partial downloads ?
                sys.exit("\nDownload Interrumpted. See you!")
            except NotAvailableMegauploadContent:
                print "Megaupload hasn't this file available.\n" \
                      "on %s .\n" \
                      "You should report this using the link" \
                      " at the bottom of \n%s" % (mu_url, content.url)
                if len(content.sources) > 1:
                    msg = "\nAlso you could try download the file you request from"
                    if len(content.sources) == 2:
                        msg += "this alternative source:"
                    else:
                        msg += "these alternatives sources:"
                    print msg + '\n'
                    for link in content.sources[1:]:
                        print link
            except NotValidMegauploadLink:
                print "Not valid megaupload link given."
                print "This is embarrasing and shouldn't have happened." \
                      "Please, report this in " \
                      "https://bitbucket.org/tin_nqn/cuevanalinks/issues " \
                      "given some context (i.e: the command line you ran). Thanks"



    language =  language.upper()
    filter = None if not download else 'megaupload'
    api = cuevanaapi.CuevanaAPI(filter)

    if title.startswith(cuevanaapi.URL_BASE) and not episode :
        try:
            print "Retrieving '%s'...\n" % title
            content = cuevanaapi.dispatch(title)
            get_or_print(content)
        except cuevanaapi.NotValidURL:
            sys.exit("Not valid URL of a cuevana's movie/episode")
        except Exception, e:        #Fix me
            print e
            sys.exit("Cuevana has problem. Try in a few minutes")

    elif episode:
        backup_last_seen = os.path.join(APP_DATA_DIR, title + '.tmp')
        if os.path.exists(backup_last_seen):
            last_seen = api.load_pickle(open(backup_last_seen).read())
        else:
            last_seen = None

        if episode == 'next':
            print "Retrieving the next episode of '%s'...\n" % (title)
            if last_seen:
                get_or_print(last_seen.next)
            else:
                print "Unknow last seen episode for '%s'...\n" % (title)
        elif episode == 'again':
            print "Retrieving the last seen episode of '%s'...\n" % (title)
            if last_seen:
                get_or_print(last_seen)
            else:
                print "Unknow last seen episode for '%s'...\n" % (title)

        else:
            print "Searching '%s'...\n" % (title)
            try:
                show = api.get_show(title)
                if show:
                    episodes = show.get_episodes(episode, end)
                    for episode in episodes:
                        get_or_print(episode)
                    try:
                        backup_last_seen = os.path.join(APP_DATA_DIR, title + '.tmp')
                        with open(backup_last_seen, 'w') as backup:
                            backup.write(episode.get_pickle())
                    except ValueError:
                        print "There was a problem saving this as last seen episode. Skipped"
                else:
                    print "Nothing found for '%s'." % title

            except Exception, e:            #Fix me
                raise e
                #sys.exit("Cuevana server has problem. Try in a few minutes")

    else:
        #movie
        print "Searching '%s'...\n" % title
        try:
            results = api.search(title)
            if results:
                if isinstance(results[0], cuevanaapi.Show):
                    print "A show was found for '%s'. "\
                          "Try defining an episode/season" % title
                else:
                    get_or_print(results[0])

            #TODO order result by relevance as done with Shows ?
            #or (better) check len of results and turns interactive if are many
            else:
                print "Nothing found for '%s'." % title

        except Exception, e:        #FIX ME this is crap
            print e
            sys.exit("Cuevana.tv has a problem. Try in a few minutes")

cli.__doc__ = ("CuevanaLinks %s - 2011 Martin Gaitán\n"
              "A program to retrieve movies and series "
              "(or links to them) from cuevana.tv"
               % __version__ )

def get_config():
    """
    """

    DEFAULTS = { 'main': {
                    "player": "mplayer -fs {file}",
                    "file_format": "long",
                  # "download_dir_show": os.path.join( DEFAULT_PATH, "Videos",
                  #                                     "{show}", "{season}"),
                  # "download_dir_movie": os.path.join( DEFAULT_PATH, "Videos",
                  #                                     "{title}" ),
                        },
                }

    config = SafeConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print "There is no config file. Creating default %s" % CONFIG_FILE
        for section, options in DEFAULTS.items():
            for section, options in DEFAULTS.items():
                if not config.has_section(section):
                    config.add_section(section)
                for option, value in options.items():
                    config.set(section, option, value)

        if not os.path.exists(APP_DATA_DIR):
            os.makedirs(APP_DATA_DIR)   #make .cuevanalinks dir
        with open(CONFIG_FILE, 'w') as cfg:
            config.write(cfg)
    else:
        with open(CONFIG_FILE, 'r') as cfg:
            config.readfp(cfg)
    return config

def background_process(command_list):
    return subprocess.call(command_list)



def main():
    plac.call(cli)

if __name__ == "__main__":
    main()
