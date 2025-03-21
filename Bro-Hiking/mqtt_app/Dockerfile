FROM python:3.12

WORKDIR /python-docker
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-u", "app.py"]