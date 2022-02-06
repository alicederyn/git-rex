git re-execute
==============

Alternative to git cherry-pick that finds and runs commands in the commit message, instead of reapplying the original diff. This allows authors to document automated code steps, and then reapply the code if a simple rebase fails.

[![Validation status page](https://github.com/alicederyn/git-rex/actions/workflows/validation.yml/badge.svg?branch=main)](https://github.com/alicederyn/git-rex/actions/workflows/validation.yml?query=branch%3Amain)


Reexecuting
-----------

Suppose `git rebase -i` gives the following script:

```
pick 151779 Add new feature
pick 2332c1 Automatic code reformatting
```

To amend the first commit and, once done, automatically rerun the script from the second, just change the rebase script to:

```
edit 151779 Add new feature
x git rex 2332c1 # Automatic code reformatting
```


Commit messages
---------------

Rex only supports scripts in a [Markdown fenced code block] with [bash syntax highlighting]:

````
Automatic code reformatting

Reformat all code with black

```bash
# Code to execute needs to go in a section like this in your commit message
poetry run black .
```
````

Scripts are always run from the repository top level, not the directory `git rex` is run in.
Each script block is invoked as a separate bash script, meaning global changes (like environment
variables, or directory changes) persist until the end of a code black. Each script is run with
`set -e` and `set -o pipefail`, so failures will not be silently ignored.

[Markdown fenced code block]: https://www.markdownguide.org/extended-syntax/#fenced-code-blocks
[bash syntax highlighting]: https://www.markdownguide.org/extended-syntax/#syntax-highlighting


Command-line options
--------------------

### `-e`, `--edit`

Before executing a commit script, opens the commit message in an editor for amendment. Unlike
in regular `git commit`, comments within scripts will not be removed from the edit message.
The author and timestamp of the original commit will be discarded.

If this flag is provided, the commit can optionally be missed off the invocation completely:

```bash
git rex --edit
```

In this case, a template commit message will be opened.


### `-n`, `--no-commit`

Runs a commit script and stages the changes made, but does not commit. The commit message will
be available the next time you run `git commit`. In addition, when this option is used, your
index may contain staged changes. The commit script is performed against the current state of
your index.

### `-v`, `--verbose`

Outputs each command before executing it. Uses `set -x`, so commands are output to standard
error, prefixed with a `+`.


Forwards-compatibility
----------------------

git-rex is currently in pre-release state, meaning **there is no guarantee that commits that work with one version will work with the next**, though no major changes are currently anticipated.


Installing
----------

To install, use [pipx]:

```bash
pip install pipx
export PATH="$PATH:$HOME/.local/bin"
pipx install git+https://github.com/alicederyn/git-rex.git
```

[pipx]: https://pipxproject.github.io/pipx/
