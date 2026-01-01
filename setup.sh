#!/usr/bin/env bash
repo="engine_2025"
if [[ "${PWD##*/}" = $repo ]]
then
    echo "Cannot run this script in the \"engine_2025\" repo."
    echo "pwd: $PWD"
    exit 1
else
    # Create an empty 'doc/' folder for the project
    mkdir -p doc
    # Create a 'font/' folder for the project
    mkdir -p fonts
    # Link to the font used in the debug HUD
    ln -rs ../${repo}/fonts/ProggyClean.ttf fonts/
    # Link to the engine, entry point, make recipes, and Python config files
    ln -rs ../${repo}/engine/ .
    ln -rs ../${repo}/main.py .
    ln -rs ../${repo}/Makefile .
    ln -rs ../${repo}/requirements.txt .
    ln -rs ../${repo}/.mypy.ini .
    ln -rs ../${repo}/.pylintrc .
    ln -rs ../${repo}/.pytest.ini .
    # Copy in a starting point for the game code
    touch README.md
    cp -i ../${repo}/game.py .
fi
