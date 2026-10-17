"""Apply page-level protections supported by GitHub Pages.

GitHub Pages serves static files; response headers are controlled by GitHub.
The active policy here is delivered by HTML metadata, not a custom server.
"""
from pathlib import Path
from html import escape,unescape
import re,hashlib,base64

root=Path(__file__).resolve().parent.parent
out=root/'_site'
files=sorted(out.glob('*.html'))
if not files:raise SystemExit('Render the Quarto site first.')
def digest(s):return "'sha256-"+base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode()+"'"
script_hashes=set()
handler_hashes=set()
for f in files:
 text=f.read_text()
 for attrs,code in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',text,re.S|re.I):
  if re.search(r'\bsrc\s*=',attrs,re.I):continue
  typ=re.search(r'\btype=[\"\']([^\"\']+)',attrs,re.I)
  if typ and typ.group(1) not in ('module','application/javascript','text/javascript'):continue
  if code.strip():script_hashes.add(digest(code))
 for _,value in re.findall(r'\s(on[a-z]+)="([^"]*)"',text,re.I):handler_hashes.add(digest(unescape(value)))
policy="; ".join([
 "default-src 'none'",
 "script-src 'self' "+' '.join(sorted(script_hashes)),
 "script-src-attr 'unsafe-hashes' "+' '.join(sorted(handler_hashes)),
 "style-src 'self' 'unsafe-inline'",
 "img-src 'self' data:",
 "font-src 'self' data:",
 "connect-src 'self'",
 "base-uri 'none'",
 "form-action 'none'",
 "object-src 'none'",
 "frame-ancestors 'none'",
 "upgrade-insecure-requests"
])
# frame-ancestors only works as an HTTP header, so omit it from the fallback meta.
meta_policy=policy.replace("; frame-ancestors 'none'",'')
for f in files:
 text=f.read_text()
 text=re.sub(r'\n?<!-- portfolio-security:start -->.*?<!-- portfolio-security:end -->\n?', '\n',text,flags=re.S)
 meta='\n<!-- portfolio-security:start -->\n<meta http-equiv="Content-Security-Policy" content="'+escape(meta_policy,quote=True)+'">\n<meta name="referrer" content="no-referrer">\n<!-- portfolio-security:end -->\n'
 text=re.sub(r'<head>',lambda m:m.group(0)+meta,text,count=1,flags=re.I)
 def safe_link(m):
  tag=m.group(0)
  if not re.search(r'\btarget=[\"\']_blank[\"\']',tag,re.I):return tag
  rel=re.search(r'\brel=([\"\'])(.*?)\1',tag,re.I)
  if rel:
   values=set(rel.group(2).split())|{'noopener','noreferrer'}
   return tag[:rel.start()]+'rel="'+' '.join(sorted(values))+'"'+tag[rel.end():]
  return tag[:-1]+' rel="noopener noreferrer">'
 text=re.sub(r'<a\b[^>]*>',safe_link,text,flags=re.I)
 f.write_text(text)
headers={
 'Content-Security-Policy':policy,
 'X-Content-Type-Options':'nosniff',
 'X-Frame-Options':'DENY',
 'Referrer-Policy':'no-referrer',
 'Permissions-Policy':'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
 'Strict-Transport-Security':'max-age=31536000'
}
(out/'.nojekyll').touch()
# Keep generated source and configuration outside the hosted static directory.
for f in out.rglob('*'):
 if f.is_file() and (f.name in ('.env','.gitconfig','hosting.json') or f.suffix in ('.qmd','.R','.rds','.RData','.py')):
  raise SystemExit('Unexpected non-public build file: '+str(f.relative_to(out)))
for f in files:
 text=f.read_text()
 assert '<meta http-equiv="Content-Security-Policy"' in text
 for attrs,code in re.findall(r'<script\b([^>]*)>(.*?)</script\s*>',text,re.S|re.I):
  if re.search(r'\bsrc\s*=',attrs,re.I):continue
  typ=re.search(r'\btype=[\"\']([^\"\']+)',attrs,re.I)
  if typ and typ.group(1) not in ('module','application/javascript','text/javascript'):continue
  if code.strip():assert digest(code) in script_hashes
print('Hardened',len(files),'pages;',len(script_hashes),'script hashes;',len(handler_hashes),'approved handler hashes.')
