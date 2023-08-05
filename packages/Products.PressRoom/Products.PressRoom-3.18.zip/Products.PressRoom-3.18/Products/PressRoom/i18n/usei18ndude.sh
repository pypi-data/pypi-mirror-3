#!/bin/bash 

PRODUCT="pressroom"
DOMAIN="pressroom"

i18ndude rebuild-pot --pot $PRODUCT.pot --create $DOMAIN --merge manual.pot ../

i18ndude sync --pot $PRODUCT.pot $PRODUCT-??.po;
i18ndude sync --pot $PRODUCT-plone.pot $PRODUCT-plone-??.po


