#!/bin/bash
# Use only for generating .po; fill .pot file manually!

DOMAIN=plone

#i18ndude merge --pot i18n/${DOMAIN}.pot --merge i18n/${DOMAIN}-manual.pot
i18ndude sync --pot ${DOMAIN}.pot ${DOMAIN}-??.po
