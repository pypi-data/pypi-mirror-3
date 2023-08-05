PyMDECO - Python Meta Data Extractor and Collection Organizer
=============================================================

PyMDECO is a library which aims to facilitate the metadata extraction,
storage and manipulation of a large collection of photos and multimedia
(audio and video) files.
Rather than developing own metadata parsers for the multitude of file
types, it depends on third-party libraries and tools to extract the
metadata from the files.


Example usage
--------------

Example with a video file:

    >>> from pymdeco import services
    >>> srv = services.FileMetadataService()
    >>> meta = srv.get_metadata('/tests/big_buck_bunny_720p_surround.avi')
    >>> import json
    >>> print json.dumps(meta, indent=2) # to pretty print the metadata
    {
      "file_name": "big_buck_bunny_720p_surround.avi",
      "file_type": "video",
      "file_size": 332243668,
      "mime_type": "video/x-msvideo",
      "file_hash": {
        "value": "b957d6e6212638441b52d3b620af157cc8d40c2a0342669294854a06edcd528c",
        "algorithm": "sha256"
      },
      "file_timestamps": {
        "modified": "2008-06-11 13:29:26",
        "created": "2008-06-13 21:13:00"
      },
      "video_metadata": {
        "streams": [
          {
            "sample_aspect_ratio": "1:1",
            "codec_type": "video",
            "codec_name": "mpeg4",
            "duration": "596.457",
            "nb_frames": "14315",
            "codec_time_base": "1/24",
            "index": 0,
            "width": 1280,
            "divx_packed": "0",
            "pix_fmt": "yuv420p",
    ... # output truncated


Example with an audio file:

    >>> from pymdeco import services
    >>> srv = services.FileMetadataService()
    >>> meta = srv.get_metadata('/tests/jonobacon-freesoftwaresong2.mp3')
    >>> import json
    >>> print(json.dumps(meta, indent=2)) # to pretty print the metadata
    {
      "file_name": "jonobacon-freesoftwaresong2.mp3",
      "file_type": "audio",
      "file_size": 3169160,
      "mime_type": "audio/mpeg",
      "file_hash": {
        "value": "d7ebc161d5d8fb802659fea949204af2958906b91913ca7577cfaeece90ffb78",
        "algorithm": "sha256"
      },
      "file_timestamps": {
        "modified": "2012-01-09 20:02:23",
        "created": "2012-01-09 20:02:23"
      },
      "audio_metadata": {
        "streams": [
          {
            "index": 0,
            "sample_fmt": "s16",
            "codec_tag": "0x0000",
            "bits_per_sample": 0,
            "r_frame_rate": "0/0",
            "start_time": "0.000",
            "time_base": "1/14112000",
            "codec_tag_string": "[0][0][0][0]",
            "codec_type": "audio",
            "channels": 2,
            "codec_long_name": "MP3 (MPEG audio layer 3)",
            "codec_name": "mp3",
    ... # output truncated

Example with an image file:

    >>> from pymdeco import services
    >>> srv = services.FileMetadataService()
    >>> meta = srv.get_metadata('/tests/some_image.jpg')
    >>> print(json.dumps(meta, indent=2)) # to pretty print the metadata
    {
      "file_name": "some_image.jpg",
      "file_type": "image",
      "file_size": 159894,
      "mime_type": "image/jpeg",
      "file_hash": {
        "value": "844a8750f2c9e1a24175c8f158abb6d204ec2b79fc49aba512cded3cdb3a0111",
        "algorithm": "sha256"
      },
      "file_timestamps": {
        "modified": "2012-01-09 20:43:12",
        "created": "2012-01-09 20:43:12"
      },
      "image_metadata": {
        "Exif": {
          "Photo": {
            "LightSource": 0,
            "PixelXDimension": 900,
            "SubSecTime": "16",
    ... # output truncated ... Image details follow
    "Image": {
            "YResolution": 72,
            "ResolutionUnit": 2,
            "Orientation": 1,
            "Copyright": "Some Rights Reserved                                  ",
            "Artist": "Yovko Lambrev                       ",
            "Make": "NIKON CORPORATION",
            "DateTime": "2008-09-13 11:26:41",
    ... # output truncated ... XMP details follow
        "Xmp": {
          "iptc": {
            "CreatorContactInfo/Iptc4xmpCore:CiEmailWork": "yovko@simplestudio.org",
            "CreatorContactInfo/Iptc4xmpCore:CiAdrCity": "Sofia",
            "CreatorContactInfo/Iptc4xmpCore:CiUrlWork": "http://simplestudio.org",
    ... # output truncated ... IPTC tags follow
        "Iptc": {
          "Application2": {
            "CountryName": "['Bulgaria']",
            "Byline": "['Yovko Lambrev']",
            "BylineTitle": "['Photographer']",
    ... # output truncated

Example with a binary file:

    >>> from pymdeco import services
    >>> srv = services.FileMetadataService()
    >>> meta = srv.get_metadata('/tests/minimal_ubuntu_11.04_natty.iso')
    >>> import json
    >>> print (json.dumps(meta, indent=2))
    {
      "file_name": "minimal_ubuntu_11.04_natty.iso",
      "file_type": "application",
      "file_size": 19922944,
      "mime_type": "application/x-iso9660-image",
      "file_hash": {
        "value": "8607e2c06090db13b06a216efbeb65d7aeff4ca8666904e6874cf4a5960f2366",
        "algorithm": "sha256"
      },
      "file_timestamps": {
        "modified": "2011-05-02 17:24:18",
        "created": "2011-05-02 17:24:18"
      }
    }


.. _installation_reference:

Installation and building documentation
========================================

Getting the latest development version:

    :command:`hg clone https://bitbucket.org/todor/pymdeco`


Installing from source:

    :command:`python setup.py install`


Generating the HTML documentation:

    :command:`python setup.py build_doc`


If the installation is successfull the following code can be used to
confirm the installation is ok and all dependencies are present:

Checking dependencies:

    >>> from pymdeco.utils import check_dependencies
    >>> print json.dumps(check_dependencies(), indent=2)
    {
      "pyexiv2": "pyexiv2: 0.3.2",
      "ffprobe": "/usr/bin/ffprobe"
    }

If any of the dictionary values are None, then PyMDECO is unable to find
some of the dependencies.


.. _dependencies_reference:

Dependencies
-------------

*   Python 2.7+ or Python 3.2+
*   `pyxeiv2 <http://tilloy.net/dev/pyexiv2/>`_ library (which is the Python
    bidnings to `exiv2 <http://exiv2.org/>`_). It is used to extract
    `EXIF <http://en.wikipedia.org/wiki/Exchangeable_image_file_format>`_,
    `XMP <http://en.wikipedia.org/wiki/Extensible_Metadata_Platform>`_ and
    `IPTC <http://en.wikipedia.org/wiki/Extensible_Metadata_Platform>`_
    tags from photos and images (JPEG, PNG, GIF, etc).
*   :program:`ffprobe` binary (from `ffmpeg suite <http://ffmpeg.org/>`_)
    (version 0.9.0 or later) located in the system's :envvar:`PATH`.
    Older versions of the :program:`ffprobe` (prior 0.9.x) cannot
    output in JSON format.
*   Sphinx (>= 1.0.0) - for building the documentation

.. note::

    After the installation of the library one please ensure that
    :program:`ffprobe` executable is installed and available to the library
    (the executable file must be available in one of the directories listed in
    :envvar:`PATH` environmental variable.

    Refer to *ffmpeg* download page on the best way to install ffmpeg suite
    (which :program:`ffprobe` is part of):
    `http://ffmpeg.org/download.html <http://ffmpeg.org/download.html>`_.
    Under Windows it is recommended to use the static version of the program.


Tutorial
========

Assuming that all external dependencies have been satisfied (see
:ref:`dependencies_reference` section for details) the easiest way to use
the library is to instantiate a service from :mod:`pymdeco.services` module:

    Example:

        >>> import os, json
        >>> from pymdeco.services import FileMetadataService
        >>> srv = FileMetadataService()
        >>> for root, dirs, files in os.walk(r'/some/multimedia/files/'):
        ...   for afile in files:
        ...     meta = srv.get_metadata(os.path.join(root,afile))
        ...     print(json.dumps(meta, indent=2)) # to prettify the output
        ...
        # long prinout of metadata in nested dictionaries

In PyMDECO, there is a separation between the various components for
extracting metadata:

* *Extractors* - The low-level functions which call the third-party libraries
  or invoke the external executable programs and parse their output. These
  functions expect the third-party libraries and tool to be present on the
  system, otherwise they won't work.

* *Scanners* - Mid-level classes which can perform additional checks during
  the initializations and identify, load and check for the external
  dependencies and/or provide alternatives if they are not present.
  Scanners usually specialize in the extraction of only certain type of
  files i.e. only in audio or only in image metadata extraction.

* *Services* - High-level classes which can combine multiple scanners to allow
  scanning of different types files. They also provide fall-back method if
  some of the scanners can not work due to missing dependencies.

Each of these class of components sit in their own module. There is a clear
separation of the of their duties and the components from a module only know
and use the classes from the lower layers i.e.:
*Services only use Scanners. Scanners only use Extractors.*

Each Service and Scanner use the file's MIME
(`Multipurpose Internet Mail Extensions <http://en.wikipedia.org/wiki/MIME>`_)
to identify what kind of data it is likely to contain and then runs the
appropriate function to get the metadata.

The Services are the most convenient way to extract data as they know which
Scanner to use for particular file type. However, sometimes the library user
may wish to exert more control over which Scanner class is used, so it is
possible to construct the service manually:

Example:

    >>> from pymdeco import scanners, services
    >>> ais = scanners.AudioInfoScanner() # using the default MIME 'audio/*'
    >>> ais.pre_checks() # see API documentation for details
    >>> srv = services.FileMetadataService(scanners_list=[ais]) # using the default scanner for */*
    >>> srv.available_scanners()
    {'*/*': <pymdeco.scanners.FileInfoScanner object at 0x02A76A30>, \
    'audio/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>}
    >>> vis = scanners.VideoInfoScanner()
    >>> vis.pre_checks()
    >>> srv.register_scanner("video/mpeg", vis) # registering with specific MIME
    >>> srv.available_scanners()
    {'video/mpeg': <pymdeco.scanners.VideoInfoScanner object at 0x02A76A90>, \
    '*/*': <pymdeco.scanners.FileInfoScanner object at 0x02A76A30>, \
    'audio/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>}
    >>> srv.set_default_scanner(ais)
    >>> srv.available_scanners()
    {'video/mpeg': <pymdeco.scanners.VideoInfoScanner object at 0x02A76A90>, \
    '*/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>, \
    'audio/*': <pymdeco.scanners.AudioInfoScanner object at 0x02A768D0>}
    >>> meta = srv.get_metadata('/some/video/file.mpeg')
    >>> # do something with the metadata

Regardless of which method has been used to obtain the metadata, the
result is always a (nested) Python dictionary with keys - undescore separated
meaningfull descriptions of the metadata tag and values - either strings or
numbers.
The result can then easily be converted to JSON for transmission via HTTP or
stored to document-oriented database (like
`MongoDB <http://www.mongodb.org/>`_).


API documentation
-------------------

Downloading the source and building the documentation (see
:ref:`installation_reference` section) will create HTML version of the
API documentation.


History and future directions
=============================

The library was created out of necessity to manage large collection of photos
(tens of thousands) and video clips (many thousands) collected over a large
period of time from different sources and created by various models of
photo cameras, camcorders and webcams.

I quickly found out that to identify duplicates and effectively manage the
backups I needed good and reliable metadata handling and storage.
After experimenting with half a dozen Python packages and tools I settled
on building a common API which makes use of well-established third-party
libraries and external tools.

So far only the metadata extraction part has been mostly completed, but
development of some sort of persistent storage for that metadata is on the
roadmap (involving the usage of MongoDB or Sqlite as potential backends). This
persistent storage will be used to build collections with metadata and then
constructing queries like "is this file already in the collection", "is there
a *similar* file in the collection", "get all files with this metadata tag" or
"list all the files created by the same device on the same date as this file".

See TODO.txt for more details.


Getting involved
=================

This library is at early stage, but is already capable to do enough useful
metadata collection. If you are interested in improving it further and want
to get involved, please send a mail to **pymdeco at googlegroups dot com**.


License
=======

PyMDECO is licenced under GNU LGP (Lesser General Public License) version 3 or
later. For details please refer to LICENSE.txt included in the source
distribution.
