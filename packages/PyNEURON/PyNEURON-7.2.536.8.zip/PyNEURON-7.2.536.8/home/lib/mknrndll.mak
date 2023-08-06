
EXTRA_CYGWIN = -L$N/i686-pc-mingw32/sys-root/mingw/lib -L$N/lib/gcc/i686-pc-cygwin/3.4.4 \
    -I$N/i686-pc-mingw32/sys-root/mingw/include
EXTRA_FLAGS =  $(EXTRA_CYGWIN)

GCC = $N/bin/gcc-3
CFLAGS = -mno-cygwin \
-DDLL_EXPORT -DPIC \
-I$N/src/scopmath -I$N/src/nrnoc -I$N/src/oc \
$(EXTRA_FLAGS)


# to handle variations of filename extensions
.SUFFIXES: .o .mod .moD .mOd .mOD .Mod .MoD .MOd .MOD
.PRECIOUS: %.c

%.o : %.mod

%.c : %.mod
	nocmodl $*

%.o : %.c
	$(GCC) $(CFLAGS) -c $*.c

# additional rules to handle variations of filename extensions
%.c : %.moD
	$(GCC) $(CFLAGS) -c $*.c

%.c : %.mOd
	$(GCC) $(CFLAGS) -c $*.c

%.c : %.mOD
	$(GCC) $(CFLAGS) -c $*.c

%.c : %.Mod
	$(GCC) $(CFLAGS) -c $*.c

%.c : %.MoD
	$(GCC) $(CFLAGS) -c $*.c

%.c : %.MOd
	$(GCC) $(CFLAGS) -c $*.c

%.c : %.MOD
	$(GCC) $(CFLAGS) -c $*.c

%.o : %.moD

%.o : %.mOd

%.o : %.mOD

%.o : %.Mod

%.o : %.MoD

%.o : %.MOd

%.o : %.MOD

mod_func.o: mod_func.c
	$(GCC) $(CFLAGS) -c $*.c

#nrnmech.dll: mod_func.o $(MODOBJFILES)
#	ld -d -S -x -r -o nrnmech.dll mod_func.o $(MODOBJFILES) -L$N/lib -lscpmt

nrnmech.dll: mod_func.o $(MODOBJFILES)
	$(GCC) $(EXTRA_FLAGS) -mno-cygwin -Wl,--enable-auto-import -shared -o nrnmech.dll mod_func.o $(MODOBJFILES) \
  -L$N/bin -lnrniv  
	$N/bin/rebase -b 0x64000000 -v nrnmech.dll

#nm nrnmech.dll | mkdll -u > nrnmech.h #will give a list of neuron.exe names
#required by nrnmech.dll

#mod_func.o $(MODOBJFILES): $(N)/bin/nrniv.exe


