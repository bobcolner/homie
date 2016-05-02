FROM python:3.5
WORKDIR /homeie
COPY . /homeie
RUN git clone https://github.com/bobcolner/pgrap.git
RUN pip install -r requirements.txt
CMD python3 homeie.py
