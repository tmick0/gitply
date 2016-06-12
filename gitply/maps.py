import os.path

class AbstractUserMap (object):
    """ A UserMap is used to map an email address to a specific user's identity.
        This is necessary because sometimes users have configured git with
        different email addresses on different machines; as a result, we need to
        define a mapping so we can account all of the commits from each user
        together.
        
        A UserMap extending this interface need only implement one method, map.
        The map method takes one argument -- an email address -- and returns the
        username to associate with that address.
    """
    def map(self, email):
        raise NotImplementedError()

class NullUserMap (AbstractUserMap):
    """ Performs no mapping from email to username -- the email is assumed to be
        the actual username.
    """
    def map(self, email):
        return email

class FileUserMap (AbstractUserMap):
    """ Loads a text file consisting of (email, username) pairs which define the
        mappings from emails to usernames.
    """
    def __init__(self, filename):
        self.name_map = {}
        filename = os.path.expanduser(filename)
        with open(filename, 'r') as file:
            for line in file:
                try:
                    email, name = line.split(" ", 1)
                    self.name_map[email.strip()] = name.strip()
                except ValueError:
                    continue
    def map(self, email):
        try:
            return self.name_map[email]
        except KeyError:
            return "unknown"
