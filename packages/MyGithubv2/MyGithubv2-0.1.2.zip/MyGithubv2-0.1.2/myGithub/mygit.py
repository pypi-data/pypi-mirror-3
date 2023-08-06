from github2.client import Github

#Define Github object        
github=Github("kSampath","")
github=Github()

def getUser(user_name):
     
    user=github.users.show(user_name)    
    return user

def searchUsers(search_user_string):     
    results = github.users.search(search_user_string)
    for user in results:
        print(user.login)
        
def printUser(user):     
    print("Full User Name = " + str(user.name))
    print("User email = " + str(user.email))
    print("User login name = " + str(user.login))
    print("User date created = " + str(user.created_at))
    print("Following count = " + str(user.following_count))
    print("Followers count = " + str(user.followers_count))
    print("User id = "  +  str(user.id))
    print("Disk usage = " + str(user.disk_usage))
    print("User location = " + str(user.location))
    print("User plan = " + str(user.plan))
    print("User authenticated? = " + str(user.is_authenticated))
    print("User no of private repos = " + str(user.owned_private_repo_count))
    print("User permission = " + str(user.permission))
    print("User private gist count = " + str(user.private_gist_count))
    print("User type = " + str(user.type))
    print("User company = " + str(user.company))
    
def getRepo(repoName):     
    repo = github.repos.show(repoName)
    return repo
    
def printRepo(repo):     
    print("Show particular repo = " + str(repo.homepage))   
    print("Date repo was created = " + str(repo.created_at))
    print("Description of repo = " + str(repo.description))
    print("Issues in repo = " + str(repo.has_issues))
    print("Repo language = " + str(repo.language))
    print("Repo name = " + str(repo.name))
    print("Repo Owner = " + str(repo.owner))
    print("Repo watchers = " + str(repo.watchers))
    print("Repo size = " + str(repo.size))
    print("Repo Parent = " + str(repo.parent))    
    
def searchRepos(search_repo_name):     
    repositories= github.repos.search(search_repo_name)
    for repository in repositories:
        print(repository.name)

def searchCommits(search_commit_repo,search_commit_branch,search_commit_file_name):     
    commits = github.commits.list(search_commit_repo, search_commit_branch, file=search_commit_file_name)
    return commits        

def printCommits(commits):     
    for commit in commits:
        print("Commit id = " +  commit.id)
        print("Commit date = " +  str(commit.committed_date))
        print("Commit message = " +  commit.message)
        
def getOrganization(orgName):     
    org = github.organizations.show(orgName)
    return org

def printOrganization(org):     
    print("Orgaization name = " + str(org.id))
    print("Orgaization plan = " + str(org.plan))
    print("Orgaization permission = " + str(org.permission))
    print("Orgaization type = " + str(org.type))
    print("Orgaization Blog = " + str(org.blog))
    print("Orgaization Email = " + str(org.email))
    print("Orgaization Location = " + str(org.location ))
    print("Orgaization Login name = " + str(org.login))
    print("Orgaization Followers count = " + str(org.followers_count))
    print("Orgaization Following count = " + str(org.following_count ))
    print("Orgaization Created At = " + str(org.created_at))

def getPullRequests(repoName):     
    requests = github.pull_requests.list(repoName)
    for request in requests:
        print("Request title = " + str(request.title))

