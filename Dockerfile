FROM python:3.11

WORKDIR /gps-station/

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

EXPOSE 8090/tcp

CMD python station/main.py

