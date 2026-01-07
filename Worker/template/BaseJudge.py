import subprocess
import threading
import queue
import time
import os
import re
import logging

import stat
import pwd

from typing import Tuple 
def default_compare(str1, str2) -> bool:
    s1 = re.sub(r"\s+", "", str1)
    s2 = re.sub(r"\s+", "", str2)
    s1=str(s1).lower()
    s2=str(s2).lower()
    return s1 == s2

class BaseJudge:
    AC = "AC"
    WR = "WR"
    TLE = "TLE"
    RE = "RE"
    
    def __init__(self,input_file_path, output_file_path, error_file_path, ans_file_path, time_limit,max_score, private=True):
        self.private = private
        self.time_limit = time_limit
        self.max_score=max_score
        
        self.output_file_path = output_file_path
        self.error_file_path = error_file_path
        self.ans_file_path = ans_file_path
        self.input_file_path=input_file_path

        self.stdout_queue = queue.Queue()
        self.stderr_queue = queue.Queue()
        self.elapsed_time = 0
        self.TLE_happened = False
        self.RE_happened = False
        self.process = None
        self.output_content = ""
        self.error_content = ""
        


    def run(self)-> tuple[str, int]:

        self.output_file = open(self.output_file_path, "w")
        self.error_file = open(self.error_file_path, "w")
        self.input_file = open(self.input_file_path, "r")
        self.prepare()
        try:
            self._run_judging_file()
            self.output_file.close()
            
            self.output_file = open(self.output_file_path, "r")
            self.ans_file = open(self.ans_file_path, "r")
            result = self._judge()
            
            return result
        finally:
            for f in [self.input_file, self.output_file, self.error_file, self.ans_file]:
                if f and not f.closed:
                    f.close()
    
    def feed_input(self, data: str):
        """Feed data to the process stdin - user controls when and what to feed"""
        if not self.process or self.process.stdin.closed:
            return False
            
        data = data.strip()
        if not data:
            return True
            
        try:
            if isinstance(data, str):
                data = data.encode()
            self.process.stdin.write(data + b'\n')
            self.process.stdin.flush()
            return True
        except (BrokenPipeError, OSError):
            self.RE_happened = True
            return False


    def _enqueue_output(self, out, queue_):
        try:
            for line in iter(out.readline, b''):
                queue_.put(line.decode(errors='replace').rstrip())
        except Exception as e:
            queue_.put(f"ERROR IN THREAD: {str(e)}")
        finally:
            out.close()

    def _run_judging_file(self):

        start_time = time.time()
        
        # Build command based on private flag
        if self.private:
            cmd = [
            'bwrap',
            '--ro-bind', '/usr', '/usr',              # Python and libraries
            '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64',
            '--ro-bind', '/usr/lib', '/usr/lib',      # Additional libraries
            '--bind', '/main/submission', '/main/submission',  # Only writable dir
            '--bind', '/etc/resolv.conf', '/etc/resolv.conf',  # DNS resolution
            '--chdir', '/main/submission',
            '--tmpfs', '/tmp',                        # Temporary files
            '--tmpfs', '/home',                       # No home access
            '--proc', '/proc',                        # Minimal proc
            '--dev', '/dev',                          # Minimal dev
            'python3',
            '-u',
            'main.py'
        ]
        else:
            cmd = [
                'python3',
                '-u',
                'main.py'
            ]

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd='/main/submission',
            bufsize=0  # Unbuffered
        )
        # Start threads to read stdout and stderr
        stdout_thread = threading.Thread(
            target=self._enqueue_output, 
            args=(self.process.stdout, self.stdout_queue), 
            daemon=True
        )
        stderr_thread = threading.Thread(
            target=self._enqueue_output, 
            args=(self.process.stderr, self.stderr_queue), 
            daemon=True
        )
        stdout_thread.start()
        stderr_thread.start()
        # Call user-defined initial input feeding
        self.feed_initial_input()
        # Main loop: read stdout/stderr and call hooks
        while True:
            # Check time limit
            self.elapsed_time = time.time() - start_time
            if self.elapsed_time > self.time_limit:
                self.TLE_happened = True
                self.kill()
                break
            # Check if process finished
            return_code = self.process.poll()
            if return_code is not None:
                # Process finished, drain remaining output
                break
            # Process stdout with timeout
            try:
                while True:
                    line = self.stdout_queue.get(timeout=0.1)
                    self.on_stdout(line)
            except queue.Empty:
                pass
            # Process stderr
            try:
                while True:
                    line = self.stderr_queue.get_nowait()
                    self.RE_happened = True
                    self.on_error(line)
            except queue.Empty:
                pass
        # Drain remaining output after process ends or TLE
        self._drain_queues()
        # Wait for process to terminate completely
        if self.process.poll() is None:
            self.process.wait(timeout=1.0)
        

    def _drain_queues(self):
        """Drain all remaining content from queues"""
        # Drain stdout
        while True:
            try:
                line = self.stdout_queue.get_nowait()
                self.on_stdout(line)
            except queue.Empty:
                break
        
        # Drain stderr
        while True:
            try:
                line = self.stderr_queue.get_nowait()
                self.RE_happened = True
                self.on_error(line)
            except queue.Empty:
                break

    def kill(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            except Exception:
                pass
    def prepare(self):
        pass
    def feed_initial_input(self):
        """Override this method to provide initial input to the program"""
        for line in self.input_file.readlines():
            self.feed_input(line.strip())
        pass
    def on_stdout(self, line):
        """Called whenever judging file prints a line to stdout."""
        print(line)
        self.output_file.write(line + '\n')
        self.output_file.flush()
        self.output_content += line + '\n'

    def on_error(self, line):
        """Called whenever judging file prints a line to stderr."""
        print(f"STDERR: {line}")
        self.error_file.write(line + "\n")
        self.error_file.flush()
        self.error_content += line + '\n'

    def _judge(self) -> tuple[str, int]:
        if self.TLE_happened:
            return (self.TLE,0)
        if self.RE_happened:
            return (self.RE,0)
        
        try:
            with open(self.output_file_path, "r") as f:
                output_content = f.read()
            
            with open(self.ans_file_path, "r") as f:
                ans_content = f.read()
            
            if default_compare(ans_content, output_content):
                return (self.AC,self.max_score)
            else:
                return (self.WR,0)
                
        except Exception as e:
            print(f"Error during file comparison: {e}")
            return (self.RE,0)

