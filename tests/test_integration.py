import json, pathlib, subprocess, sys, unittest
root=pathlib.Path(__file__).resolve().parents[1]
exe=root/'build'/('firmwarelab.exe' if sys.platform=='win32' else 'firmwarelab')
def run(commands):
    result=subprocess.run([str(exe)],input='\n'.join(commands)+'\n',text=True,capture_output=True,check=True)
    return [json.loads(line) for line in result.stdout.splitlines()]
class Integration(unittest.TestCase):
    def test_disconnect_recovery(self):
        rows=run(['normal','disconnect']+['normal']*10)
        self.assertEqual(rows[1]['fault'],'SENSOR_INVALID')
        self.assertEqual(rows[-2]['state'],'FAULT')
        self.assertEqual(rows[-1]['state'],'RUNNING')
    def test_stale(self):
        rows=run(['normal']+['stale']*6)
        self.assertEqual(rows[-2]['fault'],'OK')
        self.assertEqual(rows[-1]['fault'],'SENSOR_STALE')
    def test_heat(self):
        rows=run(['heat']*35)
        self.assertIn('WARNING',[r['state'] for r in rows])
        self.assertIn('OVERTEMP',[r['fault'] for r in rows])
    def test_long_run(self):
        rows=run(['normal']*36000)
        self.assertEqual(rows[-1]['ms'],3600000)
        self.assertTrue(all(r['fault']=='OK' and 0<=r['fan']<=1 for r in rows))
    def test_quit(self):
        self.assertEqual(len(run(['normal','quit','normal'])),1)
if __name__=='__main__': unittest.main()
