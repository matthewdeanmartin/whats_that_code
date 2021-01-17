#!/usr/bin/python

from navio.builder import task

tasks_run = []


@task()
def clean(directory="/tmp"):
    tasks_run.append("clean[%s]" % directory)


@task(clean)
def html():
    tasks_run.append("html")


@task()
def tests(*test_names):
    tasks_run.append("tests[%s]" % ",".join(test_names))


@task(clean)
def copy_file(from_, to, fail_on_error="True"):
    tasks_run.append(f"copy_file[{from_},{to},{fail_on_error}]")


@task(clean)
def start_server(port="80", debug="True"):
    tasks_run.append(f"start_server[{port},{debug}]")


@task(ignore=True)
def ignored(file, contents):
    tasks_run.append(f"append_to_file[{file},{contents}]")


@task(clean, ignored)
def append_to_file(file, contents):
    tasks_run.append(f"append_to_file[{file},{contents}]")


@task(ignored)
def echo(*args, **kwargs):
    args_str = []
    if args:
        args_str.append(",".join(args))
    if kwargs:
        args_str.append(
            ",".join("{}={}".format(kw, kwargs[kw]) for kw in sorted(kwargs))
        )

    tasks_run.append("echo[%s]" % ",".join(args_str))
