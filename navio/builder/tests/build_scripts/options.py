from navio.builder import task

tasks_run = []


@task()
def clean():
    tasks_run.append("clean")


@task(clean)
def html():
    "Generate HTML."
    tasks_run.append("html")


@task(clean, ignore=True)
def images():
    """Prepare images.

    Should be ignored."""

    raise Exception("This task should have been ignored.")


@task(clean, html, images)
def android():
    "Package Android app."

    tasks_run.append("android")
