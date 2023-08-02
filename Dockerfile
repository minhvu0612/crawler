FROM python:3.8
COPY . /app
WORKDIR /app
# RUN mkdir Log/
# RUN mkdir listPostCmt/
RUN mkdir listPostCmt_search/

RUN apt-get update && \
    apt-get install -y xvfb gnupg wget curl unzip --no-install-recommends && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    CHROME_VERSION="114.0.5735.90-1" && \
    wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}_amd64.deb \
    && apt install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb && \
    CHROME_VER=$(google-chrome --product-version | grep -o "[^\.]*\.[^\.]*\.[^\.]*") && \
    DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VER) && \
    wget https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin/ && rm chromedriver_linux64.zip && chmod +x /usr/bin/chromedriver

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python","-u", "main.py"]
# SHELL ["/bin/bash", "-c", "source .env; python main.py"]