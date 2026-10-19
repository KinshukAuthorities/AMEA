"""Record sampled rig/contact measurements; does not certify animation quality or collisions."""
import argparse,json,sys
from pathlib import Path
import bpy
from mathutils import Vector

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--frames',nargs='*',type=int);p.add_argument('--contacts',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);scene=bpy.context.scene
    contacts=json.loads(a.contacts.read_text(encoding='utf-8')) if a.contacts else []
    frames=sorted(set(a.frames or [scene.frame_start,scene.frame_end])|{int(c['frame']) for c in contacts})
    report={'native':bpy.data.filepath,'frames_sampled':frames,'units':scene.unit_settings.system,
        'unit_scale':scene.unit_settings.scale_length,'rigs':{},'contacts':[],
        'review':'Mechanical samples only; mesh collisions, deformation, likeness and artistic review are not certified.'}
    for ob in scene.objects:
        if ob.type=='ARMATURE':report['rigs'][ob.name]={'bones':len(ob.data.bones),'maximum_pose_length_ratio_deviation':0.0}
    for frame in frames:
        scene.frame_set(frame)
        for name,record in report['rigs'].items():
            for b in bpy.data.objects[name].pose.bones:
                if b.bone.length:
                    deviation=abs((b.tail-b.head).length/b.bone.length-1)
                    record['maximum_pose_length_ratio_deviation']=max(record['maximum_pose_length_ratio_deviation'],deviation)
        for c in [c for c in contacts if c['frame']==frame]:
            ob=bpy.data.objects[c['object']]
            if c.get('bone'):
                bone=ob.pose.bones[c['bone']];which=c.get('point','tail')
                if which not in {'head','tail'}:raise ValueError('Bone point must be head or tail')
                point=ob.matrix_world@getattr(bone,which)
            else:point=ob.matrix_world.translation.copy()
            target=bpy.data.objects[c['target_object']].matrix_world.translation if c.get('target_object') else Vector(c['target'])
            distance=(point-target).length;result={**c,'sampled_point':list(point),'sampled_target':list(target),'distance_units':distance}
            if 'tolerance' in c:result['within_declared_tolerance']=distance<=c['tolerance']
            report['contacts'].append(result)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
