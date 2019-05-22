#!/bin/bash -ex

projectpath=`mktemp -d`
mkdir "$projectpath/game"
cp -a test/input/*.rpy "$projectpath/game"

./tl2pot.py "$projectpath"

msgmerge test/input/testtl-fr_FR.po game.pot -o "$projectpath/testtl-fr_FR.po"

./mo2tl.py "$projectpath" "$projectpath/testtl-fr_FR.po" french
rm -f "$projectpath/game/tl/french/common.rpy"
sed -i -e 's/# TODO: Translation updated at .*/# TODO: Translation updated at XXXX-XX-XX XX:XX/' "$projectpath/game/tl/french/"*.rpy

diff -ru test/output_expected $projectpath/game/tl/french

rm -f game.pot
rm -rf "$projectpath"
