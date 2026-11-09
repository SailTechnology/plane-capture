from pathlib import Path
import argparse,datetime,json,os,shutil,subprocess,sys

def main():
 p=argparse.ArgumentParser();p.add_argument('--target',type=Path,required=True);p.add_argument('--mode',choices=['all','render'],default='render');p.add_argument('--work-root',type=Path);a=p.parse_args();target=a.target.resolve()
 source=target/'03_原理算法与过程资料/仿真Demo与SimToReal对照_20261109';python=target/'01_控制地面站/地面站_v31.2_OSD完整程序/python/python.exe';cad=target/'02_机械设计/机械设计包_20261109/04_代码与重建/runtime/CADPython'
 if not source.exists() or not python.exists() or not (cad/'vtkmodules').exists():raise RuntimeError('部署资料或运行环境缺失，请先执行完整部署校验。')
 base=(a.work_root or target.parent/'飞机捕获_仿真复现').resolve();work=base/(datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+a.mode)
 if source==base or source in base.parents:raise RuntimeError('工作目录必须位于原交付目录外。')
 work.mkdir(parents=True,exist_ok=False)
 for f in source.iterdir():
  if f.name in ['videos','qa','__pycache__','交付文件SHA256.json'] or (a.mode=='all' and f.name in ['results','pilot']):continue
  if f.is_dir():shutil.copytree(f,work/f.name)
  else:shutil.copy2(f,work/f.name)
 env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PLANE_DEMO_CAD_DEPS=str(cad))
 tasks=[]
 if a.mode=='all':tasks+=[['run_suite.py','--case','straight_120','--environment','nominal','--output',str(work/'pilot')],['run_suite.py','--all','--workers','3'],['analyze_results.py']]
 tasks+=[['render_demos.py','--all'],['render_comparisons.py']]
 for i,step in enumerate(tasks):
  log=work/f'{i+1:02d}_{Path(step[0]).stem}.log';print(json.dumps({'step':step[0],'work':str(work),'log':str(log)},ensure_ascii=False),flush=True)
  with log.open('w',encoding='utf-8') as out:
   result=subprocess.run([str(python),'-B','-X','utf8',str(work/step[0]),*step[1:]],cwd=work,env=env,stdout=out,stderr=subprocess.STDOUT)
  if result.returncode:raise RuntimeError('复现步骤失败，请查看 '+str(log))
 print(json.dumps({'complete':True,'work':str(work),'hardware_connections':0},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
