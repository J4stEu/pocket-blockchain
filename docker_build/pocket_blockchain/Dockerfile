FROM python:3
SHELL ["/bin/bash", "-c"]
ENV PYTHONUNBUFFERED 1

RUN mkdir /pocket_blockchain
RUN mkdir /pocket_blockchain/blockchain_backend
RUN mkdir /pocket_blockchain/blockchain_backend/app
RUN mkdir /pocket_blockchain/blockchain_frontend
WORKDIR /pocket_blockchain

ENV VIRTUAL_ENV=/blockchain_backend/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY ./blockchain_backend/requirements.txt ./blockchain_backend/
RUN pip install -r ./blockchain_backend/requirements.txt
COPY ./blockchain_backend/app ./blockchain_backend/app
COPY ./blockchain_backend/main.py ./blockchain_backend/
COPY ./blockchain_backend/init_db.py ./blockchain_backend/

COPY ./blockchain_frontend ./blockchain_frontend/
WORKDIR /pocket_blockchain/blockchain_frontend
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
RUN source /root/.bashrc  \
    && nvm install v14.19.2  \
    && nvm use v14.19.2  \
    && nvm alias default v14.19.2  \
    && npm install --global yarn \
    && yarn install \
    && yarn build


WORKDIR /pocket_blockchain/blockchain_backend

#CMD python main.py
CMD bash -c "python init_db.py && gunicorn --bind 0.0.0.0:5001 -w 5 main:app"
#CMD bash -c "source venv/bin/activate && python init_db.py && gunicorn --bind 0.0.0.0:5001 -w 5 main:app"
#CMD python init_db.py