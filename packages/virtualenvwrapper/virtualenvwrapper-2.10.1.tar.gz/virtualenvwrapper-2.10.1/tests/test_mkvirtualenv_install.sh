#!/bin/sh

#set -x

test_dir=$(cd $(dirname $0) && pwd)

export WORKON_HOME="$(echo ${TMPDIR:-/tmp}/WORKON_HOME | sed 's|//|/|g')"

oneTimeSetUp() {
    rm -rf "$WORKON_HOME"
    mkdir -p "$WORKON_HOME"
    source "$test_dir/../virtualenvwrapper.sh"
}

oneTimeTearDown() {
    rm -rf "$WORKON_HOME"
    rm -f "$test_dir/requirements.txt"
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

test_single_package () {
    mkvirtualenv -i commandlineapp "env4" >/dev/null 2>&1
    installed=$(pip freeze)
    assertTrue "CommandLineApp not found in $installed" "echo $installed | grep CommandLineApp"
}

test_multiple_packages () {
    mkvirtualenv -i commandlineapp -i csvcat "env4" >/dev/null 2>&1
    installed=$(pip freeze)
    assertTrue "CommandLineApp not found in $installed" "echo $installed | grep CommandLineApp"
    assertTrue "csvcat not found in $installed" "echo $installed | grep csvcat"
}

. "$test_dir/shunit2"
