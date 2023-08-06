.. _news:

News/Changelog
==============

1.0.0 (2012-02-04)
------------------

- Reimplemented existing functionality in Cython.
- Added renderer classes for customized Markdown rendering (like Redcarpet has).
- Updated Sundown files; See commits from Aug 20, 2011 to Jan 27, 2012:
  https://github.com/tanoku/sundown/commits/master/


0.4.2 (2011-08-25)
------------------

- Updated Sundown files; See commits from 2011-08-03 to 2011-08-09:
  https://github.com/tanoku/sundown/commits/master/


0.4.1 (2011-08-01)
------------------

- Fixed buffer management. It was broken and leaked memory. (tanoku)
- Updated Sundown files; See commits from 2011-07-29 to 2011-08-01:
  https://github.com/tanoku/sundown/commits/master/


0.4.0 (2011-07-25)
------------------

- API change: `misaka.toc` has been removed. Instead `HTML_TOC_TREE` has to be
  passed with `misaka.html` to get a TOC tree. When `HTML_TOC` is used the
  text will be rendered as usual, but the header HTML will be adjusted for the
  TOC.
- Updated Sundown files; See commits from 2011-07-22 to 2011-07-24:
  https://github.com/tanoku/sundown/commits/master/
- Added support for the Superscript extension.


0.3.3 (2011-07-22)
------------------

- Fix a typo in README.txt. (heintz)
- Fix non-NULL-terminated `kwlist` in `misaka_html`. (heintz)
- Rename pantyshot to misaka in benchmark.py. (honza)
- Renamed Upskirt to Sundown and updated the source files from 2011-07-04
  to 2011-07-19: https://github.com/tanoku/sundown/commits/master


0.3.2 (2011-07-03)
------------------

- Fixed minor error in setup.py.


0.3.1 (2011-07-03)
------------------

- Renamed Pantyshot to Misaka.
- Updated Upskirt files; See commits from 2011-06-06 to 2011-06-23:
  https://github.com/tanoku/upskirt/commits/master/


0.3.0 (2011-06-16)
------------------

- Added Python 3 support.
- Updated Upskirt files; See commits from 2011-06-05 to 2011-06-09:
  https://github.com/tanoku/upskirt/commits/master/


0.2.1 (2011-06-05)
------------------

- Updated Upskirt files; See commits from 2011-05-18 to 2011-06-02:
   https://github.com/tanoku/upskirt/commits/master/


0.2.0 (2011-05-17)
------------------

- Added Smartypants render flag.
- Added a `toc` function that outputs a table of contents.
- Renamed `markdown` function to `html`.
- Updated Upskirt files; See commits from 2011-05-02 to 2011-05-17:
  https://github.com/tanoku/upskirt/commits/master/


0.1.1 (2011-05-01)
------------------

- Updated Upskirt files; a HTML escaping bug in the XHTML renderer was fixed.


0.1.0 (2011-05-01)
------------------

- Initial release.
