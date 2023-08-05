import os

def get_tracked_rst_files(repo=None):
    """Returns a list of .rst files that are under version control"""

    from mercurial.match import match

    if repo is None:
        repo = get_repo()

    m = match(repo, '.', ('*.rst',), {}, default='relglob')
    tracked = filter(lambda f: f in repo.dirstate, repo[None].walk(m))
    return [os.path.join(repo.root, f) for f in tracked]

def get_untracked_rst_files(repo=None):
    """
    Returns a list of all .rst files that are not currently tracked by
    Mercurial
    """

    if repo is None:
        repo = get_repo()

    tracked = get_tracked_rst_files(repo)
    all_files = []

    for path, dirs, files in os.walk(repo.root):
        for d in dirs:
            if d.startswith('.'):
                dirs.remove(d)

        rst_files = filter(lambda s: s.endswith('.rst'), files)

        for f in rst_files:
            full_path = os.path.join(path, f)
            all_files.append(full_path)

    untracked = filter(lambda f: f not in tracked, all_files)
    source = os.path.join(repo.root, 'source')
    return [f.replace(source, '').strip('/') for f in untracked]

def get_repo(path=None):
    from mercurial.cmdutil import findrepo
    from mercurial import hg
    from mercurial.ui import ui

    if path is None:
        path = os.getcwd()

    repo_root = findrepo(path)
    repo = hg.repository(ui(), path=repo_root)
    return repo

