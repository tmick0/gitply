from weekly_history import main as weekly_history
from week_summary   import main as week_summary
import sys

def main(dest=None, *args):
    dest_map = {
        "weekly":  week_summary,
        "history": weekly_history
    }
    
    if dest is None or dest not in dest_map:
        print("usage: %s (%s) [args]" % (sys.argv[0], "|".join(dest_map)))
        return 1
    
    return dest_map[dest](*args)

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
