#!/usr/bin/env bash
repo="engine_2025"
if [[ "${PWD##*/}" = $repo ]]
then
    echo "Cannot run this script in the \"engine_2025\" repo."
    echo "pwd: $PWD"
    exit 1
else
    ln -rs ../${repo}/doc/
    ln -rs ../${repo}/engine/
    ln -rs ../${repo}/Makefile
    ln -rs ../${repo}/main.py
    cp ../${repo}/game_template.py game.py
fi
