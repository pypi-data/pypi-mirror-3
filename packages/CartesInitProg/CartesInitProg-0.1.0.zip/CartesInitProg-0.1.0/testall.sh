#! /bin/sh

for FILE in `/bin/ls Cartes/*.py`
do
    echo -n "Testing $FILE... "
    python $FILE
    echo "done."
done

# eof