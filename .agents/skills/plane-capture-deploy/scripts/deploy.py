"""Verified public-release deployment. Python standard library only; no hardware I/O."""
from pathlib import Path, PurePosixPath
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys,time,urllib.request,urllib.error,urllib.parse,zipfile,zlib,concurrent.futures,threading
REPO_ROOT=Path(__file__).resolve().parents[4]

PRINT_LOCK=threading.Lock()
def say(**data):
 with PRINT_LOCK:print(json.dumps(data,ensure_ascii=False),flush=True)
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while b:=f.read(8*1024**2):h.update(b)
 return h.hexdigest()
def dump(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf-8')
def longpath(path):
 p=str(Path(path).absolute())
 if os.name!='nt' or p.startswith('\\\\?\\'):return p
 return '\\\\?\\UNC\\'+p[2:] if p.startswith('\\\\') else '\\\\?\\'+p

class SafeRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  parsed=urllib.parse.urlparse(newurl)
  if parsed.scheme!='https':raise RuntimeError('下载重定向不是HTTPS')
  new=super().redirect_request(req,fp,code,msg,headers,newurl)
  if parsed.netloc!=urllib.parse.urlparse(req.full_url).netloc:
   new.remove_header('Authorization');new.remove_header('X-github-api-version')
  return new

class Github:
 def __init__(self):self.opener=urllib.request.build_opener(SafeRedirect())
 def open(self,url,binary=False):
  headers={'User-Agent':'PlaneCapture-Public-Deploy/1','Accept':'application/octet-stream' if binary else 'application/vnd.github+json'}
  try:return self.opener.open(urllib.request.Request(url,headers=headers),timeout=120)
  except urllib.error.HTTPError as e:raise RuntimeError('GitHub HTTP '+str(e.code)+'；请核对公开版本和网络。') from None

def public_asset_url(repo,tag,name):
 if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('无效的GitHub仓库名')
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',tag):raise ValueError('无效的Release标签')
 if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*',name):raise ValueError('无效的附件名')
 return 'https://github.com/'+repo+'/releases/download/'+urllib.parse.quote(tag,safe='')+'/'+urllib.parse.quote(name,safe='')

def validate_manifest(m):
 if m.get('schema_version')!=1:raise RuntimeError('不支持的部署清单版本')
 seen=set()
 for c in m['components']:
  for key in ['archive_relative','extract_into']:
   p=PurePosixPath(c[key])
   if p.is_absolute() or '..' in p.parts or ':' in c[key] or '\\' in c[key]:raise ValueError('部署目录越界')
  if not c['parts']:raise ValueError('组件没有附件分卷')
  for p in c['parts']:
   public_asset_url(m['repository'],m['release_tag'],p['asset'])
   if p['asset'] in seen or not isinstance(p['bytes'],int) or p['bytes']<=0 or not re.fullmatch(r'[0-9a-f]{64}',p['sha256']):raise ValueError('附件清单无效')
   seen.add(p['asset'])

def asset_download(github,repo,tag,part,cache,offline):
 target=cache/part['asset'];source=(offline/part['asset']) if offline else target
 if source.exists():
  if source.stat().st_size==part['bytes'] and digest(source)==part['sha256']:return source
  raise RuntimeError('已有文件校验失败：'+str(source)+'；请另选空缓存目录重新下载。')
 if offline:raise FileNotFoundError('离线附件缺失：'+str(source))
 url=public_asset_url(repo,tag,part['asset'])
 temp=cache/(part['asset']+'.partial')
 for attempt in range(1,4):
  try:
   started=time.monotonic();h=hashlib.sha256();count=0;last=0
   with github.open(url,binary=True) as r,temp.open('wb') as out:
    while block:=r.read(1024**2):
     out.write(block);h.update(block);count+=len(block)
     if count-last>=8*1024**2:say(downloading=part['asset'],MiB=round(count/1024**2),total_MiB=round(part['bytes']/1024**2),MiB_s=round(count/1024**2/max(time.monotonic()-started,.01),2));last=count
   if count!=part['bytes'] or h.hexdigest()!=part['sha256']:raise RuntimeError('下载校验失败：'+part['asset'])
   temp.replace(target);return target
  except Exception:
   if attempt==3:raise
   say(retrying=part['asset'],attempt=attempt+1);time.sleep(min(2*attempt,6))

def assemble(component,parts,target):
 archive=target/component['archive_relative'];archive.parent.mkdir(parents=True,exist_ok=True)
 if archive.exists():
  if archive.stat().st_size==component['archive_bytes'] and digest(archive)==component['archive_sha256']:return archive
  raise RuntimeError('目标目录已有不同归档：'+str(archive))
 partial=archive.with_name(archive.name+'.partial');h=hashlib.sha256();length=0
 with partial.open('wb') as out:
  for part in parts:
   with part.open('rb') as f:
    while b:=f.read(8*1024**2):out.write(b);h.update(b);length+=len(b)
 if length!=component['archive_bytes'] or h.hexdigest()!=component['archive_sha256']:raise RuntimeError('分卷合并校验失败：'+component['id'])
 partial.replace(archive);return archive

def safe_member(base,name):
 if '\\' in name:raise RuntimeError('归档含反斜杠路径')
 rel=PurePosixPath(name)
 if rel.is_absolute() or '..' in rel.parts or any(':' in p for p in rel.parts):raise RuntimeError('归档路径越界')
 return base.joinpath(*rel.parts)

def extract(component,archive,target):
 base=target/component['extract_into'];done=0
 with zipfile.ZipFile(archive) as z:
  for info in z.infolist():
   out=safe_member(base,info.filename)
   if ((info.external_attr>>16)&0o170000)==0o120000:raise RuntimeError('归档含符号链接')
   if info.is_dir():os.makedirs(longpath(out),exist_ok=True);continue
   os.makedirs(longpath(out.parent),exist_ok=True)
   with z.open(info) as source,open(longpath(out),'wb') as dest:shutil.copyfileobj(source,dest,1024**2)
   if os.stat(longpath(out)).st_size!=info.file_size:raise RuntimeError('解压大小错误：'+info.filename)
   done+=1
   if done%10000==0:say(extracting=component['id'],files=done,total=component['entries'])
 return done

def configure_local_paths(target,m):
 rel='01_控制地面站/地面站_v31.2_OSD完整程序/station/settings.json';file=target/rel;record_path=target/'_deployment/local_overrides.json'
 records=json.loads(record_path.read_text('utf-8')) if record_path.exists() else {}
 if rel in records:return
 c=next(x for x in m['components'] if x['id']=='control')
 with zipfile.ZipFile(target/c['archive_relative']) as z:original=z.read(c['top_directory']+'/station/settings.json')
 current=file.read_bytes()
 if current!=original:raise RuntimeError('部署前发现已修改的station/settings.json；请先确认现有配置，未覆盖。')
 settings=json.loads(current.decode('utf-8-sig'));old=settings.get('data_directory');settings['data_directory']=str(target/'运行记录/地面站_v31_2')
 new=(json.dumps(settings,ensure_ascii=False,indent=2)+'\n').encode('utf-8');file.write_bytes(new)
 records[rel]=dict(reason='Recipient-selected local data directory; explicitly mutable in DELIVERY_MANIFEST.json',field='data_directory',original_value=old,new_value=settings['data_directory'],original_sha256=hashlib.sha256(original).hexdigest(),local_sha256=hashlib.sha256(new).hexdigest(),local_bytes=len(new),local_crc32=zlib.crc32(new))
 dump(record_path,records);say(configured_local_data_directory=settings['data_directory'])

def verify(target,m,deep=True):
 failed=[];count=0;override_path=target/'_deployment/local_overrides.json';overrides=json.loads(override_path.read_text('utf-8')) if override_path.exists() else {}
 for c in m['components']:
  arc=target/c['archive_relative']
  if not arc.exists() or digest(arc)!=c['archive_sha256']:failed.append(c['id']+': archive hash');continue
  with zipfile.ZipFile(arc) as z:
   for info in z.infolist():
    if info.is_dir():continue
    f=safe_member(target/c['extract_into'],info.filename);count+=1
    try:
     change=overrides.get(f.relative_to(target).as_posix());expected_size=change['local_bytes'] if change else info.file_size;expected_crc=change['local_crc32'] if change else info.CRC
     if change and digest(longpath(f))!=change['local_sha256']:failed.append(info.filename+': local override hash');continue
     if os.stat(longpath(f)).st_size!=expected_size:failed.append(info.filename+': size');continue
     if deep:
      crc=0
      with open(longpath(f),'rb') as src:
       while b:=src.read(4*1024**2):crc=zlib.crc32(b,crc)
      if crc!=expected_crc:failed.append(info.filename+': CRC')
    except FileNotFoundError:failed.append(info.filename+': missing')
 report=dict(checked_files=count,failed=failed,deep_crc=deep,local_config_overrides=len(overrides),hardware_connections=0);dump(target/'_deployment/verification.json',report);say(verification=report)
 if failed:raise RuntimeError('部署文件校验失败')
 return report

def install(target,cache,offline,m):
 if os.name!='nt':raise RuntimeError('交付环境为Windows x64；其他平台请先选择Windows部署。')
 state_path=target/'_deployment/state.json';manifest_sha=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest()
 if target.exists() and any(target.iterdir()) and not state_path.exists():raise RuntimeError('目标目录非空且不是本部署的工作目录；请选择新目录。')
 state=json.loads(state_path.read_text('utf-8')) if state_path.exists() else dict(repository=m['repository'],manifest_sha256=manifest_sha,completed=[])
 if state['repository']!=m['repository'] or state['manifest_sha256']!=manifest_sha:raise RuntimeError('目标目录属于其他版本；请选择新目录。')
 ancestor=target
 while not ancestor.exists():ancestor=ancestor.parent
 free=shutil.disk_usage(ancestor).free
 if not state['completed'] and free<m['estimated_free_bytes_for_install']:raise RuntimeError(f'目标磁盘空间不足；本版本建议至少{m["estimated_free_bytes_for_install"]/1024**3:.1f} GiB可用空间。')
 target.mkdir(parents=True,exist_ok=True);cache.mkdir(parents=True,exist_ok=True);dump(state_path,state)
 gh=Github() if not offline else None
 for c in m['components']:
  if c['id'] in state['completed']:continue
  with concurrent.futures.ThreadPoolExecutor(max_workers=min(8,len(c['parts']))) as pool:
   parts=list(pool.map(lambda part:asset_download(gh,m['repository'],m['release_tag'],part,cache,offline),c['parts']))
  archive=assemble(c,parts,target);n=extract(c,archive,target);state['completed'].append(c['id']);dump(state_path,state);say(installed=c['id'],files=n)
 configure_local_paths(target,m)
 verify(target,m,deep=False)
 station=target/'01_控制地面站/地面站_v31.2_OSD完整程序';python=station/'python/python.exe'
 cmd=[str(python),'-B','-X','utf8',str(station/'tools/station_cli.py'),'replay','--no-browser'];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=45)
 if p.returncode:raise RuntimeError('离线回放入口检查失败：'+p.stderr[:600])
 dump(target/'_deployment/completion.json',dict(completed=datetime.datetime.now().isoformat(timespec='seconds'),release=m['release_tag'],components=state['completed'],offline_replay_check='pass',hardware_connections=0,entry=str(target/'00_交付导航.html'),video_entry=str(target/'03_原理算法与过程资料/00_全部仿真视频.html')))
 say(complete=True,target=str(target),entry=str(target/'00_交付导航.html'),hardware_connections=0)

def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['plan','install','verify'],nargs='?',default='install');a.add_argument('--target',type=Path,required=True);a.add_argument('--cache',type=Path);a.add_argument('--offline-assets',type=Path);a.add_argument('--manifest',type=Path,default=REPO_ROOT/'delivery/manifest.json');args=a.parse_args()
 m=json.loads(args.manifest.read_text('utf-8'));validate_manifest(m);target=args.target.expanduser().resolve()
 if target==Path(target.anchor):raise RuntimeError('目标不能是磁盘根目录')
 if args.action=='plan':say(repository=m['repository'],release=m['release_tag'],target=str(target),download_GiB=round(m['download_bytes']/1024**3,2),recommended_free_GiB=round(m['estimated_free_bytes_for_install']/1024**3,2),components=[x['id'] for x in m['components']],hardware_autostart=False);return
 if args.action=='verify':verify(target,m);return
 install(target,(args.cache or target/'_download_cache').resolve(),args.offline_assets.resolve() if args.offline_assets else None,m)
if __name__=='__main__':
 try:main()
 except Exception as exc:say(error=type(exc).__name__,message=str(exc));sys.exit(1)
