import urllib.request as R
import urllib.error as ER
import re
import json
import itertools as I
import sqlite3 as S

class publicRSAKey:
    def __init__(self, key : str):
        self.key : str = key

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return self.key

class User:
    def __init__(self, username : str):
        self.username : str = username
        self._cachedProjects : Project = None
        self._cachedKeys : [publicRSAKey] = None

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def __str__(self):
        return self.username

    def getPublicRSAKey(self, cache : bool, **kwargs):
        geturl = 'https://api.github.com/users/{user}/keys'.format(user = self.username)
        if kwargs["clientID"] and kwargss["clientSecret"]:
            geturl += "?client_id={id}&client_secret={secret}"
            geturl = geturl.format(id = kwargs["clientID"], secret = kwargs["clientSecret"])
        with R.urlopen(geturl) as remot:
            resp = json.loads(remot.read())
            keys = [publicRSAKey(keyStr["key"]) for keyStr in resp]
            if cache:
                self._cachedKeys = keys
            return keys
    # getProjects is also defined, but later

class Project:
    def __init__(self, url : str):
        self.url : str = url
        matches = re.match("""http[s]{0,1}:\/\/github.com\/(.+)\/(.+)""", url).groups()
        self.owner : User = User(matches[0])
        self.name : str = matches[1]
        self._cachedUsers : [User] = None

    def __eq__(self, other):
        return self.name == other.name and other.owner == other.owner

    def __hash__(self):
        return hash((name, owner))

    def getUsers(self, cache : bool) -> {User}:
        if (self._cachedUsers):
            return self._cachedUsers
        else:
            geturl = 'https://api.github.com/repos/{owner}/{name}/contributors'.format(owner = self.owner.username, name = self.name)
        if kwargs["clientID"] and kwargss["clientSecret"]:
            geturl += "?client_id={id}&client_secret={secret}"
            geturl = geturl.format(id = kwargs["clientID"], secret = kwargs["clientSecret"])
        # print(geturl)
            with R.urlopen(geturl) as remot:
                resp = json.loads(remot.read())
                usersStr = map(lambda x: x["login"], resp)
                users = set(map(User, usersStr))
                if cache:
                    self._cachedUsers = users
                return users

def getProjects(self, cache : bool) -> {Project}:
        if (self._cachedProjects):
            return self._cachedProjects
        else:
            geturl = 'https://api.github.com/users/{user}/repos?type=owner'.format(user = self.username)
            if kwargs["clientID"] and kwargss["clientSecret"]:
                geturl += "?client_id={id}&client_secret={secret}"
                geturl = geturl.format(id = kwargs["clientID"], secret = kwargs["clientSecret"])
            # print(geturl)
            with R.urlopen(geturl) as remot:
                resp = json.loads(remot.read())
                projectsStr = map(lambda x: x["name"], resp)
                projects = [Project("https://github.com/{user}/{repo}".format(user = self.username, repo = x)) for x in projectsStr]
                if cache:
                    self._cachedProjects = projects
                return projects
User.getProjects = getProjects

def recursivelyTraverse(seedUser : User) -> User:
    currentUser = seedUser
    traversedUsers = {seedUser}
    currentGeneration = set(I.chain(*[project.getUsers(False) for project in currentUser.getProjects(False)]))

    while True:
        yield from currentGeneration
        for x in currentGeneration: #TODO: make this recurse more effeciently
            if x in traversedUsers:
                continue
            traversedUsers.add(x)
            currentUser = x
            try:
                currentGeneration = set(I.chain(*[project.getUsers(False) for project in currentUser.getProjects(False)]))
            except ER.HTTPError as err:
                if (err.code == 403):
                    yield err
                else:
                    raise err
