from hgblog.refresh import refresh

def htmlize_articles(ui, repo, **kwargs):
    """Calls on Sphinx to turn our .rst files into pretty HTML"""

    refresh(repo)

