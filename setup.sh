#!/usr/bin/env bash
repo="engine_2025"
if [[ "${PWD##*/}" = $repo ]]
then
    echo "Cannot run this script in the \"engine_2025\" repo."
    echo "pwd: $PWD"
    exit 1
else
    ln -rs ../${repo}/doc/ .
    ln -rs ../${repo}/engine/ .
    ln -rs ../${repo}/Makefile .
    ln -rs ../${repo}/main.py .
    ln -rs ../${repo}/.mypy.ini .
    ln -rs ../${repo}/.pylintrc .
    ln -rs ../${repo}/.pytest.ini .
    cp -i ../${repo}/game.py .
fi
