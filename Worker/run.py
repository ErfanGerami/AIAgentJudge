
import docker
import requests
from settings import *
import time
import os
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  
        logging.FileHandler('worker.log') 
    ]
)
logger = logging.getLogger('worker')


client = docker.from_env()

def run(username,problem_id,submission_id,testcases,max_scores,files,time_limit,memory_limit,storage_limit):
    print("starting container.......")
    container= client.containers.run(
        IMAGE_NAME,
        working_dir="/main",
        command=["sh", "-c", "python3 MainJudge.py"],
        mem_limit=memory_limit,
        # storage_opt={"size": storage_limit},
        environment={"time_limit": time_limit,
                     "testcases":' '.join([str(test) for test in testcases]),
                     "max_score":' '.join([str(test) for test in max_scores]),
                     "files":' '.join([str(file) for file in files])},
        volumes={
            os.path.join(PROBLEMS_PATH,problem_id,"testcases"): {"bind": "/main/testcases", "mode": "ro"},
            # "/etc/resolv.conf": {"bind": "/etc/resolv2.conf", "mode": "ro"},
            os.path.join(PROBLEMS_PATH,problem_id,"judge.py"): {"bind": "/main/judge.py", "mode": "ro"},
            os.path.join(TEMPLATE_PATH,"BaseJudge.py"): {"bind": "/main/BaseJudge.py", "mode": "ro"},
            os.path.join(TEMPLATE_PATH,"MainJudge.py"): {"bind": "/main/MainJudge.py", "mode": "ro"},
            os.path.join(SUBMISSION_PATH,username,problem_id,submission_id): {"bind": "/main/submission", "mode": "rw"},
            os.path.join(RESULTS_PATH,username,problem_id,submission_id): {"bind": "/main/result", "mode": "rw"},
        },
        privileged=True,
        cap_add=["ALL"],  
        security_opt=[
            "apparmor:unconfined", 
            "seccomp=unconfined"
        ],
        network_mode="host", 
        pid_mode="host",
        detach=True,

    )
    for line in container.logs(stream=True):
        logger.info(line.decode().strip())
    print("waiting for the container to finish")
    logger.info("salam")
    container.wait()


    with open(os.path.join(os.getcwd(),"results",username,problem_id,submission_id,"res.txt")) as f:
        test_cases_result = {}
        for line in f:
            if ":" in line:
                key, val = line.strip().split(":")
                val=val.split()
                res=val[0].strip()
                score=int(val[1].strip())
                # logger.info(key,res,score)
                test_cases_result[key.strip()] = {"result":res,"score":score}

    data={"submission_id":submission_id,"result":test_cases_result,'api-key':API_KEY}
    logger.info("reporting the result to the backend")
    for _ in range(100):
        response = requests.post(REPORT_API, json=data)
        if response.status_code == 200:
            break
        time.sleep(3)
    # container.remove()


