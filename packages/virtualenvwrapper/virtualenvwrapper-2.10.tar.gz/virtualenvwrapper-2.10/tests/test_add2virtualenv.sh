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
}

setUp () {
    echo
    rm -f "$test_dir/catch_output"
}

test_add2virtualenv () {
    mkvirtualenv "pathtest" >/dev/null 2>&1
    full_path=$(pwd)
    add2virtualenv "$full_path"
    cdsitepackages
    # Check contents of path file
    path_file="./_virtualenv_path_extensions.pth"
    assertTrue "No $full_path in $(cat $path_file)" "grep -q $full_path $path_file"
    assertTrue "No path insert code in $(cat $path_file)" "grep -q sys.__egginsert $path_file"
    # Check the path we inserted is actually at the top
    expected="$full_path"
    actual=$($WORKON_HOME/pathtest/bin/python -c "import sys; print sys.path[1]")
    assertSame "$expected" "$actual"
    # Make sure the temporary file created
    # during the edit was removed
    assertFalse "Temporary file ${path_file}.tmp still exists" "[ -f ${path_file}.tmp ]"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_relative () {
    mkvirtualenv "pathtest" >/dev/null 2>&1
    parent_dir=$(dirname $(pwd))
    base_dir=$(basename $(pwd))
    add2virtualenv "../$base_dir"
    cdsitepackages
    path_file="./_virtualenv_path_extensions.pth"
    assertTrue "No $parent_dir/$base_dir in \"`cat $path_file`\"" "grep -q \"$parent_dir/$base_dir\" $path_file"
    cd - >/dev/null 2>&1
}

test_add2virtualenv_delete () {
    path_file="./_virtualenv_path_extensions.pth"
    mkvirtualenv "pathtest" >/dev/null 2>&1
    cdsitepackages
    # Make sure it was added
    add2virtualenv "/full/path"
    assertTrue "No $full_path in $(cat $path_file)" "grep -q $full_path $path_file"
    # Remove it and verify that change
    add2virtualenv -d "/full/path"
    assertFalse "/full/path in `cat $path_file`" "grep -q /full/path $path_file"
    cd - >/dev/null 2>&1
}


. "$test_dir/shunit2"
