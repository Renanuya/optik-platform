"""Run reproducible MuJoCo motion demos, render MP4, save joint traces."""
from pathlib import Path
import os, json, csv, math
os.environ.setdefault('MUJOCO_GL','osmesa')
import mujoco
import numpy as np
import imageio.v2 as imageio
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).parent/'simulation'; FPS=30; DURATION=10; report={}
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
for version in ('v1','v2'):
    model=mujoco.MjModel.from_xml_path(str(R/f'optik-{version}.xml'));data=mujoco.MjData(model)
    renderer=mujoco.Renderer(model,height=720,width=960)
    camera=mujoco.MjvCamera();camera.lookat[:]=[0,0,.13];camera.distance=.69;camera.azimuth=135;camera.elevation=-18
    ids=[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_JOINT,n) for n in ('pan','tilt')]
    addresses=[model.jnt_qposadr[i] for i in ids];rows=[]
    with imageio.get_writer(R/f'optik-{version}.mp4',fps=FPS,codec='libx264',quality=8,macro_block_size=16) as writer:
      for frame in range(int(FPS*DURATION)):
        target_t=(frame+1)/FPS
        while data.time<target_t-1e-9:
            data.ctrl[:]=[1.25*math.sin(2*math.pi*data.time/DURATION),.95*math.sin(4*math.pi*data.time/DURATION)]
            mujoco.mj_step(model,data)
        assert np.all(np.isfinite(data.qpos)),'Non-finite state'
        assert np.max(np.abs(data.qpos[addresses]))<math.pi/2+.02,'Joint range exceeded'
        rows.append([float(data.time),*map(float,data.ctrl),*map(float,data.qpos[addresses])])
        renderer.update_scene(data,camera=camera)
        im=Image.fromarray(renderer.render());draw=ImageDraw.Draw(im)
        draw.rectangle((0,0,960,62),fill='#17313c')
        draw.text((22,8),f'OPTIK {version.upper()} | MuJoCo hareket gosterimi',font=font,fill='white')
        draw.text((22,35),'Yaklasik dinamik parametreler / fiziksel kalibrasyon yapilmadi',font=font,fill='#bcd9dd')
        writer.append_data(np.asarray(im))
        if frame==45:im.save(R/f'optik-{version}-poster.png')
    renderer.close()
    with (R/f'optik-{version}-joints.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['time_s','command_pan_rad','command_tilt_rad','pan_rad','tilt_rad']);w.writerows(rows)
    a=np.array(rows);errors=np.degrees(np.abs(a[:,1:3]-a[:,3:5]))
    report[version]=dict(duration_s=float(data.time),frames=len(rows),finite_state=True,
      pan_range_deg=np.degrees([a[:,3].min(),a[:,3].max()]).tolist(),tilt_range_deg=np.degrees([a[:,4].min(),a[:,4].max()]).tolist(),
      maximum_demo_tracking_error_deg=errors.max(axis=0).tolist(),note='Illustrative position actuators; not measured MG996R dynamics. Mesh contacts disabled.')
    print('VIDEO_READY',version,flush=True)
(R/'simulation-report.json').write_text(json.dumps(report,indent=2))
