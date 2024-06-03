# 信息抽提

## 启动
```python

# 192.168.110.62-pc
conda activate base

scp -r user@192.168.110.94:/data/1_qunosen/project/key_pharse/gpt_task/ ./

pip install -r requirements.txt

pm2 start /home/anaconda3/bin/python --name gpt_task  /data/qhs/gpt_task/llm.py






```