FROM python:3.9
ADD ./requirements.txt .
RUN python3 -m pip install -r requirements.txt
ADD ./config.yaml .
ADD ./main.py .
ENTRYPOINT ["./main.py"]
