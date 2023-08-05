#!/bin/sh
I18NDOMAIN='simpleattachment'

# Synchronise the .pot with the templates.
#i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --merge locales/${I18NDOMAIN}-manual.pot --create ${I18NDOMAIN} .
i18ndude rebuild-pot --pot locales/${I18NDOMAIN}.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with all .po files
for po in locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot locales/${I18NDOMAIN}.pot $po
done