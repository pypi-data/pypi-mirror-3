#!/bin/bash 

# start with ./use18ndude.sh 

PRODUCT="vs.event"

# if you want to add new language, replace language code, 
# uncomment and run these two commands: 
# mkdir -p locales/en/LC_MESSAGES/
# touch locales/en/LC_MESSAGES/$PRODUCT.po 

i18ndude rebuild-pot --pot locales/$PRODUCT.pot --create $PRODUCT ./
i18ndude sync --pot locales/$PRODUCT.pot locales/*/LC_MESSAGES/$PRODUCT.po 

