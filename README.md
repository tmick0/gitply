# gitply
Simple script for visualizing the contributions of each contributor to a repository

## Requirements

- Python (tested on 2.7.11+)
- numpy
- matplotlib
- python-gitlab (for optional Gitlab interface)
- the git client (Python bindings not necessary)

## Usage

Currently, gitply supports three types of reports and two backends.

The report types available are:

- mosaic (Github-style contribution summary for a year)
- history (Chart of commits, insertions, and deletions per week for the history of a project)
- weekly (Chart of commits, insertions, and deletions per day for the past week)

The backends are:

- git CLI (Obtains statistics from the logs of one or more local repositories)
- Gitlab (Obtains statistics from a Gitlab instance using a private access token)

The git CLI backend should be stable and trustworthy. The Gitlab backend should be considered experimental for the time being. The git CLI backend will report the histories for the currently-checked out branches of each of the listed repositories, while the Gitlab backend will report the histories of the master branches of each repository hosted on the instance.

The general syntax for generating some output using the CLI backend is:

    python gitply <report_type> [--users user_map.txt] [--pdf output_plot.pdf] [--noprint] [/paths/to/git/repos ...]

Or for the Gitlab backend:

    python gitply <report_type> [--users user_map.txt] [--pdf output_plot.pdf] [--noprint] --gitlab <gitlab_url> <secret_key>

### Report types

The three plot types look like this:

**Mosaic:**

![Example of mosaic](/example_plots/mosaic.png)

The commits made on each day throughout the past year are counted. The year is displayed as a grid, where each column is a week. The color of a cell on the grid conveys how many commits were made on that day.

**History:**

![Example of history](/example_plots/history.png)

Each data point conveys the number of lines inserted (green bar) and removed (red bar), as well as the number of commits made (blue line), for each week in the repository's entire history. The additions/deletions are shown in log scale (left y-axis), and the commits are shown in linear scale (right y-axis).

**Weekly:**

![Example of weekly](/example_plots/weekly.png)

As in the history plot, we count commits, insertions, and deletions. However, we count them per-day instead of per-week, and only display the most recent week of activity.

With each report type, a plot for each user is displayed on its own page in the PDF.

By default, gitply will also print out a plaintext summary of the data presented in the plot. This can be disabled using the `--noprint` option.

### User maps

Users sometimes configure their git clients on different machines using different email addresses. By default, gitply will treat each email address as belonging to a unique user. To combine several addresses into one logical email entity, a user map can be specified. Take a look at [/usermap_example.txt](usermap_example.txt) for an example of the format for this file.
