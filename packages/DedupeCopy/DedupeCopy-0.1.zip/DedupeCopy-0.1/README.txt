Find duplicates / copy and restructure file layout command-line tool.

This is a simple multi-threaded file copy tool designed for consolidating and
restructuring sprawling file systems.

The most common use case is for backing up data into a new layout, ignoring
duplicated files.

Other uses include:
  1. Getting a .csv file describing all duplicated files
  2. Comparing different file systems
  3. Restructuring existing sets of files into different layouts (such as
    sorted by extension or last modification time)

This tool is *NOT* a Robocopy or rsync replacement and does not try to fill
the role those play.

As with all code that walks a file tree, please use with caution and expect
absolutely no warranty! :)

This project is on bitbucket: http://www.bitbucket.org/othererik/dedupe_copy
