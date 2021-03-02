PREFIX := ${DESTDIR}/usr
BINDIR := ${PREFIX}/bin
CC = gcc
CFLAGS = -Wall -Werror -O2 -g
OBJS = dev_test

all: $(OBJS)

dev_test: dev_test.c dev.o

%: %.o
	$(CC) -o $@ $< $(CFLAGS)

%: %.c
	$(CC) -o $@ $^ $(LIBS) $(CFLAGS)

%: %.sh
	cp -f $< $@
	chmod +x $@

install: install_objs
	
install_objs: $(OBJS)
	mkdir -p "${BINDIR}/"
	for obj in ${OBJS}; do \
	    install -m755 "$$obj" "${BINDIR}/"; \
	done

clean:
	rm -f $(OBJS)
