import urllib.request as R
import re
import json
import itertools as I

class User:
    def __init__(self, username : str):
        self.username = username
        self._cachedProjects = None

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def __str__(self):
        return self.username

    # getProjects is also defined, but later

class Project:
    def __init__(self, url : str):
        self.url = url
        matches = re.match("""http[s]{0,1}:\/\/github.com\/(.+)\/(.+)""", url).groups()
        self.owner = User(matches[0])
        self.name = matches[1]
        self._cachedUsers = None

    def __eq__(self, other):
        return self.name == other.name and other.owner == other.owner

    def __hash__(self):
        return hash((name, owner))

    def getUsers(self, cache : bool) -> {User}:
        if (self._cachedUsers):
            return self._cachedUsers
        else:
            geturl = 'https://api.github.com/repos/{owner}/{name}/contributors'.format(owner = self.owner.username, name = self.name)
            print(geturl)
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
            print(geturl)
            with R.urlopen(geturl) as remot:
                resp = json.loads(remot.read())
                projectsStr = map(lambda x: x["name"], resp)
                projects = [Project("https://github.com/{user}/{repo}".format(user = self.username, repo = x)) for x in projectsStr]
                if cache:
                    self._cachedProjects = projects
                return projects
User.getProjects = getProjects

def recursivelyTraverse(seedUser : User) -> {User}:
    currentUser = seedUser
    currentGeneration = set(I.chain(*[project.getUsers(False) for project in seedUser.getProjects(False)]))
    yield currentGeneration
    # map(lambda x: yield from recursivelyTraverse(x), currentGeneration) apparently this doesnt work
    for x in currentGeneration: #TODO: make this recurse more effeciently
        yield from recursivelyTraverse(x)

