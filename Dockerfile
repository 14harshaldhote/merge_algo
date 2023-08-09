# FROM python:3.9
# WORKDIR /app
# COPY . /app
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
# EXPOSE 8080
# CMD ["flask", "run", "--host", "0.0.0.0"]


FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8080
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=8080
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]
