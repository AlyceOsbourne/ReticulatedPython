import secret


def collect(login: str, *query_strings, opensource_only=True, dump_to_ast=True, high_quality_only=True,
            no_small_files=True, limit=0):
    """This requires the pyGithub and astor modules"""

    from github import Github
    if dump_to_ast:
        import ast, astor  # only import if needed

    git = Github(login)

    print(f"Logged in as {git.get_user().login}")
    print(git.rate_limiting, git.rate_limiting_resettime)

    # part of the reason I have created a generator is that there is a request limit
    # for the github rest api, so it almost makes sense to retrieve one at a time (or you can batch with the query)
    # and process them as you go, the processing time acts as a sort of buffer time between requests

    # the high quality flag makes the assumption that repositories with a high number of stars are more
    # likely to be of a high quality than say a repository with say 4 stars,
    # this is in th hope of providing higher quality data for the training model

    query = "language:python "

    if query_strings:
        query += ",".join(query_strings)  # this is for other query flags you may want to include

    if opensource_only:  # really, this should never be false, only included for completeness
        accepted_licences = "mit", 'unlicense', "mpl-2.0"
        language_query = " license:" + ' license:'.join(accepted_licences)
        query += language_query
        print("Searching for open source licenses", language_query)

    else:
        print("\nWarning, data collected is not guaranteed to be open source, \n"
              "it is unsafe to use any derivative data from this generator for any commercial use,\n"
              "I do not take any responsibility for any user who disables this flag, nor will support be given\n"
              "to anyone who has disabled this flag, you have been warned!\n")

    print(f"finding repositories with query: {query}")

    query = git.search_repositories(query=query, sort="stars", order="desc")

    print(f"Found {query.totalCount} repositories")

    end = False

    total_yielded = 0

    for repository in query:

        if limit and total_yielded >= limit:
            break

        if high_quality_only and repository.get_stargazers().totalCount > 2000 or not high_quality_only:
            print(f"Searching {repository.owner.login}/{repository.name}")
            for _file in repository.get_contents(""):
                if limit and total_yielded >= limit:
                    break
                if _file.name.endswith(".py"):
                    # if dump_to_ast takes the raw content, parses it into ast,
                    # then dumps that ast as nice readable text (not that this matters to NN)
                    # or if not dumping to ast returns the raw content
                    if _file.size < 99999:
                        if no_small_files and _file.size > 1000 or not no_small_files:
                            print(f"    Found file {_file.name}, size {_file.size}")
                            if dump_to_ast:
                                try:
                                    out = astor.dump_tree(ast.parse(_file.decoded_content))
                                    yield out
                                    total_yielded += 1
                                except IndentationError:
                                    continue
                                except SyntaxError:
                                    continue
                            else:
                                yield _file.decoded_content
                                total_yielded += 1


import requests

headers = {
    'Authorization': f'token {secret.github_login}',
}

response = requests.get('https://api.github.com/rate_limit', headers=headers)

print(response.text.replace("},", "},\n"))
