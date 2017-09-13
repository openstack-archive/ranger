from orm.services.resource_distributor.rds.sot.git_sot import git_sot

sot_type = ""
local_repository_path = ""
relative_path_format = ""
file_name_format = ""
commit_message_format = ""
commit_user = ""
commit_email = ""
git_server_url = ""
git_type = ""


def get_sot():
    """Return the correct SoT implementation according to sot_type"""

    if sot_type == 'git':
        git_sot.GitSoT.local_repository_path = local_repository_path
        git_sot.GitSoT.relative_path_format = relative_path_format
        git_sot.GitSoT.file_name_format = file_name_format
        git_sot.GitSoT.commit_message_format = commit_message_format
        git_sot.GitSoT.commit_user = commit_user
        git_sot.GitSoT.commit_email = commit_email
        git_sot.GitSoT.git_server_url = git_server_url
        git_sot.GitSoT.git_type = git_type
        sot = git_sot.GitSoT()
        return sot
    else:
        raise RuntimeError("Invalid SoT implementation!!")
