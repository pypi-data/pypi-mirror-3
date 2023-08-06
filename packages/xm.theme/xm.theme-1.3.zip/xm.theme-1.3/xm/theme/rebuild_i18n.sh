#!/bin/sh
PRODUCTNAME=xm.theme
I18NDOMAIN=$PRODUCTNAME

# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
i18ndude sync --pot locales/${PRODUCTNAME}.pot locales/*/LC_MESSAGES/${PRODUCTNAME}.po

# Only needed for Plone 3.0, not 3.1:
for lang in locales/*; do
    if test -d lang; then
        msgfmt -o lang/LC_MESSAGES/${PRODUCTNAME}.mo lang/LC_MESSAGES/${PRODUCTNAME}.po
    fi
done
