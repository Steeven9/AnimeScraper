FROM python:3

WORKDIR /usr/src/app
CMD [ "python", "-u", "./main.py" ]

COPY . .
RUN pip install --no-cache-dir deps/*.whl
RUN pip install --no-cache-dir -r requirements.txt
