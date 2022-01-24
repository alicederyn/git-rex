git re-execute
==============

Alternative to git cherry-pick that finds and runs commands in the commit message, instead of reapplying the original diff. This allows authors to document automated code steps, and then reapply the code if a simple rebase fails.

[![Validation status page](https://github.com/alicederyn/git-rex/actions/workflows/validation.yml/badge.svg?branch=main)](https://github.com/alicederyn/git-rex/actions/workflows/validation.yml?query=branch%3Amain)

For instance, suppose `git rebase -i` gives the following script:

```
pick 151779 Add new feature
pick 2332c1 Automatic code reformatting
```

To amend the first commit and, once done, automatically rerun the script from the second, just change the rebase script to:

```
edit 151779 Add new feature
x git rex 2332c1 # Automatic code reformatting
```

Note that rex only supports scripts in a [Markdown fenced code block] with
[bash syntax highlighting]:

````
Automatic code reformatting

Reformat all code with black

```bash
# Code to execute needs to go in a section like this in your commit message
poetry run black .
```
````

[Markdown fenced code block]: https://www.markdownguide.org/extended-syntax/#fenced-code-blocks
[bash syntax highlighting]: https://www.markdownguide.org/extended-syntax/#syntax-highlighting


Forwards-compatibility
----------------------

git-rex is currently in pre-release state, meaning **there is no guarantee that commits that work with one version will work with the next**. In particular, the following hold, but will not in future releases:

* The script currently runs in whichever directory you happen to be in when you run git-rex ([#1]). The intent is for scripts to consistently run at the root of the repository. Until this is done, please run git-rex at the root of your repository.
* Each line of a script section is currently run in a separate bash shell ([#2]), meaning global changes (like environment variables, or the current directory) will not propagate from one line to the next. The intent is for each code *block* to execute in a fresh shell. If you want to write forwards-compatible scripts, but need to change directory in your script, put your script line into a subshell by wrapping it in brackets.
* git-rex actually uses `/bin/sh` at the moment, not bash ([#3]).

[#1]: https://github.com/alicederyn/git-rex/issues/1
[#2]: https://github.com/alicederyn/git-rex/issues/2
[#3]: https://github.com/alicederyn/git-rex/issues/3


Installing
----------

To install, use [pipx]:

```bash
pip install pipx
export PATH="$PATH:$HOME/.local/bin"
pipx install git+https://github.com/alicederyn/git-rex.git
```

[pipx]: https://pipxproject.github.io/pipx/
