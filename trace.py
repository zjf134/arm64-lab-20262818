"""Run inside GDB: source trace.py. Records real instruction-level state."""
import csv
import json
import os
from pathlib import Path
import time
import gdb

out = Path('logs')
out.mkdir(exist_ok=True)
signals = Path('/media/sf_shared/arm64-lab-20262818')
capture = os.environ.get('ARM64_CAPTURE') == '1'

def reg(name):
    return int(gdb.parse_and_eval('$' + name))

def state():
    r = {k: reg(k) for k in ['pc', 'sp', 'x29', 'x30', 'x0', 'x1']}
    r['instruction'] = gdb.execute('x/i $pc', to_string=True).strip()
    r['stack_address'] = r['sp']
    r['stack_hex'] = bytes(gdb.selected_inferior().read_memory(r['sp'], 96)).hex()
    return r

def snapshot(name, title, command='disassemble f'):
    if not capture:
        return
    gdb.execute('shell clear')
    gdb.write(title + '\n')
    gdb.execute(command)
    gdb.execute('info registers pc sp x29 x30 w0 w1')
    gdb.execute('x/8gx $sp')
    gdb.execute('x/i $pc')
    (signals / (name + '.ready')).write_text(title)
    deadline = time.time() + 180
    while not (signals / (name + '.go')).exists():
        if time.time() > deadline:
            raise RuntimeError('Screenshot timeout: ' + name)
        time.sleep(0.2)

gdb.execute('set pagination off')
gdb.execute('set confirm off')
gdb.execute('set style enabled off')
gdb.execute('set print address on')
gdb.execute('set architecture aarch64')
gdb.execute('target remote 127.0.0.1:12368')
gdb.execute('break *main')
gdb.execute('continue')
addresses = {n: int(gdb.parse_and_eval('(void*)' + n)) for n in ['main', 'f', 'g']}
disassembly = {n: gdb.execute('disassemble /r ' + n, to_string=True) for n in addresses}
main_instructions = gdb.selected_frame().architecture().disassemble(addresses['main'], addresses['main'] + 28)
f_instructions = gdb.selected_frame().architecture().disassemble(addresses['f'], addresses['f'] + 48)
g_instructions = gdb.selected_frame().architecture().disassemble(addresses['g'], addresses['g'] + 24)
valid = {v['addr'] for v in main_instructions + f_instructions + g_instructions}
records = []
entry = state()
f_entry_sp = None
for step in range(100):
    before = state()
    if before['pc'] not in valid:
        break
    if before['pc'] == addresses['f']:
        f_entry_sp = before['sp']
    gdb.execute('stepi', to_string=True)
    after = state()
    records.append({'step': step + 1, 'before': before, 'after': after})
    gdb.write('STEP %02d %s\n' % (step + 1, before['instruction']))
    if after['pc'] == addresses['f'] + 20:
        snapshot('02-gdb-frame', 'GDB: f frame formed; x=8 at SP+28, i=18 at SP+44')
        assert int.from_bytes(bytes(gdb.selected_inferior().read_memory(after['sp'] + 28, 4)), 'little') == 8
        assert int.from_bytes(bytes(gdb.selected_inferior().read_memory(after['sp'] + 44, 4)), 'little') == 18
    if after['pc'] == addresses['g']:
        snapshot('03-gdb-call', 'GDB: BL g wrote X30; SP unchanged by BL', 'disassemble g')
        assert before['sp'] == after['sp']
        assert after['x30'] == before['pc'] + 4
    if after['pc'] == addresses['main'] + 20:
        snapshot('04-gdb-return', 'GDB: f returned 29; main added 1; W0=30', 'disassemble main')
        assert after['x0'] == 30
        assert after['sp'] == f_entry_sp
else:
    raise RuntimeError('Trace exceeded instruction limit')

assert len(records) == 25, len(records)
assert any(r['before']['pc'] == addresses['f'] + 44 for r in records)
data = {'addresses': addresses, 'entry': entry, 'f_entry_sp': f_entry_sp,
        'disassembly': disassembly, 'records': records}
(out / 'trace.json').write_text(json.dumps(data, indent=2) + '\n')
with (out / 'trace.csv').open('w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['step', 'instruction', 'PC_before', 'PC_after', 'SP_before', 'SP_after',
                     'FP_after', 'LR_after', 'W0_after', 'W1_after'])
    for r in records:
        b, a = r['before'], r['after']
        writer.writerow([r['step'], b['instruction'], hex(b['pc']), hex(a['pc']), hex(b['sp']),
                         hex(a['sp']), hex(a['x29']), hex(a['x30']), a['x0'] & 0xffffffff, a['x1'] & 0xffffffff])
(out / 'disassembly.txt').write_text('\n'.join(disassembly.values()))
gdb.execute('continue')
gdb.write('TRACE_PASS: 25 instructions, f frame restored, main result=30\n')
