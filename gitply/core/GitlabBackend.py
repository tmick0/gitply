import gitlab
from datetime import datetime

class GitlabBackend (object):

    def __init__(self, host, token, since=None):
        self.api = gitlab.Gitlab(host, token)
        if since is not None:
            self.since = datetime.strptime(since, "%Y-%m-%d")
        else:
            self.since = None
    
    def diff_stat(self, diff_list):
        inserts, deletes = 0, 0
        for file_diff in diff_list:
            diff_str = file_diff['diff']
            for line in diff_str.split(u'\n'):
                if len(line) >= 2 and line[0] == "+" and line[1] != "+":
                    inserts += 1
                elif len(line) >= 2 and line[0] == "-" and line[1] != '-':
                    deletes += 1
        return inserts, deletes
    
    def __iter__(self):
        
        def it():
            for proj in self.api.projects.list(all=True):
                for commit in proj.commits.list(all=True):
                    
                    date,_ = commit.created_at.split("T")
                    date = datetime.strptime(date, "%Y-%m-%d")
                    if self.since is None or date >= self.since:
                        yield commit.author_email, date, self.diff_stat(commit.diff())
                
        return it()
    
