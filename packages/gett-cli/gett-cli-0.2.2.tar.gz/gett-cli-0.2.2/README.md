# What is it?

This tool is a simple command-line interface to the [ge.tt](http://ge.tt/)
file sharing website.
You can use it to upload files, list and create shares and delete those.

One of the advantages of ge.tt over other sharing websites is that you don't
need to wait for the uploading process to end to be able to share a file
with others. Your file gets a link as soon as it starts uploading, and others
will be able to download it while it's uploading.

Every file is part of share, which can contain several of them.
Shares can have a custom title, and are identified by an URL in the form of
`http://ge.tt/share_name`

Here is an example of what it looks like when uploading files:

    --------------------------------------------------------------------------------
    Share: Untitled (7 file(s)) [http://ge.tt/8ExGXpA]
    --------------------------------------------------------------------------------
    - distribute_setup.py             15.76 KB  http://ge.tt/8ExGXpA/v/1  remote
    - COPYING                          7.65 KB  http://ge.tt/8ExGXpA/v/0  remote
    - gett_uploader.py                 9.17 KB  http://ge.tt/8ExGXpA/v/3  remote
    - gett.py                          7.36 KB  http://ge.tt/8ExGXpA/v/2  remote
    - README.md                        2.02 KB  http://ge.tt/8ExGXpA/v/5  remote
    - MANIFEST.in                     13.00  B  http://ge.tt/8ExGXpA/v/4  remote
    - setup.py                       539.00  B  http://ge.tt/8ExGXpA/v/6  remote

    COPYING         (1/7) [##################################################] 100 %
    distribute...py (2/7) [##################################################] 100 %
    gett.py         (3/7) [##################################################] 100 %
    gett_uploa...py (4/7) [##################################################] 100 %
    MANIFEST.in     (5/7) [##################################################] 100 %
    README.md       (6/7) [##################################################] 100 %
    setup.py        (7/7) [##################################################] 100 %

    Storage used: 316.30 KB out of 2.00 GB (0 %)

# Installation

To use this tool, you need to have __Python 3__ installed:

- If you're using Windows you can download it from
  [python.org](http://python.org/download/)
  Please make sure to pick Python 3.x and not Python 2.x!

- For apt-get-based Linux distributions (such as Debian or Ubuntu),
  you can install it with:
  `$ apt-get install python3`

You then need to install gett-cli (this will provide the `gett` command):

- on Windows, use the provided MSI Installer:
    - for Python 3.1, use [this one](https://bitbucket.org/mickael9/gett-cli/downloads/gett-cli-0.2.2.win32-py3.1.msi)
    - for Python 3.2, use [this one](https://bitbucket.org/mickael9/gett-cli/downloads/gett-cli-0.2.2.win32-py3.2.msi)
- on other systems, you can simply use `pip` if you have it:
  `$ pip install gett-cli`
  alternatively, you can download the [source tarball](https://bitbucket.org/mickael9/gett-cli/get/v0.2.2.tar.bz2)
  and run
  `$ python3 setup.py install` (you might need to substitute `python3` to `python`
   if python3 is the default interpreter)

That's it!

# Usage examples

Uploading files to a new share:

    $ gett hello.jpg image2.png


Uploading files to an existing share:

    $ gett -s http://ge.tt/share_name hello.jpg image2.png


Listing your shares:

    $ gett --list


Deleting a share:

    $ gett --delete http://ge.tt/share_name


Deleting a file:

    $ gett --delete http://ge.tt/share_name/v/0


Note that whenever `http://ge.tt/<share_name>[/v/<fileid>]` is expected,
you can omit the `http://ge.tt/` part:

    $ gett --delete share_name/v/0


You can see all the available options with:

    $ gett --help
