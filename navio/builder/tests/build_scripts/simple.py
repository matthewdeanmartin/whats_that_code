#!/usr/bin/python

from navio.builder import task


@task()
def clean():
    """Clean build directory."""

    print("clean")


@task()
def html():
    """Generate HTML."""

    print("html")


@task()
def images():
    """Prepare images."""

    print("images")


@task()
def android():
    """Package Android app."""

    print("android")


@task()
def ios():
    """Package iOS app."""

    print("ios")


def some_utility_method():
    """Some utility method."""

    print("some utility method")


__DEFAULT__ = ios
