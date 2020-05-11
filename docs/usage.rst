=====
Usage
=====

To use Music Full Tag Downloader in terminal:

1. Get the `MID` of singer/album/song, witch is used to download songs :
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    $ musicftdl search <KEYWORD1 KEYWORD2 ...>

2. (Optional) Get more information about a singer/album/song:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* List albums of a singer, or list songs of an album :

.. code-block:: console

    $  musicftdl list <SINGER_MID | ALBUM_MID>

* Show information of a song :

.. code-block:: console

    $  musicftdl show <SONG_MID>

3. Download songs:
^^^^^^^^^^^^^^^^^^

* Download a song by it's song_mid :

.. code-block:: console

    $ musicftdl download <SONG_MID>

* Download the first song in the results by searching for some keywords :

.. code-block:: console

    $ musicftdl download -k <KEYWORD | "KEYWORD1 KEYWORD2 ...">

Note: multiple keywords should be quoted as `"KEYWORD1 KEYWORD2 ..."`.

* Download all songs of a singer by it's singer_mid :

.. code-block:: console

    $ musicftdl download -s <SINGER_MID>

* Download all songs of an album by it's album_mid :

.. code-block:: console

    $ musicftdl download -a <ALBUM_MID>

You can get the download options by typing `musicftdl download --help` in ternimal :

.. code-block:: none

    Usage: musicftdl download [OPTIONS] RESOURCE

      Download songs by SINGER/ALBUM MID or KEYWORDS.

    Options:
      -s, --singer                    Download songs by SINGER_MID.
      -a, --album                     Download songs by ALBUM_MID.
      -k, --keywords                  Download song by searching keywords.
      -o, --overwrite                 Overwrite exist files.
      -d, --destination TEXT          Destination to save songs.
      -n, --name-style [1|2|3]        Style of filename. [ 1: SONG.ext | 2: SINGER
                                      - SONG.ext | 3: SINGER - ALBUM - SONG.ext
                                      [default: 3]
      -t, --album_types TEXT          Download songs of selected types of albums.
                                      [ S: Studio Album | E: EP Single | L: Live
                                      Album | O: Others ]  [default: SELO]
      -c, --classified / -C, --no-classified
                                      Store in folders classify by singers and
                                      albums.  [default: True]
      -f, --format [128|320|m4a|flac|ape]
                                      Song format.  [default: 128]
      -P, --page INTEGER              Page No.  [default: 1]
      -S, --page-size INTEGER         Page size.  [default: 50]
      --help                          Show this message and exit.


Here is an example for download all `周杰伦's` songs with `320k` bitrate, and save to the directory of `/mnt/e/Music/musicftdl` :

.. code-block:: console

    $ musicftdl download -d /mnt/e/Music/musicftdl -f 320 -s 0025NhlN2yWrP4
