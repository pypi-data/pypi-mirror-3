#!/bin/sh

DOMAIN='pcommerce.payment.ogone'

i18ndude rebuild-pot --pot ./${DOMAIN}.pot --merge ./additional.pot --create ${DOMAIN} ..
i18ndude sync --pot ./${DOMAIN}.pot ./*/LC_MESSAGES/${DOMAIN}.po

