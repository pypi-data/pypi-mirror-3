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

* Implement annotated tiles for sequence moves.
* Implement annotated tiles for marked stones.
* Implement diagram captions and metadata.

.. _Sensei's Library: http://senseis.xmp.net/?HowDiagramsWork
