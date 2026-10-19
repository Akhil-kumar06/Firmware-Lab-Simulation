"""Build portable C11 sources using GCC or Clang. No Python packages required."""
import pathlib, shutil, subprocess, sys
root=pathlib.Path(__file__).resolve().parent
out=root/'build'; out.mkdir(exist_ok=True)
cc=shutil.which('gcc') or shutil.which('clang')
if not cc: sys.exit('Install GCC or Clang first. See README.md.')
ext='.exe' if sys.platform=='win32' else ''
flags=['-std=c11','-Wall','-Wextra','-Werror','-pedantic','-O2','-I',str(root/'src')]
for name,source in [('firmwarelab','src/main.c'),('test_controller','tests/test_controller.c')]:
    subprocess.run([cc,*flags,str(root/'src/controller.c'),str(root/source),'-o',str(out/(name+ext))],check=True)
subprocess.run([str(out/('test_controller'+ext))],check=True)
subprocess.run([sys.executable,str(root/'tests/test_integration.py')],check=True)
print('Build and tests passed. Run: python3 dashboard.py')
