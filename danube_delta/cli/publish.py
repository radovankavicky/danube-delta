
import re

import click
import requests

from . import blog
from .helpers import choose_commit_emoji, run, header, abort


@blog.command()
@click.pass_context
def publish(context):
    """Saves changes and sends them to GitHub"""

    header('Recording changes...')
    run('git add -A')

    header('Displaying changes...')
    command = 'git -c color.status=always status'
    status = run(command.stdout)
    click.echo(status)

    if not click.confirm('\nContinue publishing'):
        run('git reset HEAD --')
        abort(context)

    header('Saving changes...')
    run('git commit -m "{message}"', format={
        'message': 'Publishing {}'.format(choose_commit_emoji())
    }, redir=True)

    header('Pushing to GitHub...')
    branch = get_branch()
    run('git push origin {branch}:{branch}', format={
        'branch': branch,
    }, redir=True)

    pr_link = get_pr_link(branch)
    if pr_link:
        click.launch(pr_link)


def get_pr_link(branch):
    repo_slug = get_repo_slug()
    repo_url = 'https://api.github.com/repos/{}'.format(repo_slug)

    res = requests.get(repo_url)
    res.raise_for_status()
    repo_info = res.json()

    if not repo_info['fork']:
        return None

    return 'https://github.com/{}/compare/master...{}:{}'.format(
        repo_info['parent']['full_name'],
        repo_info['owner']['login'],
        branch,
    )


def get_repo_slug():
    url = run('git remote get-url origin')
    return re.search(r'github\.com[\:\/](.+)\.git$', url).group(1)


def get_branch():
    branches = run('git branch --no-color')
    return re.search(r'\*\s+(\S+)', branches).group(1)
