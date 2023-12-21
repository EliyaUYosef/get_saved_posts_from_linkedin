from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from dotenv import load_dotenv
import MySQLdb
import os
import time

load_dotenv()

class Post:
    def __init__(self, post):
        # print(post)
        self.id = post[0]
        self.post_writer_profile_url = post[1]
        self.writer_details = post[2]
        self.post_text = post[3]
        self.post_title = post[4]
        self.post_link = post[5]
        self.writer_image = post[6]
    def get_post_link(self):
        return self.post_link
    def get_id(self):
        return self.id
    def __str__(self):
        return (
            f"post_writer_profile_url: {self.post_writer_profile_url},"
            f"\n\nwriter_details: {self.writer_details},"
            f"\n\npost_title: {self.post_title},"
            f"\n\npost_link: {self.post_link},"
            f"\n\nwriter_image: {self.writer_image}"
        )

def get_post_from_db():
    select_query = "SELECT * FROM posts WHERE full_text is NULL ORDER BY id DESC  LIMIT 1 "
    cursor.execute(select_query)
    result = cursor.fetchone()
    if result:
        poster = Post(result)
        return poster
    else:
        return None
def hover_the_file_preview():
    li_element = driver.find_element(By.XPATH, "//li[@class='carousel-slide-active']")
    actions = ActionChains(driver)

    actions.move_to_element(li_element)
    # Perform the hover action
    actions.perform()

def update_post_status(post_id,full_text, media_link):
    update_query = "UPDATE posts SET full_text = %s, media_link = %s WHERE id = %s"
    cursor.execute(update_query, (full_text, media_link,post_id,))
    mysql_config.commit()

def click_on_full_screen_button():
    actions = ActionChains(driver)
    # button_to_click = driver.find_element(By.CSS_SELECTOR, "button.ssplayer-fullscreen-on-button")
    button_to_click = driver.find_element(By.XPATH, "//button[@class='ssplayer-fullscreen-on-button']")
    actions.click(button_to_click).perform()

def get_additional_info(post_link):
    driver.get(post_link)
    time.sleep(6)
    # hover_the_file_preview()
    print("hovered - 1")
    # click_on_full_screen_button()
    print("full screen clicked")
    virus_scan_container = driver.find_element(By.CLASS_NAME, "ssplayer-virus-scan-container")
    WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "ssplayer-virus-scan-container")))

    # Locate and click the download button
    download_button = driver.find_element(By.CLASS_NAME, "ssplayer-virus-scan-container__download-button")
    download_button.click()
    time.sleep(1)
    # hover_the_file_preview()
    print("hovered - 2")
    button_to_click = driver.find_element(By.CLASS_NAME, "ssplayer-virus-scan-container__download-button").get_attribute('href')
    print("Found it :"+button_to_click)
    time.sleep(5)
    # button_to_click.click()
    time.sleep(100)
    
    time.sleep(1)
    # for pdf, find the button : 
    # hover on pdf preview
    #   click on : ssplayer-fullscreen-on-button
    
    #   click on : button with class : ssplayer-topbar-action ssplayer-topbar-action-download
    # # button_to_click = driver.find_element(By.CLASS_NAME, "ssplayer-fullscreen-on-button")
    # # button_to_click.click()
    #   get href : ssplayer-virus-scan-container__download-button
    

def process_post(post):
    # Get additional information using Selenium
    post_new_data = get_additional_info(post.get_post_link())
    # Update the processed status in the database
    update_post_status(post.get_id())
    # Print or do further processing if needed
    poster = Post(post)
    print("\n\nProcessing Post:\n", poster)


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

# Linkedin credentials
username = "eliya.yosef@gmail.com"
password = "GRq_VWy6gR*eG?G"

db_port = int(os.getenv("DB_PORT"))

mysql_config = MySQLdb.connect(
    host=os.getenv("DB_HOST"),
    port=db_port,
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_DATABASE")
)
cursor = mysql_config.cursor()

driver = webdriver.Chrome()
print("start loop")

login_to_linkedin(username, password)
time.sleep(7)
try:
    while True:
        poster = get_post_from_db()
        if not poster:
            print("No more unprocessed posts.")
            break

        print(poster.get_post_link())
        time.sleep(12)

        process_post(poster)

        # Optional: Add a delay between processing posts to avoid overloading the website
        time.sleep(2)

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver and database connection
    driver.quit()
    mysql_config.close()
