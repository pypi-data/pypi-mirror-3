F2PY = f2py
PYF_FLAGS = --overwrite-signature
CFLAGS = --fcompiler=gnu95
RM = rm

MODULE = fortran_utils
${MODULE}: ${MODULE}.so
${MODULE}.so: ${MODULE}.pyf
	${F2PY} ${CFLAGS} -c ${MODULE}.pyf ${MODULE}.f90
${MODULE}.pyf: ${MODULE}.f90
	${F2PY} ${PYF_FLAGS} ${MODULE}.f90 -m ${MODULE} -h ${MODULE}.pyf

.PHONY: clean
clean:
	${RM} -f ${MODULE}.pyf

