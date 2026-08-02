"""
T-036 heartbeat gap analysis script.
Run: py -3.13 research/results/T-036_raw/heartbeat_gap_check.py
Read-only: does not modify any files.
"""
import re
import sys
from datetime import datetime

LOG_PATH = r'user_data\logs\dryrun.log'

def main():
    with open(LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    # Find all heartbeat lines with PID=52788
    hb_lines = [l for l in lines if 'Bot heartbeat' in l and 'PID=52788' in l]
    print(f'Total heartbeat lines with PID=52788: {len(hb_lines)}')

    if hb_lines:
        print(f'First: {hb_lines[0].strip()[:150]}')
        print(f'Last:  {hb_lines[-1].strip()[:150]}')

    # Parse timestamps and find max gap
    ts_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
    timestamps = []
    for l in hb_lines:
        m = ts_pattern.match(l.strip())
        if m:
            timestamps.append(datetime.strptime(m.group(1), '%Y-%m-%d %H:%M:%S'))

    if len(timestamps) >= 2:
        gaps = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
        max_gap = max(gaps)
        max_gap_idx = gaps.index(max_gap)
        print(f'\nMax gap: {max_gap:.0f} seconds ({max_gap/3600:.1f} hours)')
        print(f'  Between: {timestamps[max_gap_idx]} and {timestamps[max_gap_idx+1]}')
        
        print(f'\nAll gaps > 300 seconds:')
        for i, g in enumerate(gaps):
            if g > 300:
                print(f'  Gap at index {i}: {g:.0f}s ({g/3600:.1f}h) between {timestamps[i]} and {timestamps[i+1]}')
        
        print(f'\nGaps > 300s count: {sum(1 for g in gaps if g > 300)}')
        print(f'Total window: {timestamps[0]} to {timestamps[-1]}')
        total_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        print(f'Total hours: {total_hours:.1f}')
        print(f'Total days: {total_hours/24:.1f}')

    # Check for PID changes
    start_idx = None
    for i, l in enumerate(lines):
        if 'PID=52788' in l and 'Bot heartbeat' in l:
            start_idx = i
            break

    if start_idx is not None:
        post_lines = lines[start_idx:]
        other_pids = [l for l in post_lines if 'Bot heartbeat' in l and 'PID=52788' not in l and 'PID=' in l]
        print(f'\nHeartbeat lines with OTHER PIDs after 52788 started: {len(other_pids)}')
        if other_pids:
            for l in other_pids[:5]:
                print(f'  {l.strip()[:150]}')
    
    # Check stderr for errors
    print('\n--- dryrun_stderr.log error summary ---')
    try:
        with open(r'user_data\logs\dryrun_stderr.log', 'r', encoding='utf-8', errors='replace') as f:
            stderr_lines = f.readlines()
        errors = [l for l in stderr_lines if any(kw in l for kw in ['ERROR', 'CRITICAL', 'Traceback', 'Exception'])]
        print(f'Total ERROR/CRITICAL/Traceback/Exception lines: {len(errors)}')
        for l in errors:
            print(f'  {l.strip()[:200]}')
    except FileNotFoundError:
        print('  dryrun_stderr.log not found')

    # PASS/FAIL verdict
    print('\n--- VERDICT ---')
    fail_gaps = [(i, g) for i, g in enumerate(gaps) if g > 300]
    if fail_gaps:
        print(f'FAIL: {len(fail_gaps)} gaps exceed 300 seconds (5 minutes)')
        for i, g in fail_gaps:
            print(f'  Gap {i}: {g:.0f}s between {timestamps[i]} and {timestamps[i+1]}')
    else:
        print('PASS: No gaps exceed 300 seconds')

if __name__ == '__main__':
    main()
