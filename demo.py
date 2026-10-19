import pathlib, subprocess, sys
root=pathlib.Path(__file__).resolve().parent
exe=root/'build'/('firmwarelab.exe' if sys.platform=='win32' else 'firmwarelab')
commands=['normal']*30+['disconnect']*10+['normal']*30+['stale']*10+['normal']*20+['heat']*25+['normal']*200
subprocess.run([str(exe)],input='\n'.join(commands)+'\n',text=True,check=True)
