import sys
from datetime import datetime, timedelta
from itertools import chain
from math import ceil

# for plotting
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colorbar as colorbar
from matplotlib import gridspec
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

# gitply imports
from maps import NullUserMap, FileUserMap
from core import iterate_commits, get_repo_log
from utils import weeks_in_year

def main(*args):
    """\
This script generates a github-style summary of a year's commit activity.

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

    # Dictionary for storing the data to be presented
    commits   = {}
    
    # Find the bound for searching -- the beginning of the week, one year ago
    today    = datetime.now().replace(hour=0, minute=0,second=0,microsecond=0)
    year_ago = today.replace(year = today.year - 1)
    _, __, dow = year_ago.isocalendar()
    year_ago-= timedelta(days=(dow-1))
    
    # Processes the git logs and stores some intermediate results in the three
    # dictionaries instantiated above
    for email, date, stats in chain(*[iterate_commits(get_repo_log(repo, since=year_ago.strftime("%Y-%m-%d"))) for repo in repos]):
        
        # Trim date of commit to midnight of that day
        date = date.replace(hour=0,minute=0,second=0,microsecond=0)
        user = user_map.map(email)
        
        if not user in commits:
            commits[user] = {}
        if not date in commits[user]:
            commits[user][date] = 0
        
        commits[user][date]   += 1
    
    # Print plaintext report
    if printout:
    
        for user, cal in commits.items():
            
            print("Annual summary for %s" % (user))
            
            for date, count in sorted(cal.items(), key=lambda x: x[0]):
                strdate = date.strftime("%x")
                print("  %s: %2d commits" % (strdate, count))
            
            print("")

    # Draw plots
    if plotout is not None:

        with PdfPages(plotout) as pdf:
        
            labels  = []
            offsets = {}
            
            cdict = ((205.,247.,237.), (15.,191.,148.))
            
            cdict = {
                'red':  (
                    (0.0, cdict[0][0]/255, cdict[0][0]/255),
                    (1.0, cdict[1][0]/255, cdict[1][0]/255)
                ),
                'green':(
                    (0.0, cdict[0][1]/255, cdict[0][1]/255),
                    (1.0, cdict[1][1]/255, cdict[1][1]/255)
                ),
                'blue': (
                    (0.0, cdict[0][2]/255, cdict[0][2]/255),
                    (1.0, cdict[1][2]/255, cdict[1][2]/255)
                )
            }
            
            plt.register_cmap(name='Sea', data=cdict)
            colormap = plt.get_cmap('Sea')
            
            min_yr, min_week, _ = year_ago.isocalendar()
            max_yr, max_week, _ = today.isocalendar()
            
            week_counts = {yr: weeks_in_year(yr) for yr in range(min_yr, max_yr+1)}
            
            # Generate labels for each week -- 
            # Add year to the label of the first week of each year as well as 
            # the very first week in the history
            lastmon = None
            for yr, weeks in sorted(week_counts.items(), key=lambda x: x[0]):
                cur = datetime(year=yr, month=1, day=4) # jan 4 is always in week 1 of the iso year
                for i in range(weeks):
                    mon = cur.strftime("%b")
                    if mon != lastmon:
                        labels.append(cur.strftime("%b"))
                    else:
                        labels.append("")
                    offsets[(yr, i+1)] = len(offsets)
                    cur += timedelta(days=7)
                    lastmon = mon
            
            for user in commits:
            
                fig = plt.figure(figsize=(7.5, 1.65))

                gs = gridspec.GridSpec(2, 1, height_ratios=[8, 1]) 
                ax, cax = plt.subplot(gs[0]), plt.subplot(gs[1])
                
                maxcommits = ceil(max(commits[user].values()) * 1.5)
                
                for date, count in commits[user].items():
                    yr, wk, dow = date.isocalendar()
                    offset = offsets[(yr, wk)]
                    
                    ax.add_patch(
                        patches.Rectangle(
                            (offset+0.05, dow - 1 + 0.05),
                            0.95, 0.95,
                            linewidth=0,
                            facecolor=colormap(1. * (count - 1) / (maxcommits) )
                        )
                    )
                
                ax.set_title("Commit summary for %s" % user, y=1.28)
                
                ax.xaxis.tick_top()
                ax.set_xticks([x for x in np.arange(len(offsets)) if labels[int(x)] != ""])
                ax.set_xticks(np.arange(len(offsets)), minor=True)
                
                ax.set_xticklabels([x for x in labels if x != ""])
                ax.set_xlim(offsets[(min_yr, min_week)], offsets[(max_yr, max_week)]+1)

                ax.set_ylim(0, 7)
                ax.set_yticks(np.arange(7))
                ax.set_yticklabels(["S ","M ","T ","W ","R ","F ","S "])
                ax.invert_yaxis()
                
                if maxcommits <= 10:
                    top  = maxcommits
                    step = 1.
                else:
                    top = (maxcommits - 1) + 11 - ((maxcommits - 1) % 11)
                    step = top/11.

                colorticks  = np.arange(0., top+(step/2), step) / (top)
                colorlabels = ["%d" % (x*top) for x in colorticks]
                
                cbar = colorbar.ColorbarBase(
                        cax, cmap=colormap,
                        orientation='horizontal'
                )
                cbar.set_ticks(colorticks)
                cbar.set_ticklabels(colorlabels)
                cax.set_xlim(colorticks[0], colorticks[-1])
                
                for label in ax.get_xticklabels():
                    label.set_horizontalalignment('left')
                
                for label in ax.get_yticklabels():
                    label.set_horizontalalignment('center')
                    label.set_verticalalignment('top')
                
                for item in (
                    [ax.xaxis.label, ax.yaxis.label] +
                    ax.get_xticklabels() + ax.get_yticklabels() +
                    cax.get_xticklabels()
                ):
                    item.set_fontsize(7)
                
                ax.title.set_fontsize(10)
                fig.subplots_adjust(top=0.7, bottom=0.15)
                
                pdf.savefig(fig)

    return 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
