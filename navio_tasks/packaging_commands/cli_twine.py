"""
Upload to pypi. Pypi is public, don't do that unless you mean to.
"""
import os

from navio_tasks.cli_commands import check_command_exists, execute


def do_upload_package() -> None:
    """
    Send to private package repo
    """
    # devpi use  http://localhost:3141
    # login with root...
    # devpi login root --password=
    # get indexes
    # devpi use -l
    # make an index
    # devpi index -c dev bases=root/pypi
    # devpi use root/dev

    # Must register (may go away with newer version of devpi), must be 1 file!
    # twine register --config-file .pypirc -r devpi-root -u root
    # -p PASSWORD dist/search_service-0.1.0.zip
    # can be all files!
    # twine upload --config-file .pypirc -r devpi-root -u root -p PASSWORD dist/*

    # which is installable using...
    #  pip install search-service --index-url=http://localhost:3141/root/dev/

    check_command_exists("devpi")
    password = os.environ["DEVPI_PASSWORD"]
    any_zip = [file for file in os.listdir("dist") if file.endswith(".zip")][0]
    register_command = (
        "twine register --config-file .pypirc -r devpi-root -u root"
        f" -p {password} dist/{any_zip}"
    )
    upload_command = (
        "twine upload --config-file .pypirc -r devpi-root "
        f"-u root -p {password} dist/*"
    )

    execute(*(register_command.strip().split(" ")))
    execute(*(upload_command.strip().split(" ")))
