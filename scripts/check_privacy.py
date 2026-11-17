#!/usr/bin/env python3
"""Check publication files; never print matched values."""
import re
import subprocess
from pathlib import Path
PATTERNS = {
    'personal email': r'(?i)[\w.+-]+@(?:gmail|qq|163|outlook|hotmail)\.com',
    'access token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[A-Z0-9]{16})',
    'private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'home directory': r'/' + r'Users/[^/\s]+/',
    'device MAC': r'(?i)(?:[0-9a-f]{2}:){5}[0-9a-f]{2}',
    'private IPv4': r'\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b',
}
def check_text(text):
    return [name for name, pat in PATTERNS.items() if re.search(pat,text)]
def main():
    root=Path(__file__).resolve().parents[1]
    files=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root).decode().split('\0')
    findings=[]
    for file in set(files)-{''}:
        path=root/file
        if path.is_file():
            for name in check_text(path.read_text()):findings.append(file+': '+name)
    if findings:raise SystemExit('\n'.join(findings))
    print('Publication privacy checks passed')
if __name__=='__main__':main()
