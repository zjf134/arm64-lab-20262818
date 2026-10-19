import subprocess

for name, expected_code, expected_text in [
    ('hello', 0, 'Hello World! ARM64 20262818\n'),
    ('c_calls_asm', 0, 'C -> ASM: asm_add18(8) = 26\nC -> ASM -> C: asm_call_c(8) = 29\n'),
    ('week040120262818', 30, ''),
]:
    p = subprocess.run(['qemu-aarch64', 'build/' + name], capture_output=True, text=True)
    print(p.stdout, end='')
    assert p.returncode == expected_code, (name, p.returncode, p.stderr)
    assert p.stdout == expected_text, (name, p.stdout)
    print(f'PASS {name}: exit={p.returncode}')
