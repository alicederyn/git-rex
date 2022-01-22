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

