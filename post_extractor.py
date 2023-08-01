from abc import ABC, abstractmethod
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from post_model import Post


class PostExtractor(ABC):
    post_element: WebElement
    driver: WebDriver

    def __init__(self, post_element: WebElement, driver: WebDriver):
        self.post_element = post_element
        self.driver = driver       

    @abstractmethod
    def extract_post_author(self):
        pass

    @abstractmethod
    def extract_post_author_link(self):
        pass

    @abstractmethod
    def extract_post_author_avatar_link(self):
        pass

    @abstractmethod
    def extract_post_time(self):
        pass

    @abstractmethod
    def extract_post_content(self):
        pass

    @abstractmethod
    def extract_post_link(self):
        pass

    @abstractmethod
    def extract_post_id(self):
        pass

    @abstractmethod
    def extract_post_photos(self):
        pass

    @abstractmethod
    def extract_post_comments(self):
        pass
    

    def extract(self) -> Post:
        post = Post()
        author = self.extract_post_author()
        author_link = self.extract_post_author_link()
        author_avatar_link = self.extract_post_author_avatar_link()
        created_time = self.extract_post_time()
        content = self.extract_post_content()
        link = self.extract_post_link()
        id = self.extract_post_id()
        comments = self.extract_post_comments()
        image_links = self.extract_post_photos()
        post.id = id
        post.author = author
        post.author_link = author_link
        post.avatar = author_avatar_link
        post.created_time = created_time
        post.content = content
        post.link = link
        post.image_url = image_links
        post.dataInListComments = comments

        return post     
    
