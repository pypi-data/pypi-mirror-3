from githubv2 import github

print("\nUsers\n\n")
searchUser=github.getUser("ryanb")
print("Search user" + str(searchUser))
github.printUser(searchUser)

print("\nRepos\n\n")
searchRepo=github.getRepo("jacquev6/PyGithub")
print("Search repo" + str(searchRepo))
github.printRepo(searchRepo)

print("\nCommits\n\n")
commitRepo="kSampath/cancan"
commitBranch="master"
commitFileName="Rakefile"
commits=github.searchCommits(commitRepo,commitBranch,commitFileName)
github.printCommits(commits)

print("\nPull requests\n\n")
github.getPullRequests("ask/python-github2")

print("\nOrganizations\n\n")
searchOrg=github.getOrganization("collectiveidea")
print("Search organization" + str(searchOrg))
github.printOrganization(searchOrg)
