FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN pip install pipenv
COPY Pipfile /code/
COPY Pipfile.lock /code/
RUN pipenv install
COPY . /code/
CMD ["pipenv", "run", "gunicorn clubhouse.wsgi"]

