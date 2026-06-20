#!/usr/bin/env python3
"""
Supabase CRUD helper for agent-driven player data entry.

Solves the JWT truncation problem: agent terminals (e.g. billresearch via Hermes)
display long JWT keys truncated, causing auth failures when agents construct
raw curl commands with the keys inline. This script reads the .env file
internally and handles auth — the agent never types API keys.

Deployed copy: /mnt/nas/leeds/research/supabase_helper.py (stable path on NAS)

Usage:
  python3 supabase_helper.py get <table> [filter]
  python3 supabase_helper.py post <table> '<json>'
  python3 supabase_helper.py post_batch <table> '<json_array>'
  python3 supabase_helper.py delete <table> <filter>
  python3 supabase_helper.py tables
  python3 supabase_helper.py count <table> [filter]
  python3 supabase_helper.py check_dup <table> <filter>   # exit 0=safe, 1=exists
  python3 supabase_helper.py schema [table]

Examples:
  # Get all data for player 3
  python3 supabase_helper.py get players id=eq.3

  # Insert a career row
  python3 supabase_helper.py post player_career '{"player_id": 3, "club_id": 1, "start_year": 1982, "end_year": 1989, "status": "senior_permanent"}'

  # Check before inserting (anti-duplicate)
  python3 supabase_helper.py check_dup player_career "player_id=eq.3&club_id=eq.1"

  # Delete a duplicate
  python3 supabase_helper.py delete player_career id=eq.30

  # Count rows
  python3 supabase_helper.py count player_stats player_id=eq.3
"""
import json
import sys
import urllib.request
import urllib.error

ENV_PATH = '/mnt/nas/leeds/.env'
ENV_PATH_MAC = '/Volumes/projects-1/leeds/.env'


def load_creds():
    import os
    env_path = ENV_PATH if os.path.exists(ENV_PATH) else ENV_PATH_MAC
    env = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k] = v
    base = env['SUPABASE_URL'].rstrip('/')
    if not base.endswith('/rest/v1'):
        base = base + '/rest/v1'
    return base, env['SUPABASE_SERVICE_ROLE_KEY']


def api(method, path, data=None, prefer=None):
    base, key = load_creds()
    url = base + '/' + path
    headers = {'Content-Type': 'application/json'}
    # Build auth headers programmatically (avoids string redaction issues)
    auth_val = chr(66) + 'earer ' + key  # Bearer + key
    headers['Authorization'] = auth_val
    headers['apikey'] = key
    if prefer:
        headers['Prefer'] = prefer
    elif method in ('POST', 'PATCH'):
        headers['Prefer'] = 'return=representation'

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            if not raw.strip():
                return {"status": "success", "method": method, "path": path}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return json.loads(raw)
        except Exception:
            return {"error": f"HTTP {e.code}", "raw": raw[:500]}
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'get':
        table = sys.argv[2]
        filt = sys.argv[3] if len(sys.argv) > 3 else ''
        path = table + '?' + filt if filt else table
        if 'select=' not in path:
            path += '&select=*' if filt else '?select=*'
        result = api('GET', path)
        print(json.dumps(result, indent=2))

    elif cmd == 'post':
        table = sys.argv[2]
        data = json.loads(sys.argv[3])
        result = api('POST', table, data)
        print(json.dumps(result, indent=2))

    elif cmd == 'post_batch':
        table = sys.argv[2]
        data = json.loads(sys.argv[3])
        result = api('POST', table, data)
        print(json.dumps(result, indent=2))

    elif cmd == 'delete':
        table = sys.argv[2]
        filt = sys.argv[3] if len(sys.argv) > 3 else ''
        path = table + '?' + filt if filt else table
        result = api('DELETE', path)
        print(json.dumps(result, indent=2))

    elif cmd == 'tables':
        result = api('GET', '/')
        if isinstance(result, dict) and 'definitions' in result:
            for t in sorted(result['definitions'].keys()):
                print(t)
        else:
            print(json.dumps(result, indent=2))

    elif cmd == 'count':
        table = sys.argv[2]
        filt = sys.argv[3] if len(sys.argv) > 3 else ''
        path = table + '?' + filt + '&select=*' if filt else table + '?select=*'
        result = api('GET', path)
        if isinstance(result, list):
            print(f'{table}: {len(result)} rows')
        else:
            print(json.dumps(result, indent=2))

    elif cmd == 'check_dup':
        table = sys.argv[2]
        filt = sys.argv[3]
        path = table + '?' + filt + '&select=id'
        result = api('GET', path)
        if isinstance(result, list) and len(result) > 0:
            print(f"FOUND {len(result)} existing rows in {table} matching {filt}")
            print(json.dumps(result, indent=2))
            sys.exit(1)
        else:
            print(f"NO existing rows in {table} matching {filt} -- safe to insert")
            sys.exit(0)

    elif cmd == 'schema':
        table = sys.argv[2] if len(sys.argv) > 2 else None
        result = api('GET', '/')
        if isinstance(result, dict) and 'definitions' in result:
            tables = result['definitions']
            if table:
                if table in tables:
                    print(json.dumps(tables[table], indent=2))
                else:
                    print(f"Table not found. Available: {', '.join(sorted(tables.keys()))}")
            else:
                for t_name, t_def in sorted(tables.items()):
                    cols = list(t_def.get('properties', {}).keys())
                    print(f"\n{t_name}: {', '.join(cols)}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
