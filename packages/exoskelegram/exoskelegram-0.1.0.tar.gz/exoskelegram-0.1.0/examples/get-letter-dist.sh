#/bin/bash
IFS=$'\n'

rm /tmp/wl

for x in a b c d e f g h i j k l m n o p q r s t u v w x y z; do
    echo `grep -ic $x /usr/share/dict/words` $x >> /tmp/wl
done

sort -rn /tmp/wl
