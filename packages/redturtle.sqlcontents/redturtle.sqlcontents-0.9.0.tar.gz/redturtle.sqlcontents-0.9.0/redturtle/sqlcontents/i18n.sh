#!/bin/sh

DOMAIN='redturtle.sqlcontents'

test -d locales || mkdir locales
test -d locales/it || mkdir locales/it
test -d locales/it/LC_MESSAGES || mkdir locales/it/LC_MESSAGES
test -f locales/${DOMAIN}.pot || touch locales/${DOMAIN}.pot
test -f locales/manual.pot || touch locales/manual.pot
test -f locales/it/LC_MESSAGES/${DOMAIN}.po || cp locales/${DOMAIN}.pot locales/it/LC_MESSAGES/${DOMAIN}.po

i18ndude rebuild-pot --pot locales/${DOMAIN}.pot --create ${DOMAIN} --merge locales/manual.pot .

i18ndude sync --pot locales/${DOMAIN}.pot locales/*/LC_MESSAGES/${DOMAIN}.po

# Compile po files
for lang in `find locales -mindepth 1 -maxdepth 1 -type d`; do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${DOMAIN}.mo $lang/LC_MESSAGES/${DOMAIN}.po
    fi
done
