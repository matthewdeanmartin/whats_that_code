(
    export MSYS_NO_PATHCONV=1
    ./dockerw.sh run --rm --volume "$PWD":/output so_pip:latest "$@" --output=/output --logs
)
