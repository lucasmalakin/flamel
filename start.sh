export > /export

python3 setup.py develop 2>&1 | tee -a /setup.log
echo "Starting Jupyter..." >&2
jupyter notebook --allow-root --ip=0.0.0.0 | tee -a /jupyter.log &
