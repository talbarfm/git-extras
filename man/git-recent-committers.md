git-recent-committers(1) -- List committers with at least one commit in the last N days
===============================================

## SYNOPSIS

`git-recent-committers` [-n &lt;days&gt;]

## DESCRIPTION

  Lists people who made at least one commit in the last N days, with their commit count in that period (one line per committer, e.g. `5  Alice`, `2  Bob`).

## OPTIONS

  -n &lt;days&gt;

  Use the last &lt;days&gt; days. Overrides the default from GIT_RECENT_COMMITTERS_DAYS.

## ENVIRONMENT

  GIT_RECENT_COMMITTERS_DAYS

  Default number of days to look back when -n is not given. Defaults to 7 if unset.

## EXAMPLES

  List committers in the last 7 days (default):

    $ git recent-committers
    5  Alice
    2  Bob

  List committers in the last 14 days:

    $ git recent-committers -n 14

  Use a custom default of 30 days:

    $ GIT_RECENT_COMMITTERS_DAYS=30 git recent-committers

## AUTHOR

Written for git-extras.

## REPORTING BUGS

&lt;<https://github.com/tj/git-extras/issues>&gt;

## SEE ALSO

&lt;<https://github.com/tj/git-extras>&gt;
