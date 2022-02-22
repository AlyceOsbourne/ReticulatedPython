"""A collector class for files from GitHub, being used to train_tokenizer a NN how to code,
"""

import ast
import datetime

import astor
import time

from github import Github
import github.GithubException
from github.PaginatedList import PaginatedList
from github.Repository import Repository


def build_query(*query_strings,
                opensource_only=True,
                since=None,
                till=None,
                language="python") -> str:
    """builds query strings for GitHub,
    """

    query = f"language:{language} "

    if since is not None or till is not None:
        query += f" created:{since if since else ''}{'..' + till if till else ''}"

    if query_strings:
        query += " ".join(
            query_strings
        )  # this is for other query flags you may want to include

    if opensource_only:  # really, this should never be false, only included for completeness
        accepted_licences = "mit", 'unlicense', "mpl-2.0"
        language_query = " license:" + ' license:'.join(accepted_licences)
        query += language_query
        print("Searching for open source licenses", language_query)

    else:
        print(
            "\nWarning, data collected is not guaranteed to be open source, \n"
            "it is unsafe to use any derivative data from this generator for any commercial use,\n"
            "I do not take any responsibility for any user who disables this flag, nor will support be given\n"
            "to anyone disabling this flag, you have been warned!\n")

    return query


def walk(res, directory="", extension=".py"):
    """Recursive Generator that walks through the page, repo or directory and grabs files"""
    # todo make operation skip known misc directories and files, such as .github or ISSUE_TEMPLATE
    #   they take up calls pointlessly
    skipped = ".github", "docs", "__pycache__", ".idea", "locale"
    print(f" Searching {res.owner.login}/{res.name}/{directory}")
    if isinstance(res, PaginatedList):
        for repo in res:

            if not isinstance(repo, Repository):
                break

            for data in walk(repo):
                yield data

    elif isinstance(res, Repository):
        for _file in res.get_contents(directory):
            if _file.name in skipped:
                continue
            # this sleep is to attempt to make sure requests are not limited,
            # 5000 requests over an hour total 1 request every 1.3888888888889 seconds
            time.sleep(1.4)
            if _file.type == "dir":
                print(f"    {_file.name} is subdirectory, searching...\n")
                for i in walk(res, directory=_file.path):
                    yield i

            elif _file.name.endswith(extension):
                print(f"    Found candidate :{_file.name}")
                yield _file


def filtered_walk(results,
                  minimum_stars=1500,
                  minimum_file_size=1000,
                  maximum_file_size=99999):
    """A filtering function that filters repos going into walk and files coming out"""
    for repository in results:
        print("\nGetting next quality result")
        if repository.get_stargazers().totalCount > minimum_stars:
            print(
                f" Found candidate result: {repository.owner.login}/{repository.name}, meets criteria, searching...\n"
            )
            for _file in walk(repository):
                if minimum_file_size < _file.size < maximum_file_size:
                    print(
                        f"      Candidate file: {_file.name} meets criteria, returning for processing"
                    )
                    yield _file
                else:
                    print(
                        f"      Candidate file: {_file.name} does not meet criteria, moving on"
                    )
                    continue
        else:
            print(
                f" Found candidate res: {repository.owner.login}/{repository.name}, did not meet criteria, moving on\n"
            )


def collect(login: str,
            *query_strings,
            opensource_only=True,
            dump_to_ast=True,
            filter_results=True,
            batch_size=0):
    # todo need to create a batch requests collector, currently this just yields the 1000 from repos,
    #   I want it to iterate through pages so it will continue until exhaustion or until interrupt

    git = Github(login)
    print(f"Logged in as {git.get_user().login}")
    day_length = 86400
    step = 30
    end_time = time.time()
    start_time = end_time - (day_length * ((30 * 12) * 5))
    for time_frame in reversed(range(int(start_time), int(end_time), int(day_length * step))):
        query = build_query(*query_strings,
                            f" pushed:{datetime.datetime.utcfromtimestamp(time_frame - (day_length * step)).strftime('%Y-%m-%d')}..{datetime.datetime.utcfromtimestamp(time_frame).strftime('%Y-%m-%d')}",
                            opensource_only=opensource_only)
        print(f"Finding repositories with query: {query}")
        results = git.search_repositories(query=query, sort="stars", order="desc")
        print(f" Found {results.totalCount} repositories", "\n")
        processing_func = filtered_walk if filter_results else walk
        total = 0
        for i in processing_func(results):
            try:
                decoded = i.decoded_content
                yield decoded if not dump_to_ast else astor.dump_tree(ast.parse(decoded))
                total += 1
                if batch_size and total >= batch_size:
                    break

            except (SyntaxError, ValueError, AttributeError,
                    github.RateLimitExceededException) as e:
                if isinstance(e, github.RateLimitExceededException):
                    print("Github ran out of internets, waiting on delivery")
                    time.sleep(
                        3600
                    )  # waits an hour, this is to make sure rate limit is reset
                else:
                    print(
                        f"file failed to parse to ast with error: {e.__class__.__name__}, "
                        f"suggests bad data, discarding and moving on")
                    continue

        print(f"Found {total} files")
