from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException

from dotenv import load_dotenv
import time
import MySQLdb
import os
load_dotenv()

class Post:
    def __init__(self, post):
        self.post_writer_profile_url = post.get("post_writer_profile_url", "")
        self.writer_details = post.get("writer_details", "")
        self.post_text = post.get("post_text", "")
        self.post_title = post.get("post_title", "")
        self.post_link = post.get("post_link", "")
        self.writer_image = post.get("writer_image", "")

    def __str__(self):
        return (
            # f"post_writer_profile_url: {self.post_writer_profile_url},"
            f"\n"+"- - - - - - - - - - - -"
            f"\n{self.writer_details},"
            f"\n"+"- - - - - - - - - - - -"
            f"\n{self.post_title},\n"
            f"\n"+"- - - - - - - - - - - -"
            # f"\n\npost_link: {self.post_link},"
            # f"\n\nwriter_image: {self.writer_image}"
        )

def get_post_title(post_element, post):
    try:
        post["post_title"] = post_element.find_element(By.CLASS_NAME, "entity-result__embedded-object-title").text
    except:
        pass

def get_post_text(post_element, post):
    try:
        post["post_text"] = post_element.find_element(By.CLASS_NAME, "entity-result__summary").text
    except:
        pass

def get_writer_image(post_element, post):
    try:
        a_elements = post_element.find_elements(By.CSS_SELECTOR, 'img.presence-entity__image')
        srcs = [a.get_attribute('src') for a in a_elements]
        post['writer_image'] = srcs[0]
    except:
        pass

def get_post_link(post_element, post):
    try:
        a_elements = post_element.find_elements(By.CSS_SELECTOR, 'a.app-aware-link[target="_self"]')
        hrefs = [a.get_attribute('href') for a in a_elements]
        post['post_link'] = hrefs[0]
    except:
        pass

def login_to_linkedin(username, password):
    driver.get("https://www.linkedin.com/?original_referer=")
    time.sleep(3)
    # find username/email field and send the username itself to the input field
    driver.find_element("name", "session_key").send_keys(username)
    # find password input field and insert password as well
    driver.find_element("name", "session_password").send_keys(password)

    # click login button
    sign_in_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
    # Click the "Sign in" button
    sign_in_button.click()
    print(f"Loged In to account : {username}")

def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

def contains_keywords(post_data, target_variations = ["js", "javascript"]):
    for field_value in post_data:
        if isinstance(field_value, str):
            normalized_value = field_value.lower().replace("-", "").replace(" ", "")
            if any(variation in normalized_value for variation in target_variations):
                return True
    return False

def click_show_more_button():
    try:
        show_more_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(span, "Show more results")]'))
        )
        show_more_button.click()
    except (TimeoutException, StaleElementReferenceException):
        print("TimeoutException or StaleElementReferenceException: Show more button not found or not clickable. Continuing...")
    except NoSuchElementException:
        print("NoSuchElementException: Show more button not found. Continuing...")


# Linkedin credentials
username = "eliya.yosef@gmail.com"
password = "_______________"

db_port = int(os.getenv("DB_PORT"))

mysql_config = MySQLdb.connect(
    host=os.getenv("DB_HOST"),
    port=db_port,
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)
cursor = mysql_config.cursor()
print("Mysql is connected.")

driver = webdriver.Chrome()
print("Web Driver created")

insert_query = (
    "INSERT INTO posts "
    "(post_writer_profile_url, writer_details, post_text, post_title, post_link,writer_image,profile_post_count) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
)

login_to_linkedin(username, password)
time.sleep(20)
print("\033[91msleeped\033[0m")

driver.get("https://www.linkedin.com/my-items/saved-posts/")
print("Open Your posts.")
time.sleep(6)

scroll_to_bottom()
posts_counter = 1
i =1

while True and i < 10:
    print('- ' * 8 + "\n")
    print("\033[91m#\nStarting\033[0m\n")
    posts_elements = driver.find_elements(By.CLASS_NAME, "entity-result__content-container")
    for post_element in posts_elements:
        print('\033[92m- ' * 12 + "\033[0m")
        
        post = {}
        print("\033[91m\ninserted : "+str(i)+"\nposts_counter : "+str(posts_counter)+"#\n\033[0m")
        if post_element:

            post['writer_image'] = post["post_text"] = post["post_title"] = post["post_link"] = ""
            post["post_writer_profile_url"] = post_element.find_element(By.CLASS_NAME, "app-aware-link").get_attribute("href")
            post["writer_details"] = post_element.find_element(By.CLASS_NAME, "entity-result__title-text").text
            
            get_writer_image(post_element,post)
            get_post_link(post_element,post)
            get_post_text(post_element,post)            
            get_post_title(post_element,post)
            
            posts_counter+=1

            if not post["post_link"]:
                print("\033[91m#No Post Link\033[0m\n\n")
                continue  

            poster = Post(post)
            
            post_data = (
                post["post_writer_profile_url"],
                post["writer_details"],
                post["post_text"],
                post["post_title"],
                post["post_link"],
                post["writer_image"],
                i
            )
            print(poster)
            if contains_keywords(post_data, ["js", "javascript"]):
                try:
                    cursor.execute(insert_query, post_data)
                    i+=1
                    mysql_config.commit()
                except MySQLdb.IntegrityError as e:
                    if "Duplicate entry" in str(e):
                        print("\033[91m#\nDuplicate entries on DB\033[0m\n")
                        # Handle duplicate entry case here
                    elif "foreign key constraint fails" in str(e):
                        print("\033[91m#\nForeign key constraint violation\033[0m\n")
                        # Handle foreign key violation case here
                    else:
                        print("\033[91m#\nOther IntegrityError: {}\033[0m\n".format(e))
                        # Handle other IntegrityError cases here
                        mysql_config.rollback()  # Rollback changes
                except MySQLdb.Error as e:
                    print("\033[91m#\nMySQL Error: {}\033[0m\n".format(e))
                    # Handle other MySQL errors here
                    mysql_config.rollback()  # Rollback changes
                except Exception as e:
                    print("\033[91m#\nUnexpected Error: {}\033[0m\n".format(e))
                    # Handle other unexpected errors here
                    mysql_config.rollback()  # Rollback changes
                time.sleep(2)
            else:
                print("\033[93m#\nSkipping row - 'writer_details' does not contain 'JS'\033[0m\n")
    scroll_to_bottom()
    time.sleep(3)
    click_show_more_button()
    time.sleep(3)
    scroll_to_bottom()

driver.quit()
