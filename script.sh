set -e
trap 'echo "fatal: $LINENO: '"'"'$BASH_COMMAND'"'"' returned status code $?"' ERR
echo hi there
false
echo hi again
