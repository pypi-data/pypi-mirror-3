######
README
######

rstgo is a package for parsing go diagrams of the style used at the 
`Sensei's Library`_ and rendering them using reStructuredText.  It was 
designed for embedding dynamically generated images of go games into reST 
documents, particularly for pelican blogs or sphinx documentation.  

The code lives at http://bitbucket.org/cliff/rstgo.  Bug reports, feature
requests, and contributions are all welcome.  If you find the code useful,
hop on bitbucket and send me a quick message letting me know.

To use with sphinx, add 'rstgo.rst' to your list of extensions.  

To use with pelican, add the following to your pelican configuration file

    from rstgo import rst
    rst.setup_pelican()
    

Changelog
=========

0.1.6 -- 2011/
-------------------

* Sequence moves can now start with either black or white.
* Refactored parser a little bit.


0.1.5 -- 2011/11/05
-------------------

Implemented rendering of sequence moves and letter annotations.  Currently,
sequence moves have to start with black


0.1.4 -- 2011/11/04
-------------------

Fixed a bug where ``:alt:`` argument was unintentionally required.


0.1.3 -- 2011/11/03
-------------------

Fixed pathing and extension loading for usage with Sphinx.


0.1.2 -- 2011/10/27
-------------------

Added release notes to README.txt 


0.1.1 -- 2011/10/27
-------------------

Added intro text to README.txt 


0.1.0 -- 2011/10/27
-------------------

Initial release


To Do
=====

* Diagrams should render captions and metadata.
* Sequences should accept starting numbers > 1.
* Non-alphanumeric annotations should work as described in the `Sensei's Library`_.
* Numbering should accept other fonts and use a condensed font for numbers
  above 9 (or 20, or whenever it gets too wide).
* If condensed fonts are still too big, it should dynamically resize itself.


.. _Sensei's Library: http://senseis.xmp.net/?HowDiagramsWork
