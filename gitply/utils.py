from datetime import datetime, timedelta
import subprocess

def weeks_in_year(yr):
    """ Quick hack to return the number of ISO weeks in some given year. Based
        on the assumption that December 31 is either in the last week of the
        requested year, or the first week of the next year.
    """
    d = datetime(year=yr, month=12, day=31)
    isoyr, week, day = d.isocalendar()
    while week <= 1:
        d -= timedelta(days=1)
        isoyr, week, day = d.isocalendar()
    return week

# Credit for this function goes to http://blog.endpoint.com/2015/01/getting-realtime-output-using-python.html
def get_proc_iter(cmd, cwd=None):
    """ Generates the output of the specified shell command one line at a time
    """
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=cwd)
    while True:
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            break
        if output:
            yield output.rstrip().decode("utf-8")
