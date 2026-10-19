"""Local Tk dashboard; launches the real C executable and exchanges JSON lines."""
import json, pathlib, queue, subprocess, sys, threading, tkinter as tk
from tkinter import messagebox
root=pathlib.Path(__file__).resolve().parent
exe=root/'build'/('firmwarelab.exe' if sys.platform=='win32' else 'firmwarelab')
if not exe.exists(): sys.exit('Run python3 build.py first.')
proc=subprocess.Popen([str(exe)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
inbox=queue.Queue()
def reader():
    try:
        for line in proc.stdout: inbox.put(json.loads(line))
    except Exception as exc: inbox.put({'error':str(exc)})
    finally: inbox.put({'error':'Simulator stopped.'})
threading.Thread(target=reader,daemon=True).start()
app=tk.Tk(); app.title('FirmwareLab | C Controller Simulator'); app.geometry('960x650'); app.configure(bg='#101827')
tk.Label(app,text='FIRMWARELAB',font=('Arial',24,'bold'),fg='#6ee7b7',bg='#101827').pack(pady=(20,4))
tk.Label(app,text='Milestone 1 • simulated time • portable C controller • no RTOS yet',fg='#cbd5e1',bg='#101827').pack()
status=tk.StringVar(value='Starting controller...')
tk.Label(app,textvariable=status,font=('Arial',15),fg='white',bg='#101827').pack(pady=15)
canvas=tk.Canvas(app,bg='#172338',height=310,highlightthickness=0); canvas.pack(fill='x',padx=25)
pending='normal'; history=[]; closing=False; waiting=False
log=tk.StringVar(value='Select a fault below. Normal restores the sensor and normal heat input.')
def command(value):
    global pending
    pending=value
buttons=tk.Frame(app,bg='#101827'); buttons.pack(pady=18)
for label,value in [('Normal / recover','normal'),('Disconnect sensor','disconnect'),('Freeze samples','stale'),('Increase heat','heat'),('Disable','off'),('Enable','on')]:
    tk.Button(buttons,text=label,command=lambda v=value:command(v)).pack(side='left',padx=3)
tk.Label(app,textvariable=log,fg='#fbbf24',bg='#101827',wraplength=900).pack(pady=8)
def send():
    global pending,waiting
    if closing or waiting:return
    try:
        proc.stdin.write(pending+'\n'); proc.stdin.flush(); pending=''; waiting=True
    except (OSError,ValueError): close()
def draw(row):
    history.append(row['temperature']); del history[:-240]
    canvas.delete('all'); w=max(canvas.winfo_width(),100); h=310
    for temp in [25,60,65,80,100,150]:
        y=h-20-temp/160*(h-40)
        canvas.create_line(45,y,w-10,y,fill='#334155')
        canvas.create_text(23,y,text=str(temp),fill='#94a3b8')
    coords=[]
    for i,t in enumerate(history):coords.extend([45+i*(w-60)/239,h-20-max(0,min(160,t))/160*(h-40)])
    if len(coords)>=4:canvas.create_line(*coords,fill='#6ee7b7',width=2)
    canvas.create_text(w-120,15,text='Temperature °C',fill='white')
    status.set(f"{row['state']}   |   {row['temperature']:.1f} °C   |   Fan {row['fan']*100:.0f}%   |   t={row['ms']/1000:.1f}s")
    log.set(f"Fault: {row['fault']}   •   Sample age: {row['age_ms']} ms   •   Recovery: 10 healthy samples below 65 °C")
def poll():
    global waiting
    if closing:return
    try:
        row=inbox.get_nowait()
        if 'error' in row:
            messagebox.showerror('FirmwareLab',row['error']); close(); return
        waiting=False; draw(row); app.after(100,send)
    except queue.Empty:pass
    app.after(20,poll)
def close():
    global closing
    if closing:return
    closing=True
    if proc.poll() is None:
        proc.terminate()
        try:proc.wait(timeout=2)
        except subprocess.TimeoutExpired:proc.kill(); proc.wait()
    app.destroy()
app.protocol('WM_DELETE_WINDOW',close)
app.after(100,send); app.after(20,poll); app.mainloop()
