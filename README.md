git rex
=======

Alternative to git cherry-pick that finds and runs commands in the commit message, instead of reapplying the original diff. This allows authors to document automated code steps, and then reapply the code if a simple rebase fails.

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


Installing
----------

To install, use [pipx]:

```bash
pip install pipx
export PATH="$PATH:$HOME/.local/bin"
pipx install git+https://github.com/alicederyn/git-rex.git
```

[pipx]: https://pipxproject.github.io/pipx/
