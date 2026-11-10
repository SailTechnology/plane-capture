from pathlib import Path
import unittest,tempfile,os,json,hashlib,io,zipfile,urllib.request,importlib.util
ROOT=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('deployment',ROOT/'.agents/skills/plane-capture-deploy/scripts/deploy.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)

class DeploymentBehavior(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  base=Path(os.environ.get('PLANE_CAPTURE_TEST_ROOT','H:/Temp/Codex/飞机捕获_GitHub交付/behavior_tests'))
  base.mkdir(parents=True,exist_ok=True);cls.work=Path(tempfile.mkdtemp(prefix='case_',dir=base))
 def test_zip_traversal_does_not_write_outside_target(self):
  archive=self.work/'traversal.zip';dest=self.work/'unpack';dest.mkdir()
  with zipfile.ZipFile(archive,'w') as z:z.writestr('../outside.txt','must-not-write')
  with self.assertRaises(RuntimeError):d.extract({'extract_into':'','id':'test','entries':1},archive,dest)
  self.assertFalse((self.work/'outside.txt').exists())
 def test_symbolic_link_entry_is_rejected(self):
  archive=self.work/'symlink.zip';info=zipfile.ZipInfo('link');info.external_attr=(0o120777<<16)
  with zipfile.ZipFile(archive,'w') as z:z.writestr(info,'target')
  with self.assertRaises(RuntimeError):d.extract({'extract_into':'','id':'test','entries':1},archive,self.work/'links')
 def test_existing_project_is_preserved(self):
  target=self.work/'existing';target.mkdir();file=target/'important.txt';file.write_text('preserve','utf-8')
  with self.assertRaises(RuntimeError):d.install(target,self.work/'cache',None,{'repository':'test/repo'})
  self.assertEqual(file.read_text('utf-8'),'preserve')
 def test_bad_offline_asset_stops_before_extraction(self):
  assets=self.work/'bad_assets';assets.mkdir();f=assets/'part001';f.write_bytes(b'wrong')
  part={'asset':f.name,'bytes':5,'sha256':hashlib.sha256(b'right').hexdigest()}
  with self.assertRaises(RuntimeError):d.asset_download(None,'test/repo','v1',part,self.work/'cache',assets)
  self.assertEqual(f.read_bytes(),b'wrong')
 def test_public_download_uses_release_url_without_login(self):
  data=b'public release part';cache=self.work/'public_cache';cache.mkdir()
  part={'asset':'part001.zip','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  class Client:
   def __init__(self):self.urls=[]
   def open(self,url,binary=False):self.urls.append((url,binary));return io.BytesIO(data)
  client=Client();result=d.asset_download(client,'test/repo','v1',part,cache,None)
  self.assertEqual(result.read_bytes(),data)
  self.assertEqual(client.urls,[('https://github.com/test/repo/releases/download/v1/part001.zip',True)])
 def test_public_client_never_sends_authorization(self):
  class Opener:
   def open(self,request,timeout):self.request=request;return io.BytesIO(b'ok')
  client=d.Github();client.opener=Opener();client.open('https://github.com/test/repo/releases/download/v1/part001.zip',binary=True)
  self.assertIsNone(client.opener.request.get_header('Authorization'))
 def test_manifest_rejects_invalid_public_asset_paths(self):
  with self.assertRaises(ValueError):d.public_asset_url('test/repo','v1','../other.zip')
  with self.assertRaises(ValueError):d.public_asset_url('test/repo/extra','v1','part001.zip')
 def test_ordered_join_requires_full_hash(self):
  a=self.work/'a';b=self.work/'b';a.write_bytes(b'abc');b.write_bytes(b'def');target=self.work/'join';target.mkdir()
  c={'id':'test','archive_relative':'joined.zip','archive_bytes':6,'archive_sha256':hashlib.sha256(b'abcdef').hexdigest()}
  with self.assertRaises(RuntimeError):d.assemble(c,[b,a],target)
  self.assertFalse((target/'joined.zip').exists())
  result=d.assemble(c,[a,b],target);self.assertEqual(result.read_bytes(),b'abcdef')
 def test_cross_host_redirect_drops_credentials(self):
  req=urllib.request.Request('https://api.github.com/repos/test',headers={'Authorization':'Bearer TEST_ONLY','Accept':'application/octet-stream'})
  out=d.SafeRedirect().redirect_request(req,None,302,'Found',{},'https://release-assets.githubusercontent.com/object')
  self.assertIsNone(out.get_header('Authorization'));self.assertEqual(out.get_header('Accept'),'application/octet-stream')
 def test_only_local_log_directory_is_configured(self):
  target=self.work/'configure';folder=target/'01_控制地面站/地面站_v31.2_OSD完整程序/station';folder.mkdir(parents=True);original={'data_directory':'H:/author/log','iris_port':'COM17','camera_device':'USB CAMERA','tracking_speed_deg_s':170};raw=json.dumps(original).encode();(folder/'settings.json').write_bytes(raw)
  with zipfile.ZipFile(target/'control.zip','w') as z:z.writestr('地面站_v31.2_OSD完整程序/station/settings.json',raw)
  m={'components':[{'id':'control','archive_relative':'control.zip','top_directory':'地面站_v31.2_OSD完整程序'}]};d.configure_local_paths(target,m);after=json.loads((folder/'settings.json').read_text('utf-8'))
  self.assertEqual(after['data_directory'],str(target/'运行记录/地面站_v31_2'))
  self.assertEqual({k:v for k,v in after.items() if k!='data_directory'},{k:v for k,v in original.items() if k!='data_directory'})
  self.assertTrue((target/'_deployment/local_overrides.json').exists())

if __name__=='__main__':unittest.main(verbosity=2)
