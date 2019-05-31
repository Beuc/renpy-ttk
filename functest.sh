#!/bin/bash -ex

projectpath=`mktemp -d`
mkdir "$projectpath/game"
cp -a test/input/*.rpy "$projectpath/game"

renpy.sh . tl2pot "$projectpath"

msgmerge -v test/input/testtl-fr_FR.po game.pot -o "$projectpath/testtl-fr_FR.po"

renpy.sh . mo2tl "$projectpath" "$projectpath/testtl-fr_FR.po" french
rm -f "$projectpath/game/tl/french/common.rpy"
sed -i -e 's/# TODO: Translation updated at .*/# TODO: Translation updated at XXXX-XX-XX XX:XX/' "$projectpath/game/tl/french/"*.rpy

diff -ru test/output_expected $projectpath/game/tl/french

# TODO: check result but PO editors' reformatting makes it difficult
renpy.sh . tl2po "$projectpath" french

rm -f game.pot french.po
rm -rf "$projectpath"
