# Using the Python Docker image: https://hub.docker.com/_/python
FROM python:3.8

# Changing the working directory
WORKDIR /bot

# Copying the requirements file so that we can pip install later
COPY requirements.txt .

# Installing all the Python dependencies
RUN pip install -r requirements.txt

# Copying the bot source code
COPY . /bot

# Running the bot
CMD python -m ayiko