FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /MealPlanner/requirements.txt

WORKDIR /MealPlanner

RUN pip install -r requirements.txt

COPY . /MealPlanner

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]


