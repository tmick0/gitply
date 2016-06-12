import re
from datetime import datetime
from utils import get_proc_iter

# Regular expression for getting the numbers out of --numstat's output
STATS_REGEX = re.compile("^([0-9]+)[ \t]+([0-9]+)")

def get_repo_log(location, since=None):
    """ Returns an iterator over the log lines of a the git repo at the provided
        location. The log will be generated with arguments --numstat --no-notes
        --date=short, to facilitate parsing for the purposes of this script.
    """
    
    args = ["git", "log", "--numstat", "--date=short", "--no-notes"]
    
    if since is not None:
        args.append("--since=%s" % since)
    
    proc = get_proc_iter(args, cwd=location)
    return proc

def iterate_commits(log_lines):
    """ When passed an iterator over the lines of a git log (see get_repo_log),
        this function will generate triples of (email, date, stats) for each
        commit in the log. The stats object is itself a tuple, consisting of
        (additions, deletions).
    """

    it = iter(log_lines)
    author, date, stats = None, None, (0, 0)
    
    # Trim garbage until we find the beginning of a commit
    while next(it)[0:7] != "commit ":
        pass
    
    for line in it:
        if line[0:7] == "Author:":
            # Clean up the email and add it to the pending tuple
            _, t = line[7:].strip().split("<", 1)
            t = t.rstrip(">")
            author = t
        elif line[0:5] == "Date:":
            # Parse date into a datetime object and add it to the pending tuple
            date = datetime.strptime(line[5:].strip(), "%Y-%m-%d")
        elif line[0:7] == "commit ":
            # When we get to the next commit, yield the tuple of the previous one
            # and reset our author, date, stats data
            yield (author, date, stats)
            author, date, stats = None, None, (0, 0)
        else:
            # Either we're in the commit message, or this is part of the --numstat,
            # in which case we should parse it
            match = STATS_REGEX.match(line)
            if match is not None:
                # Accumulate the stats for each file
                x, y = stats
                dx, dy = match.group(1, 2)
                stats = x + int(dx), y + int(dy)

    # When we get to the end of the log, we should yield the last result from
    # the log
    if author is not None and date is not None:
        yield author, date, stats

