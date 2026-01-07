import os

REDIS_HOST=os.environ.get("REDIS_HOST","localhost")
REDIS_PORT=os.environ.get("REDIS_PORT","6379")
CNOSUMER_NAME=os.environ.get("CONSUMER_NAME","worker1")
MAX_JOBS=int(os.environ.get("MAX_JOBS",5))
STREAM_NAME=os.environ.get("STREAM_NAME","job_stream")
GROUP_NAME=os.environ.get("GROUP_NAME","judgers")
IMAGE_NAME=os.environ.get("IMAGE_NAME","my-image:1")
API_KEY=os.environ.get("API_KEY","api-key")
REPORT_API=os.environ.get("REPORT_API","localhost")

PATH_ON_HOST=os.environ.get("PATH_ON_HOST","/home/erfan/Desktop/projects/Judge/Worker")
PROBLEMS_PATH=os.environ.get("PROBLEMS_PATH","/home/erfan/Desktop/projects/Judge/JudgeBackend/media/problems")
SUBMISSION_PATH=os.environ.get("SUBMISSION_PATH","/home/erfan/Desktop/projects/Judge/JudgeBackend/media/submissions")
RESULTS_PATH=os.environ.get("RESULTS_PATH","/home/erfan/Desktop/projects/Judge/Worker/results")
TEMPLATE_PATH=os.environ.get("TEMPLATE_PATH","/home/erfan/Desktop/projects/Judge/Worker/template")
