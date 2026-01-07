docker image rm -f my-image:1

docker build . -t my-image:1


# echo "print('1')" > submission/main.py

# bwrap --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --bind /main/submission /main/submission --chdir /main/submission python3 -u main.py