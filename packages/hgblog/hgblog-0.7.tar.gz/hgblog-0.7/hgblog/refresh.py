import os

def refresh(repo=None):
    """Calls on Sphinx to turn our .rst files into pretty HTML"""

    from sphinx.cmdline import main as sphinxify
    from hgblog.utils import get_repo, get_tracked_rst_files

    if repo is None:
        repo = get_repo()

    files_to_consider = get_tracked_rst_files(repo)

    # tell Sphinx to HTML-ize the .rst files we found
    args = [
        '-bdirhtml',
        '-d%s' % os.path.join(repo.root, 'build', 'doctrees'),
        os.path.join(repo.root, 'source'),
        os.path.join(repo.root, 'build', 'html'),
    ] + files_to_consider
    sphinxify(args)

