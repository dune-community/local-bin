
export BASEDIR=/home/r_milk01/projekte/uni/dune/docker/gdt-super/local/bin/localscripts/test/data
export INSTALL_PREFIX=/tmp
export PATH=/tmp/bin:$PATH
export LD_LIBRARY_PATH=/tmp/lib64:/tmp/lib:$LD_LIBRARY_PATH
export PKG_CONFIG_PATH=/tmp/lib64/pkgconfig:/tmp/lib/pkgconfig:/tmp/share/pkgconfig:$PKG_CONFIG_PATH
export CC=nosuch.compiler
export CXX=g++
export F77=gfortran
[ -e /tmp/bin/activate ] && . /tmp/bin/activate
export OMP_NUM_THREADS=1
