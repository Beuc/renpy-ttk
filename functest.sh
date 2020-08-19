#!/bin/bash -ex

projectpath=`mktemp -d`
mkdir "$projectpath/game"
cp -a test/input/*.rpy "$projectpath/game"

renpy.sh . tl2pot "$projectpath"

msgmerge -v test/input/testtl-fr_FR.po game.pot -o "$projectpath/testtl-fr_FR.po"

renpy.sh . mo2tl "$projectpath" "$projectpath/testtl-fr_FR.po" french

# obsolete entry
cat <<EOF >> "$projectpath/game/tl/french/script.rpy"
# game/script.rpy:1
translate french start_baaaaaad:

    # e "obsolete entry"
    e "entrée obsolète"

# game/script.rpy:2
# OBSOLETE
translate french start_badddddd:

    # e "obsolete entry 2"
    e "entrée obsolète 2"

EOF

renpy.sh . mo2tl "$projectpath" "$projectpath/testtl-fr_FR.po" french

rm -f "$projectpath/game/tl/french/common.rpy" "$projectpath/game/tl/french/"*.rpyc
sed -i -e 's/# TODO: Translation updated at .*/# TODO: Translation updated at XXXX-XX-XX XX:XX/' "$projectpath/game/tl/french/"*.rpy

diff -ru test/output_expected $projectpath/game/tl/french

sed -i -e 's/^    "skipped translation"/    pass/' "$projectpath/game/tl/french/script.rpy"
# TODO: check result but PO editors' reformatting makes it difficult
renpy.sh . tl2po "$projectpath" french

rm -f game.pot french.po
rm -rf "$projectpath"
