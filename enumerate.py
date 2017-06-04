import urllib.request as R
import re
import json
import itertools as I

class User:
    def __init__(self, username : str):
        self.username = username
        self.__cachedProjects = None

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def __str__(self):
        return self.username

    def getProjects(self, cache : bool) -> {Project}:
        if (self.__cachedProjects):
            return self.__cachedProjects
        else:
            geturl = 'https://api.github.com/users/{user}/repos?type=owner'.format(user = self.username)
            print(geturl)
            with R.urlopen(geturl) as remot:
                resp = json.loads(remot.read())
                projectsStr = map(lambda x: x["name"], resp)
                projects = [Project("https://github.com/{user}/{repo}".format(user = self.username, repo = x)) for x in projectsStr]
                if cache:
                    self.__cachedProjects = projects
                return projects


class Project:
    def __init__(self, url : str):
        self.url = url
        matches = re.match("""http[s]{0,1}:\/\/github.com\/(.+)\/(.+)""", url).groups()
        self.owner = User(matches[0])
        self.name = matches[1]
        self.__cachedUsers = None

    def __eq__(self, other):
        return self.name == other.name and other.owner == other.owner

    def __hash__(self):
        return hash((name, owner))

    def getUsers(self, cache : bool) -> {User}:
        if (self.__cachedUsers):
            return self.__cachedUsers
        else:
            geturl = 'https://api.github.com/repos/{owner}/{name}/contributors'.format(owner = self.owner.username, name = self.name)
            print(geturl)
            with R.urlopen(geturl) as remot:
                resp = json.loads(remot.read())
                usersStr = map(lambda x: x["login"], resp)
                users = set(map(User, usersStr))
                if cache:
                    self.__cachedUsers = users
                return users

def recursivelyTraverse(seedUser : User) -> {User}:
    currentUser = seedUser
    currentGeneration = set(I.chain(*[project.getUsers(False) for project in seedUser.getProjects(False)]))
    yield currentGeneration
    yield from map(recursivelyTraverse, currentGeneration)
