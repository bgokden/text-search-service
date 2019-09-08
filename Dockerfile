
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

COPY tf_embed.py requirements.txt /app/

WORKDIR /app

RUN pip install -r ./requirements.txt

RUN python tf_embed.py

RUN python -m spacy download xx_ent_wiki_sm

COPY searchlib.py main.py /app/
