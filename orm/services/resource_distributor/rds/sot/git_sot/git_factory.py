from git_gittle import GitGittle
from git_native import GitNative


def get_git_impl(git_type):
    """Return the correct Git implementation according to git_type"""
    git_impl = None
    if git_type == 'gittle':
        git_impl = GitGittle()
    elif git_type == 'native':
        git_impl = GitNative()
    else:
        raise RuntimeError("Invalid Git implementation!!")

    return git_impl
