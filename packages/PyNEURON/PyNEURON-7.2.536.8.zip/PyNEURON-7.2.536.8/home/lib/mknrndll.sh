
# Cygpath think neuronhome to be '/', so we use this hack
N="`$1/bin/cygpath -u $1/..`""`$1/bin/basename $1`"
PATH="$N/bin:$N/lib/gcc/i686-pc-cygwin/3.4.4"
export PATH
export N
NEURONHOME=$N
export NEURONHOME

$N/bin/rm -f nrnmech.dll
$N/bin/sh $N/lib/mknrndl2.sh

echo ""
if [ -f nrnmech.dll ] ; then
echo "nrnmech.dll was built successfully."
else
echo "There was an error in the process of creating nrnmech.dll"
fi
echo "Press Return key to exit"
read a

