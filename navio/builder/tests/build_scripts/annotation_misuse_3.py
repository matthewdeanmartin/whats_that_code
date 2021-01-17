from navio.builder import task


@task()
def clean():
    pass


# Referring to clean by name rather than reference.


@task(1234)
def html():
    pass
