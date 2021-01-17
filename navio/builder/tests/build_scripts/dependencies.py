from navio.builder import task


@task()
def clean():
    """Clean build directory."""

    print("clean")


@task(clean)
def html():
    """Generate HTML."""

    print("html")


@task(clean)
def images():
    """Prepare images."""

    print("images")


@task(clean, html, images)
def android():
    """Package Android app."""

    print("android")


@task(clean, html, images)
def ios():
    """Package iOS app."""

    print("ios")


def some_utility_method():
    """Some utility method."""

    print("some utility method")
