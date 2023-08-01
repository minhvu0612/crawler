FROM python:3.8
COPY . /app
WORKDIR /app
# RUN mkdir Log/
# RUN mkdir listPostCmt/
RUN mkdir listPostCmt_search/
RUN apt-get update
RUN apt-get install -y xvfb gnupg wget curl unzip --no-install-recommends
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - 
RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list 
RUN apt-get update -y 
RUN apt-get install -y google-chrome-stable 
RUN CHROMEVER=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") 
RUN DRIVERVER=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROMEVER") 
RUN wget -q --continue -P /chromedriver "http://chromedriver.storage.googleapis.com/$DRIVERVER/chromedriver_linux64.zip"
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/$DRIVERVER/chromedriver_linux64.zip
RUN unzip /chromedriver/chromedriver* -d /chromedriver
RUN chmod +x /chromedriver/chromedriver
RUN mv /chromedriver/chromedriver /usr/bin/chromedriver
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/bin/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python","-u", "main.py"]
# SHELL ["/bin/bash", "-c", "source .env; python main.py"]
# ENV DISPLAY=:99