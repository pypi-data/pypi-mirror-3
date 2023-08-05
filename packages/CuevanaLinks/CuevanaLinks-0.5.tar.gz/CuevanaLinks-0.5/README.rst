************
Cuevanalinks
************

Cuevanalinks is a command line program to download, play or get links of contents
from cuevana.tv_ .

Documentation is in http://packages.python.org/CuevanaLinks

Source code and Issue Tracker: https://bitbucket.org/tin_nqn/cuevanalinks/

Dependecies
-----------

CuevanaLinks is based on top of cuevanalib_ . Also uses plac_ as command
line arguments parser. progressbar_ is used to give feedback while downloading.

Everything is available via `easy_install` or `pip`


.. _cuevana.tv: http://www.cuevana.tv
.. _cuevanalib: http://packages.python.org/cuevanalib
.. _plac: http://pypi.python.org/pypi/plac
.. _progressbar: http://pypi.python.org/pypi/progressbar

Example usage
-------------

- Get help::

    $ cuevanalinks -h
    usage: cuevanalinks [-h] [-s] [-d] [-p] [-l {es, en, pt}] [-r None]
                        title [episode] [end]

    CuevanaLinks 0.4 - 2011 Martin Gaitán
    A program to retrieve movies and series (or links to them) from cuevana.tv

    positional arguments:
      title                 Look for a movie or show with this title or URL. If
                            it's not an URL and `episode` is empty a movie is
                            assummed
      episode               Specifies a season/episode of a show. Examples: S01 (a
                            whole season), s02e04, 1x4 If `end` is given retrieve
                            the slices including limits
      end                   Specifies the end of season/episode slices (including
                            it). Examples: S01 (a whole season), s02e04, 1x4

    optional arguments:
      -h, --help            show this help message and exit
      -s, --subs            Download subtitles (if available)
      -d, --download        Download the contents instead show links
      -p, --play            Play while download. This automatically buffer enough
                            data before call the player. It's possible define the
                            player command in the config file
      -l {es, en, pt}, --language {es, en, pt}
                            Define the language of subtitles. Default: 'es'
      -r None, --max_rate None
                            Max File transfer rate (in kbps)


- Download *Black Swan*:

    $ cuevanalinks -d 'black swan'

- Retrieve URLs of one specific episode of a show::

    $ cuevanalinks house 4x10

- Download the complete 4th season of *Mad Men* and its subtitles (in spanish)::

    $ cuevanalinks -d -s 'mad men' s04

  Note that you can also handle downloads through Tucan ::

    $ cuevanalinks -s 'mad men' s04 > links.txt && tucan -d -i links.txt

- Retrieve links of 'Seinfeld' between s02e10 and the last one of 4th season
  limiting the filetransfer rate to 30kbps ::

    $ cuevanalinks -r 30 seinfeld s02e12 s04

- Retrieve URLs of *El secreto de sus ojos* (*The Secret in Their Eyes*) and
  download subtitles in english::

    $ cuevanalinks 'secreto de sus ojos' -s -l en
