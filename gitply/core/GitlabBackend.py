import gitlab
from datetime import datetime

class GitlabBackend (object):

    def __init__(self, host, token, since=None):
        self.api = gitlab.Gitlab(host, token=token)
        if since is not None:
            self.since = datetime.strptime(since, "%Y-%m-%d")
        else:
            self.since = None
    
    def __iter__(self):
        
        def it():
            for proj in self.api.getall(self.api.getprojects):
                for commit in self.api.getall(self.api.getrepositorycommits, proj['id']):
                    date,_ = commit['created_at'].split("T")
                    date = datetime.strptime(date, "%Y-%m-%d")
                    if self.since is None or date >= self.since:
                        yield commit['author_email'], date, (0, 0)
                
        return it()
    
