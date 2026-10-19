CC = aarch64-linux-gnu-gcc
AS = aarch64-linux-gnu-as
LD = aarch64-linux-gnu-ld
CFLAGS = -O0 -g3 -fno-omit-frame-pointer -fno-stack-protector -fno-pie
LDFLAGS = -static -no-pie

.PHONY: all check clean
all: build/hello build/c_calls_asm build/week040120262818 build/main.s

build:
	mkdir -p build

build/hello.o: hello.s | build
	$(AS) -g -o $@ $<

build/hello: build/hello.o
	$(LD) -o $@ $<

build/c_calls_asm: c_calls_asm.c asm_functions.s | build
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

build/week040120262818: week040120262818.c | build
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

build/main.s: week040120262818.c | build
	$(CC) $(CFLAGS) -S -o $@ $<

check: all
	python3 check.py

clean:
	rm -f build/hello.o build/hello build/c_calls_asm build/week040120262818 build/main.s
