FROM python:3.10.6

WORKDIR /data_visualization
COPY . /data_visualization/

RUN pip install -r requirements.txt

EXPOSE 8050

CMD [ "python", "data_visualization/app.py" ]