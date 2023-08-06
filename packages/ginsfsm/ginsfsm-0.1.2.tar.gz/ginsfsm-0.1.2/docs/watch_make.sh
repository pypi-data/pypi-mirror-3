OLD=`stat -t \
    index.rst \
    api.rst \
    glossary.rst \
    src/api/gaplic.rst \
    src/api/gobj.rst \
    src/api/smachine.rst \
    src/api/c_timer.rst \
    src/api/c_sock.rst \
    src/api/c_srv_sock.rst \
    src/api/c_connex.rst \
    src/core/core.rst \
    src/core/between.rst \
    src/examples/examples.rst \
    ../ginsfsm/gaplic.py \
    ../ginsfsm/gobj.py \
    ../ginsfsm/smachine.py \
    ../ginsfsm/c_timer.py \
    ../ginsfsm/c_sock.py \
    ../ginsfsm/c_srv_sock.py \
    ../ginsfsm/examples/example1.py \
    ../ginsfsm/c_connex.py`

make html
while true
do
NEW=`stat -t \
    index.rst \
    api.rst \
    glossary.rst \
    src/api/gaplic.rst \
    src/api/gobj.rst \
    src/api/smachine.rst \
    src/api/c_timer.rst \
    src/api/c_sock.rst \
    src/api/c_srv_sock.rst \
    src/api/c_connex.rst \
    src/core/core.rst \
    src/core/between.rst \
    src/examples/examples.rst \
    ../ginsfsm/gaplic.py \
    ../ginsfsm/gobj.py \
    ../ginsfsm/smachine.py \
    ../ginsfsm/c_timer.py \
    ../ginsfsm/c_sock.py \
    ../ginsfsm/c_srv_sock.py \
    ../ginsfsm/examples/example1.py \
    ../ginsfsm/c_connex.py`

if [ "$NEW" != "$OLD" ]; then
    OLD=$NEW
    echo "changed"
    make html
    ##make latexpdf
    ##cp _build/latex/AdministracionStratus.pdf _build/html/_static/
#else
    #echo "NOT changed"
fi
sleep 1
done
