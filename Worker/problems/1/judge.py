import subprocess
import threading
import queue
import time
import os
import re

def default_compare(str1,str2)->bool:
    s1 = re.sub(r"\s+", "", str1)
    s2 = re.sub(r"\s+", "", str2)
    
    return s1==s2


class Judge:
    AC="AC"
    WR="WR"
    TLE="TLE"
    RE="RE"
    def __init__(self, input_file_path,output_file_path,error_file_path,ans_file_path,time_limit,private=True):
        """
        Middleware judge:
        - Runs judging_file and interacts with submission_file in real-time
        - initial_input: string/bytes to feed to judging file stdin at the start
        """
        self.private=private
        self.time_limit=time_limit
        
        self.input_file_path = input_file_path
        self.error_file_path = error_file_path
        self.output_file_path =output_file_path
        self.ans_file_path=ans_file_path
        self.input_file =None
        self.error_file =None
        self.output_file=None
        
        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.elapsed_time=0
        self.TLE_happened=False
        self.RE_happened=False
        self.process = None 
         

        

    def run(self):
        self.input_file = open(self.input_file_path,"r")
        self.error_file = open(self.error_file_path,"w")
        self.output_file =open(self.output_file_path,"w")

        self._run_judging_file()

        self.input_file.close()
        self.error_file.close()
        self.output_file.close()
        self.output_file =open(self.output_file_path,"r")
        self.ans_file=open(self.ans_file_path,"r")
        return self._judge()

        



    def feed_input(self, data:str):
        """
        Feed data to the judging file's stdin at any time.
        data: str or bytes
        """
        data=data.strip()
        if not self.process or self.process.stdin.closed:
            raise RuntimeError("Judging process not running or stdin closed.")
        if isinstance(data, str):
            data = data.encode()
        self.process.stdin.write(data + b'\n')
        self.process.stdin.flush()

    
    def _enqueue_output(self, out, queue_):
        for line in iter(out.readline, b''):
            queue_.put(line.decode().rstrip())
        out.close()

    def _run_judging_file(self):
        start_time = time.time()
        if(self.private):
            self.process = subprocess.Popen(
                [   
                    'firejail',           
                    '--quiet',           
                    '--private=/main/submission', 
                    'python3',
                    '-u',            
                    'submission/main.py'  
                ],         
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            self.process = subprocess.Popen(
                [   
                    'python3',
                    '-u',            
                    'submission/main.py'  
                ],         
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        # Feed initial input
        self.feed_initial_input()

        # Start threads to read stdout and stderr
        threading.Thread(target=self._enqueue_output, args=(self.process.stdout, self.stdout_queue), daemon=True).start()
        threading.Thread(target=self._enqueue_output, args=(self.process.stderr, self.stderr_queue), daemon=True).start()

        # Main loop: read stdout/stderr and call hooks
        while True:
            if self.process.poll() is not None:
                break  # judging file finished

            self.elapsed_time = time.time() - start_time
            if self.elapsed_time > self.time_limit:
                self.kill()
                self.TLE_happened=True
                break

            # Process stdout
            try:
                while True:
                    line = self.stdout_queue.get_nowait()
                    self.on_stdout(line.strip())
            except queue.Empty:
                pass

            # Process stderr
            try:
                while True:
                    line = self.stderr_queue.get_nowait()
                    self.RE_happened=True
                    self.on_error(line.strip())
            except queue.Empty:
                pass

        self.process.wait()
    def kill(self):
        if self.process and self.process.poll() is None:
            self.process.kill() 
            self.process.wait()

    def feed_initial_input(self):
        """Feed initial input to judging file stdin if provided"""
        self.feed_input(self.input_file.read().strip())

    def on_stdout(self, line):
        print(line)
        self.output_file.write(line.strip()+'\n')
        """Called whenever judging file prints a line to stdout."""
        pass

    def on_error(self, line):
        self.error_file.write(line + "\n")
        """Called whenever judging file prints a line to stderr."""
        pass
    def _judge(self) -> bool:
        if(self.TLE_happened):
            return self.TLE
        if(self.RE_happened):
            return self.RE
        
        if(self.TLE_happened):
            return self.TLE
        if(self.RE_happened):
            return self.RE
        if default_compare(self.ans_file.read(),self.output_file.read()):
            return self.AC
        return self.WR



class MyJudge(Judge):   
    pass

if __name__=="__main__":
    testcases=os.environ.get("testcases","1 2").split(' ')
    os.makedirs("result",exist_ok=True)
    res=open("result/res.txt","w")
    time_limit=float(os.environ.get("time_limit",1))

    for testcase in testcases:
        judge=MyJudge(f"testcases/{testcase}.in",f"result/{testcase}.out",f"result/{testcase}.err",f"testcases/{testcase}.ans",time_limit,True)
        result=judge.run()
        res.write(f"{testcase} : {result}\n")


