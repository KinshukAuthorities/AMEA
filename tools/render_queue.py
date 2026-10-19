"""Versioned, resumable Blender rendering of an already-authored scene; no generation downloads."""
import argparse,hashlib,json,math,os,subprocess,sys,time
from fractions import Fraction
from pathlib import Path
from common import discover,project_output,sha256,write_json

def validate_job(path):
    path=Path(path).resolve();job=json.loads(path.read_text(encoding='utf-8-sig'));base=path.parent
    for key in ['start','end','width','height']:
        if type(job.get(key)) is not int:raise ValueError(f'{key} must be an integer')
    if job['start']<0 or job['end']<job['start']:raise ValueError('Invalid inclusive frame range')
    if any(job[k]<2 or job[k]%2 for k in ['width','height']):raise ValueError('Output dimensions must be positive and even')
    rate=Fraction(str(job['fps']))
    if not 0<rate<=1000:raise ValueError('Invalid frame rate')
    if 'samples' in job and (type(job['samples']) is not int or job['samples']<1):raise ValueError('Invalid sample count')
    if type(job.get('encode',True)) is not bool:raise ValueError('encode must be boolean')
    scene=(base/job['scene']).resolve()
    if not scene.is_file():raise FileNotFoundError(scene)
    dependencies=[scene]+[(base/p).resolve() for p in job.get('dependencies',[])]
    if job.get('audio_mix'):dependencies.append((base/job['audio_mix']).resolve())
    for file in dependencies:
        if not file.is_file():raise FileNotFoundError(file)
    return path,job,scene,dependencies,project_output(base,job.get('output_dir','renders'))

def call(args):
    r=subprocess.run(args,capture_output=True,text=True)
    if r.returncode:raise RuntimeError(r.stderr[-5000:] or r.stdout[-5000:])
    return r.stdout

def frame_valid(path,size):
    from PIL import Image
    try:
        with Image.open(path) as im:
            if im.size!=tuple(size):return False
            im.verify()
        return True
    except (OSError,ValueError):return False

