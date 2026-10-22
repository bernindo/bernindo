#!/usr/bin/env python3
"""Refresh public data only. Never writes to GitHub or reads credentials."""
import json
import re
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER = 'bernindo'


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'bernindo-local-profile-preview', 'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'text/html'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode('utf-8')


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.tips = {}, {}
        self.tip = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and a.get('data-date'):
            self.cells[a['id']] = {'date': a['data-date'], 'level': int(a.get('data-level', 0))}
        if tag == 'tool-tip' and a.get('for'):
            self.tip = a['for']
            self.tips[self.tip] = ''

    def handle_data(self, data):
        if self.tip:
            self.tips[self.tip] += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip = None

    def days(self):
        result = []
        for ident, cell in self.cells.items():
            tip = self.tips.get(ident, '').strip()
            match = re.match(r'([\d,]+) contributions?\b', tip)
            if match:
                count = int(match[1].replace(',', ''))
            elif tip.startswith('No contributions'):
                count = 0
            else:
                raise ValueError('Unrecognized contribution tooltip; preserving previous snapshot.')
            result.append({**cell, 'count': count})
        result.sort(key=lambda d: d['date'])
        if len(result) < 300:
            raise ValueError('Incomplete calendar; preserving previous snapshot.')
        return result


def main():
    now = datetime.now(timezone.utc)
    user = json.loads(fetch(f'https://api.github.com/users/{USER}'))
    repos = []
    page = 1
    while True:
        batch = json.loads(fetch(f'https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}'))
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    events = json.loads(fetch(f'https://api.github.com/users/{USER}/events/public?per_page=20'))
    calendar_html = fetch(f'https://github.com/users/{USER}/contributions')
    parser = CalendarParser()
    parser.feed(calendar_html)
    days = parser.days()
    h = re.search(r'id="js-contribution-activity-description"[^>]*>(.*?)</h2>', calendar_html, re.S)
    total_match = re.search(r'([\d,]+)\s+contributions?', h[1]) if h else None
    if not total_match:
        raise ValueError('Missing calendar total; preserving previous snapshot.')
    total = int(total_match[1].replace(',', ''))
    # GitHub renders whole calendar weeks; keep the published annual total separately.
    longest = run = 0
    for day in days:
        run = run + 1 if day['count'] else 0
        longest = max(longest, run)
    checks = []
    for name, url in [('EdBrix Studios', 'https://edbrixstudios.vercel.app')]:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'bernindo-local-profile-preview'})
            with urllib.request.urlopen(request, timeout=20) as response:
                checks.append({'name': name, 'url': url, 'status': response.status, 'reachable': response.status == 200, 'checked_at': now.isoformat()})
        except Exception:
            checks.append({'name': name, 'url': url, 'status': None, 'reachable': False, 'checked_at': now.isoformat()})
    snapshot = {
        'updated_at': now.isoformat(),
        'user': {key: user.get(key) for key in ['login', 'name', 'public_repos', 'followers', 'following', 'html_url']},
        'contributions': {'total': total, 'days': days, 'longest_streak': longest, 'best_day': max(d['count'] for d in days), 'source': f'https://github.com/users/{USER}/contributions'},
        'repos': [{k: r.get(k) for k in ['name', 'description', 'html_url', 'homepage', 'language', 'stargazers_count', 'updated_at']} for r in repos],
        'events': [{k: e.get(k) for k in ['type', 'created_at', 'repo']} for e in events],
        'checks': checks,
        'sources': [f'https://api.github.com/users/{USER}', f'https://api.github.com/users/{USER}/repos', f'https://api.github.com/users/{USER}/events/public', f'https://github.com/users/{USER}/contributions']
    }
    target = ROOT / 'data'
    target.mkdir(exist_ok=True)
    # Commit a complete snapshot only after every required source has parsed correctly.
    payload = json.dumps(snapshot, ensure_ascii=False, indent=2)
    (target / 'profile.json.tmp').write_text(payload)
    (target / 'profile.json.tmp').replace(target / 'profile.json')
    (target / 'profile-data.js').write_text('window.PROFILE_DATA = ' + json.dumps(snapshot, ensure_ascii=False).replace('</', '<\\/') + ';\n')
    print(f'Updated: {len(days)} calendar days, {total} annual contributions, {len(repos)} public repositories, {len(events)} recent public events.')


if __name__ == '__main__':
    main()
