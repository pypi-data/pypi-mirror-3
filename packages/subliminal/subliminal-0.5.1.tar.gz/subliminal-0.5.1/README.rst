Subliminal
==========
Subliminal is a python library to search and download subtitles.

It uses video hashes and the powerful `guessit <http://guessit.readthedocs.org/>`_ library
that extracts informations from filenames or filepaths to ensure you have the best subtitles.
It also relies on `enzyme <https://github.com/Diaoul/enzyme>`_ to detect embedded subtitles
and avoid duplicates.

Features
--------
Multiple subtitles services are available:

* OpenSubtitles
* TheSubDB
* BierDopje
* SubsWiki
* Subtitulos

You can use main subliminal's functions with a **file path**, a **file name** or a **folder path**.

CLI
^^^
Download english subtitles::

    $ subliminal -l en The.Big.Bang.Theory.S05E18.HDTV.x264-LOL.mp4
    **************************************************
    Downloaded 1 subtitles
    (Episode(u'The.Big.Bang.Theory.S05E18.HDTV.x264-LOL.mp4'), ResultSubtitle(en, opensubtitles, 0.33, The.Big.Bang.Theory.S05E18.HDTV-LOL.srt))
    **************************************************

Module
^^^^^^
List english subtitles::

    >>> subliminal.list_subtitles('The.Big.Bang.Theory.S05E18.HDTV.x264-LOL.mp4', ['en'])

Multi-threaded use
^^^^^^^^^^^^^^^^^^
Use 4 workers to achieve the same result::

    >>> with subliminal.Pool(4) as p:
    ...     p.list_subtitles('The.Big.Bang.Theory.S05E18.HDTV.x264-LOL.mp4', ['en'])