def encode(run_dir,job,base,ffmpeg,ffprobe):
    count=job['end']-job['start']+1;rate=Fraction(str(job['fps']));duration=float(count/rate)
    video=run_dir/'animation.mp4';temp=run_dir/'animation.encoding.mp4'
    command=[ffmpeg,'-v','error','-nostdin','-y','-framerate',str(rate),'-start_number',str(job['start']),
             '-i',str(run_dir/'frames/frame_%06d.png')]
    if job.get('audio_mix'):
        audio=(base/job['audio_mix']).resolve()
        info=json.loads(call([ffprobe,'-v','error','-show_streams','-show_format','-of','json',str(audio)]))
        stream=next((s for s in info['streams'] if s['codec_type']=='audio'),None)
        if stream is None:raise ValueError('audio_mix contains no audio')
        length=float(stream.get('duration',info['format'].get('duration',0)))
        if abs(length-duration)>max(.03,1/float(rate)):raise ValueError('Prepare an audio mix aligned to the full output duration before encoding')
        command+=['-i',str(audio)]
    command+=['-frames:v',str(count),'-t',str(duration),'-c:v','libx264','-crf','18','-preset','fast','-pix_fmt','yuv420p','-threads','4']
    if job.get('audio_mix'):command+=['-c:a','aac','-b:a','192k','-af','apad']
    command+=['-movflags','+faststart',str(temp)];call(command)
    info=json.loads(call([ffprobe,'-v','error','-count_frames','-show_streams','-show_format','-of','json',str(temp)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    if int(v['nb_read_frames'])!=count or Fraction(v['avg_frame_rate'])!=rate:raise RuntimeError('Encoded frame count/rate mismatch')
    if [v['width'],v['height']]!=[job['width'],job['height']]:raise RuntimeError('Encoded dimensions mismatch')
    if abs(float(v['duration'])-duration)>.002:raise RuntimeError('Encoded duration mismatch')
    audio=next((s for s in info['streams'] if s['codec_type']=='audio'),None)
    if bool(audio)!=bool(job.get('audio_mix')):raise RuntimeError('Encoded audio presence mismatch')
    os.replace(temp,video)
    report={'video':video.name,'sha256':sha256(video),'decoded_frames':count,'fps':str(rate),
            'seconds':float(v['duration']),'resolution':[v['width'],v['height']],
            'audio_seconds':float(audio['duration']) if audio else None,'visual_review':'pending','listening_review':'pending' if audio else 'not applicable'}
    write_json(run_dir/'delivery-checks.json',report)
    selections=sorted(set(job.get('review_frames',[])))
    if any(type(f) is not int or not job['start']<=f<=job['end'] for f in selections):raise ValueError('Invalid review frame selection')
    if selections:
        expr='+'.join(f'eq(n\\,{f-job["start"]})' for f in selections)
        call([ffmpeg,'-v','error','-nostdin','-y','-i',str(video),'-vf','select='+expr,'-fps_mode','vfr',str(run_dir/'encoded-review-%03d.png')])
    return report

def render(path,blender=None,workers=1,threads=4,ffmpeg=None,ffprobe=None):
    path,job,scene,dependencies,out=validate_job(path);base=path.parent
    if not 1<=workers<=min(8,os.cpu_count() or 1) or threads<1:raise ValueError('Choose a bounded positive worker/thread count')
    executable=discover('blender',blender)
    if not executable:raise FileNotFoundError('Supply the selected Blender executable')
    version=call([executable,'--version']).splitlines()[0]
    helper=Path(__file__).with_name('blender_render_worker.py')
    identity={'job':job,'inputs':[{'file':str(f),'sha256':sha256(f)} for f in dependencies],
              'worker_sha256':sha256(helper),'queue_sha256':sha256(__file__),'blender':version}
    digest=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    run_dir=out/digest[:20];run_dir.mkdir(parents=True,exist_ok=True)
    write_json(run_dir/'run.json',{'identity':identity,'signature':digest,'job':job,'threads':threads})
    total=job['end']-job['start']+1;workers=min(workers,total);chunk=math.ceil(total/workers)
    processes=[];started=time.monotonic()
    try:
        for i,first in enumerate(range(job['start'],job['end']+1,chunk)):
            last=min(job['end'],first+chunk-1);log=(run_dir/f'worker-{i+1}.log').open('w',encoding='utf-8')
            cmd=[executable,'-b',str(scene),'-t',str(threads),'--python',str(helper),'--','--run',str(run_dir/'run.json'),'--first',str(first),'--last',str(last)]
            try:process=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
            except Exception:log.close();raise
            processes.append((process,log))
        while any(p.poll() is None for p,_ in processes):
            done=len(list((run_dir/'frames').glob('frame_*.png'))) if (run_dir/'frames').exists() else 0
            print(json.dumps({'completed':done,'total':total,'elapsed_seconds':round(time.monotonic()-started),'generation':str(run_dir)}),flush=True)
            time.sleep(2)
        failed=[p.returncode for p,_ in processes if p.returncode]
        if failed:raise RuntimeError(f'Render worker failed: {failed}; inspect worker logs and resume this generation')
    finally:
        for p,log in processes:
            if p.poll() is None:p.terminate();p.wait(timeout=20)
            log.close()
    missing=[f for f in range(job['start'],job['end']+1) if not frame_valid(run_dir/f'frames/frame_{f:06d}.png',[job['width'],job['height']])]
    if missing:raise RuntimeError(f'Invalid/missing frames: {missing[:20]}')
    result={'generation':str(run_dir),'frames':total,'render_seconds':round(time.monotonic()-started,3),'artistic_review':'pending'}
    if job.get('encode',True):
        encoder=discover('ffmpeg',ffmpeg);probe=discover('ffprobe',ffprobe)
        if not encoder or not probe:raise FileNotFoundError('FFmpeg and FFprobe are required for encoding; rendered frames are preserved')
        result['delivery']=encode(run_dir,job,base,encoder,probe)
    write_json(run_dir/'status.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('job',type=Path);p.add_argument('--blender');p.add_argument('--workers',type=int,default=1);p.add_argument('--threads',type=int,default=4);p.add_argument('--ffmpeg');p.add_argument('--ffprobe');a=p.parse_args()
    print(json.dumps(render(a.job,a.blender,a.workers,a.threads,a.ffmpeg,a.ffprobe),indent=2))
