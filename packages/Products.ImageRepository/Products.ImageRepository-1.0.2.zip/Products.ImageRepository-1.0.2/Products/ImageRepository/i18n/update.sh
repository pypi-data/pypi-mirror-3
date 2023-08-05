#!/bin/bash

if ! which i18ndude > /dev/null; then
    echo "You need to install the i18ndude utility first: easy_install i18ndude"
    exit 1
fi

# Access the real directory of the current file
cd -P `dirname $0`

PRODUCT_DIR="`dirname $PWD`"
PRODUCT=`basename $PRODUCT_DIR`
I18NDOMAIN=plone
POT=$PRODUCT-plone.pot
MANUAL=$PRODUCT-plone-manual.pot
LOG=rebuild.log

echo -n "Rebuilding POT files, this can take a while..."

# Rebuild the main POT file
i18ndude rebuild-pot \
  --pot $POT \
  --create $I18NDOMAIN \
  --merge $MANUAL \
  $PRODUCT_DIR/skins/  > $LOG 2>&1

# Made paths relative to the product directory
sed -ri "s,$PRODUCT_DIR,\.,g" $POT

echo " done. Full report at $LOG."

echo "Now updating the PO files:"

# Proceed with the PO syncing
for PO in *.po ; do
    i18ndude sync --pot $POT $PO
done
