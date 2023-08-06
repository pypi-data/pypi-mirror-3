Source checking/linting tool
----------------------------

It's easy to use.

Import the package yuou want to check:

  >>> import refline.srccheck

Import the checker:

  >>> from refline.srccheck.checker import checker

Run the checks.
It will pinpoint the problems found.

  >>> c = checker(refline.srccheck)
  >>> c.run()
  <BLANKLINE>
  testing/bad.py
  --------------
    Tab found in file
  <BLANKLINE>
  testing/bad.py
  --------------
    undefined name 'bar'
    6:     foo = bar


Just in case you cannot / do not want to avoid those problems,
fix them in the doctest as above.

To ignore files:

- With the string `checker_ignore_this_file` in the file

- With the checker `ignoreFiles` parameter

- With `##ignore PyflakesChecker##` in the file