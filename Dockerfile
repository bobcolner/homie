FROM python:3.5
WORKDIR /homie
COPY . /homie
RUN rm -r ./pgrap && git clone https://github.com/bobcolner/pgrap.git
RUN pip install -r requirements.txt
