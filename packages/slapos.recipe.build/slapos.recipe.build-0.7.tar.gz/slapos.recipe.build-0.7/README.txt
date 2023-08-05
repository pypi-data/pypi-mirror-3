slapos.recipe.build
===================

Important notice
----------------

This is totally experimental recipe for fully flexible software "build".

Examples
--------

Recipe to build the software.

Example buildout::

  [buildout]
  parts =
    file

  [zlib]
  # Use standard configure, make, make install way
  recipe = slapos.recipe.build:cmmi
  url = http://prdownloads.sourceforge.net/libpng/zlib-1.2.5.tar.gz?download
  md5sum = c735eab2d659a96e5a594c9e8541ad63
  slapos_promise =
    directory:include
    file:include/zconf.h
    file:include/zlib.h
    directory:lib
    statlib:lib/libz.a
    dynlib:lib/libz.so linked:libc.so.6 rpath:
    dynlib:lib/libz.so.1 linked:libc.so.6 rpath:
    dynlib:lib/libz.so.1.2.5 linked:libc.so.6
    directory:lib/pkgconfig
    file:lib/pkgconfig/zlib.pc
    directory:share
    directory:share/man
    directory:share/man/man3
    file:share/man/man3/zlib.3

  [file]
  recipe = slapos.recipe.build:cmmi
  url = ftp://ftp.astron.com/pub/file/file-5.04.tar.gz
  md5sum = accade81ff1cc774904b47c72c8aeea0
  environment =
    CPPFLAGS=-I${zlib:location}/include
    LDFLAGS=-L${zlib:location}/lib -Wl,-rpath -Wl,${zlib:location}/lib
  slapos_promise =
    directory:bin
    dynlib:bin/file linked:libz.so.1,libc.so.6,libmagic.so.1 rpath:${zlib:location}/lib,!/lib
    directory:include
    file:include/magic.h
    directory:lib
    statlib:lib/libmagic.a
    statlib:lib/libmagic.la
    dynlib:lib/libmagic.so linked:libz.so.1,libc.so.6 rpath:${zlib:location}/lib
    dynlib:lib/libmagic.so.1 linked:libz.so.1,libc.so.6 rpath:${zlib:location}/lib
    dynlib:lib/libmagic.so.1.0.0 linked:libz.so.1,libc.so.6 rpath:${zlib:location}/lib
    directory:share
    directory:share/man
    directory:share/man/man1
    file:share/man/man1/file.1
    directory:share/man/man3
    file:share/man/man3/libmagic.3
    directory:share/man/man4
    file:share/man/man4/magic.4
    directory:share/man/man5
    directory:share/misc
    file:share/misc/magic.mgc

  [somethingelse]
  # default way with using script
  recipe = slapos.recipe.build
  url_0 = http://host/path/file.tar.gz
  md5sum = 9631070eac74f92a812d4785a84d1b4e
  script =
    import os
    os.chdir(%(work_directory)s)
    unpack(%(url_0), strip_path=True)
    execute('make')
    execute('make install DEST=%(location)s')
  slapos_promise =
    ...

  [with_patches]
  recipe = slapos.recipe.build:cmmi
  md5sum = 1b845a983a50b8dec0169ac48479eacc
  url = http://downloads.sourceforge.net/project/w3m/w3m/w3m-0.5.3/w3m-0.5.3.tar.gz
  configure-options =
    --disable-nls
    --disable-image
    --disable-dict
    --disable-xface
    --disable-mouse
    --disable-nntp
    --disable-help-cgi
    --disable-external-uri-loader
    --disable-w3mmailer

  # default patch options
  patch-options =
    -p1

  # patches can be local files, then can have (optional) md5sum, they can have
  # own options added
  patches =
    /path/to/local/file
    /path/to/local/file2 75422a6f7f671b3a6d9add6724cc0945
    http://downloaded/ 75422a6f7f671b3a6d9add6724cc0945
    http://download/ uNkNoWn -p8
    http://downloaded2/ 75422a6f7f671b3a6d9add6724cc0945 -p2


  [multiarchitecture]
  recipe = slapos.recipe.build
  slapos_promise =
    ...
  x86 = http://host/path/x86.zip [md5sum]
  x86-64 =  http://host/path/x64.zip [md5sum]
  script =
    if not self.options.get('url'): self.options['url'], self.options['md5sum'] = self.options[guessPlatform()].split(' ')
    extract_dir = self.extract(self.download(self.options['url'], self.options.get('md5sum')))
    workdir = guessworkdir(extract_dir)
    self.copyTree(workdir, "%(location)s")

TODO:

 * add linking suport, buildout definition:

slapos_link = <relative/path> [optional-path]

can be used as::

  [file]
  slapos_link =
    bin/file
    bin/file ${buildout:bin-directory}/bin/anotherfile

Which will link ${file:location}/bin/file to ${buildout:bin-directory}/bin/file
and ${file:location}/bin/file to ${buildout:bin-directory}/bin/anotherfile

Pure download
-------------

::

  [buildout]
  parts =
    download

  [download]
  recipe = slapos.recipe.build:download
  url = https://some.url/file

Such profile will download https://some.url/file and put it in
buildout:parts-directory/download/download

filename parameter can be used to change destination named filename.

destination parameter allows to put explicit destination.

md5sum parameter allows pass md5sum.

mode (octal, so for rw-r--r-- use 0644) allows to set mode

Exposes target attribute which is path to downloaded file.

Notes
-----

This recipe suffers from buildout download utility issue, which will do not
try to redownload resource with wrong md5sum.

