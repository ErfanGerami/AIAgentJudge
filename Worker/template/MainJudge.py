
import os
from judge import MyJudge
import shutil
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
def clean_folder(folder_path, keep_file="main.py"):
    folder_path = os.path.abspath(folder_path)

    if not os.path.isdir(folder_path):
        raise RuntimeError(f"{folder_path} is not a valid folder")

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # Skip the file we want to keep
        if item == keep_file:
            continue

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                print(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed directory: {item_path}")
        except Exception as e:
            print(f"Failed to remove {item_path}: {e}")



if __name__=="__main__":
    testcases=os.environ.get("testcases","1 2").split(' ')
    max_scores=os.environ.get("max_score","1 2").split(' ')
    files=[None if file=="None" else file for file in  os.environ.get("files","None None").split(' ')]
    logger.info(f"Testcases: {testcases}, Max Scores: {max_scores}")
    os.makedirs("result",exist_ok=True)
    res=open("result/res.txt","w")
    time_limit=float(os.environ.get("time_limit",1))

    for i in range(len(testcases)):
        
        testcase=testcases[i]
        max_score=int(max_scores[i])
        file=files[i]
        clean_folder("/main/submission",keep_file="main.py")
        
        if(file):
            shutil.copy(f"./testcases/{file}",f"/main/submission/file.{file.split(".")[-1]}")
        judge=MyJudge(f"testcases/{testcase}.in",f"result/{testcase}.out",f"result/{testcase}.err",f"testcases/{testcase}.ans",time_limit,max_score)
        result,score=judge.run()
        print(result)
        res.write(f"{testcase} : {result} {score}\n")


