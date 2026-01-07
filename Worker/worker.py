import redis
import threading
import logging
from settings import *
from run import run
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  
        logging.FileHandler('worker.log') 
    ]
)
logger = logging.getLogger('worker')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

semaphore = threading.Semaphore(MAX_JOBS)



try:
    r.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" in str(e):
        print("Group already exists")



def do_the_job(job, msg_id):
    try:
        logger.info(f"Starting job {msg_id} for user {job['username']}, problem {job['problem_id']}")
        
        run(
            username=job["username"],
            problem_id=job["problem_id"], 
            submission_id=job["submission_id"],
            testcases=json.loads(job["testcases"]),
            max_scores=json.loads(job["max_score"]),
            files=json.loads(job["files"]),
            time_limit=job["time_limit"],
            memory_limit=job['memory_limit'],
            storage_limit=job['storage_limit']
        )
        
        r.xack(STREAM_NAME, GROUP_NAME, msg_id)
        logger.info(f"Finished job {msg_id} successfully")
        
    except Exception as e:
        logger.error(f"Error processing job {msg_id}: {str(e)}")
    finally:
        semaphore.release()

def process_message():
    while True:
        try:
            semaphore.acquire()
            
            message = r.xreadgroup(
                groupname=GROUP_NAME,
                consumername=CNOSUMER_NAME,
                streams={STREAM_NAME: ">"},
                count=1,
                block=1000 
            )

            if not message:
                logger.debug("No message received, releasing semaphore")
                semaphore.release()
                continue 
                
            stream, jobs = message[0]
            msg_id, job = jobs[0]
            
            logger.info(f"Received new job {msg_id}: {job}")
            
            thread = threading.Thread(target=do_the_job, args=(job, msg_id))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            semaphore.release()

if __name__ == "__main__":
    logger.info(f"Worker starting with consumer name: {CNOSUMER_NAME}")
    logger.info(f"Redis connection: {REDIS_HOST}:{REDIS_PORT}")
    logger.info(f"Stream: {STREAM_NAME}, Group: {GROUP_NAME}")
    logger.info(f"Max concurrent jobs: {MAX_JOBS}")
    
    try:
        process_message()
    except KeyboardInterrupt:
        logger.info("Worker shutting down gracefully...")
    except Exception as e:
        logger.error(f"Worker crashed: {str(e)}")