import sys
from datetime import datetime, timedelta
from itertools import chain

# for plotting
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# gitply imports
from maps import NullUserMap, FileUserMap
from core import iterate_commits, get_repo_log
from utils import weeks_in_year

def main(*args):
    """\
This script gathers some information about the commit history from the
currently-checked-out branches of each of the git repos listed on the
command line. It will show the number of commits (with insertion and
deletion counts) made per ISO week by contributor to the project.
Optionally, it will also generate plots of the same data.

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
        else:
            repos.append(a)

    # Dictionaries for storing the data to be presented
    commits   = {}
    additions = {}
    deletions = {}
    
    # Keep track of the start date and end date for the purposes of fitting the
    # axes of the plot
    start_date = None
    end_date   = None
    
    # Processes the git logs and stores some intermediate results in the three
    # dictionaries instantiated above
    for email, date, stats in chain(*[iterate_commits(get_repo_log(repo)) for repo in repos]):

        # We will use the ISO year and week number
        year, week, dow = date.isocalendar()
        
        # Trim date to be the first day of the current ISO week -- we will save this in order to identify gaps in the history later
        date = date.replace(hour=0,minute=0,second=0,microsecond=0) - timedelta(days=(dow-1))
        user = user_map.map(email)
        
        if start_date is None or date < start_date:
            start_date = date
        if end_date is None or date > end_date:
            end_date = date
        
        if not user in commits:
            commits[user] = {}
        if not year in commits[user]:
            commits[user][year] = {}
        if not week in commits[user][year]:
            commits[user][year][week] = (0, date)
        
        if not user in additions:
            additions[user] = {}
        if not year in additions[user]:
            additions[user][year] = {}
        if not week in additions[user][year]:
            additions[user][year][week] = 0
        
        if not user in deletions:
            deletions[user] = {}
        if not year in deletions[user]:
            deletions[user][year] = {}
        if not week in deletions[user][year]:
            deletions[user][year][week] = 0
        
        prev, d = commits[user][year][week]
        commits[user][year][week] = (prev+1, d)
        
        additions[user][year][week] += stats[0]
        deletions[user][year][week] += stats[1]
    
    # Print plaintext report
    if printout:
    
        for user in commits:
            
            print("History for %s" % (user))
            last = None
            
            for year in sorted(commits[user]):
                for week in sorted(commits[user][year]):
                
                    count, date = commits[user][year][week]
                    
                    # Identify gaps in the user's history
                    if last is not None and date - last >= timedelta(days=8):
                        delta = int((date - last).total_seconds() / (3600*24*7) - 1)
                        print("  -- Gap of %d week%s" % (delta, "s" if delta > 1 else "")) 
                    last = date
                    
                    adds = additions[user][year][week]
                    dels = deletions[user][year][week]
                    
                    print("  %d, week %2d: %2d commits, +%-4d -%-4d" % (year, week, count, adds, dels))
            
            print("")

    # Draw plots
    if plotout is not None:

        with PdfPages(plotout) as pdf:

            # Figure out min and max (year, week) pair
            min_yr, min_week, _  = start_date.isocalendar()
            max_yr, max_week, _  = end_date.isocalendar()

            # Calculate week counts for each year in our range
            week_counts = {yr: weeks_in_year(yr) for yr in range(min_yr, max_yr+1)}
            labels = []
        
            # Generate labels for each week -- 
            # Add year to the label of the first week of each year as well as 
            # the very first week in the history
            for yr, weeks in sorted(week_counts.items(), key=lambda x: x[0]):
                for i in range(weeks):
                    if i == 0 or (yr == min_yr and i == min_week - 1):
                        labels.append("%d - %d" % (yr, i+1))
                    else:
                        labels.append("%d" % (i+1))
            
            # Helper method for converting a date to a position on the x axis
            def date_to_offset(year, week):
                offset = sum(count for yr, count in week_counts.items() if yr < year)
                return offset + week - 1
            
            x_ticks = np.arange(len(labels))
            template = [0 for i in range(len(labels))]
            
            width = 0.4
            
            for user in commits:
            
                grn = template[:]
                red = template[:]
                cnt = template[:]
            
                for year in commits[user]:
                    for week in commits[user][year]:
                        pos = date_to_offset(year, week)
                        grn[pos] = additions[user][year][week]
                        red[pos] = deletions[user][year][week]
                        cnt[pos] = commits[user][year][week][0]
                
                fig, ax = plt.subplots(figsize=(24,4))
                ax.set_title("Modification history for %s" % user)
                ax.set_ylabel("Lines added/deleted")
                ax.set_yscale('symlog')
                ax.set_xlabel("Week number")
                ax.set_xlim(date_to_offset(min_yr, min_week), date_to_offset(max_yr, max_week))
                ax.set_ylim(0, max(grn+red+[1])*1.5)
                
                ax.grid()
                
                ax.bar(x_ticks, grn, width, color='g')
                ax.bar(x_ticks + width, red, width, color='r')
                
                ax.set_xticks(x_ticks + width)
                ax.set_xticklabels(labels, rotation='vertical')
                
                ax2 = ax.twinx()
                ax2.set_xlim(date_to_offset(min_yr, min_week), date_to_offset(max_yr, max_week))
                ax2.set_ylim(0, max(cnt)*1.5)
                
                ax2.set_ylabel("Commit count")
                ax2.plot(x_ticks+width, cnt)
                
                fig.subplots_adjust(bottom=0.28)
                
                pdf.savefig(fig)

    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
