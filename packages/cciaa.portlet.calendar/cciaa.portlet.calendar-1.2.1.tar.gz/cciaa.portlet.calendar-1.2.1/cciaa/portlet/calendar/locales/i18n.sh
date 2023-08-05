#!/bin/sh

DOMAIN='cciaa.portlet.calendar'

i18ndude rebuild-pot --pot ./${DOMAIN}.pot --create ${DOMAIN} ..

i18ndude sync --pot ./${DOMAIN}.pot ./*/LC_MESSAGES/${DOMAIN}.po

