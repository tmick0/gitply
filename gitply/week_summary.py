import sys
from datetime import datetime, timedelta
from itertools import chain

# for plotting
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# gitply imports
from maps import NullUserMap, FileUserMap
from core import GitCLIBackend, GitlabBackend
from core.utils import weeks_in_year

def main(*args):
    """\
This script prints statistics about the past week's worth of activity
on the listed repository (or repositories). Optionally, it will also
generate plots of the same data.

Some command-line options are accepted:
    
    --users <user_map.txt>
    
        Loads a mapping from user email addresses to actual identities
        of the users. Each line in the provided text file should consist
        of the email address, followed by at least one space or tab,
        then finally the user name to map to.
        
        If not specified, the raw email address from the commit log
        will be used instead. 
    
    --pdf <plot_output.pdf>
    
        Enables plotting the analysis and saving it to a PDF file. If
        not specified, only a textual analysis will be presented.
        
        With PDF output enabled, the textual analysis will normally
        still be printed (use --noprint to disable it). It may look
        like the script hangs after printing the plaintext report --
        this is normal, it just takes a while to generate the PDF.
    
    --noprint
    
        If you only want the plot, and no text output, supply this
        option.

Any other command-line argument will be interpreted as a directory
containing a git repository which should be analyzed.\
    """

    # Default options
    repos = []
    user_map = NullUserMap()
    plotout = None
    printout = True
    gitlab = None

    if "--help" in args:
        print(main.__doc__)
        return 0

    # Parse command-line    
    it = iter(args)
    for a in it:
        if a == "--users":
            user_map = FileUserMap(next(it))
        elif a == "--pdf":
            plotout = next(it)
        elif a == "--noprint":
            printout = False
        elif a == "--gitlab":
            gitlab = next(it), next(it)
        else:
            repos.append(a)
        
    # Setup backend
    if gitlab is None:
        coretype = GitCLIBackend
        coreargs = repos
    else:
        coretype = GitlabBackend
        coreargs = gitlab

    # Dictionaries for storing the data to be presented
    commits   = {}
    additions = {}
    deletions = {}
    
    # Figure out the date today and one week ago
    
    today    = datetime.now().replace(hour=0, minute=0,second=0,microsecond=0)
    week_ago = today - timedelta(days=7)
    
    # Processes the git logs and stores some intermediate results in the three
    # dictionaries instantiated above
    for email, date, stats in coretype(*coreargs, since=week_ago.strftime("%Y-%m-%d")):
        
        # Trim date of commit to midnight of that day
        date = date.replace(hour=0,minute=0,second=0,microsecond=0)
        user = user_map.map(email)
        
        if not user in commits:
            commits[user] = {}
        if not date in commits[user]:
            commits[user][date] = 0
        
        if not user in additions:
            additions[user] = {}
        if not date in additions[user]:
            additions[user][date] = 0
        
        if not user in deletions:
            deletions[user] = {}
        if not date in deletions[user]:
            deletions[user][date] = 0
        
        commits[user][date]   += 1
        additions[user][date] += stats[0]
        deletions[user][date] += stats[1]
    
    # Print plaintext report
    if printout:
    
        for user in commits:
            
            print("Weekly report for %s" % (user))
            
            for date in sorted(commits[user]):
                strdate = date.strftime("%a, %b %d")
                count = commits[user][date]
                adds = additions[user][date]
                dels = deletions[user][date]
                print("  %s: %2d commits, +%-4d -%-4d" % (strdate, count, adds, dels))
            
            print("")

    # Draw plots
    if plotout is not None:

        with PdfPages(plotout) as pdf:
        
            labels  = []
            offsets = {}
        
            # Generate labels for each day
            cur = week_ago
            while cur <= today:
                offsets[cur] = len(offsets)
                labels.append(cur.strftime("%a"))
                cur += timedelta(days=1)
            
            x_ticks = np.arange(len(labels))
            template = [0 for i in range(len(labels))]
            
            width = 0.4
            
            for user in commits:
            
                grn = template[:]
                red = template[:]
                cnt = template[:]
            
                for date in commits[user]:
                    pos = offsets[date]
                    grn[pos] = additions[user][date]
                    red[pos] = deletions[user][date]
                    cnt[pos] = commits[user][date]
                
                fig, ax = plt.subplots(figsize=(6,3))
                ax.set_title("Weekly report for %s" % user)
                ax.set_ylabel("Lines added/deleted")
                ax.set_yscale('symlog')
                ax.set_xlabel("Day of Week")
                ax.set_xlim(offsets[week_ago], offsets[today]+1)
                ax.set_ylim(0, max(grn+red+[1])*1.5)
                
                ax.grid()
                
                ax.bar(x_ticks, grn, width, color='g')
                ax.bar(x_ticks + width, red, width, color='r')
                
                ax.set_xticks(x_ticks + width)
                ax.set_xticklabels(labels, rotation='vertical')
                
                ax2 = ax.twinx()
                ax2.set_xlim(offsets[week_ago], offsets[today]+1)
                ax2.set_ylim(0, max(cnt)*1.5)
                
                ax2.set_ylabel("Commit count")
                ax2.plot(x_ticks+width, cnt)
                
                fig.subplots_adjust(bottom=0.28)
                
                pdf.savefig(fig)

    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
