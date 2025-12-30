from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
 
def get_driver():
    options = Options()
    options.add_argument("--headless=new")     
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

 
def scrape_internship(driver):
    output = "INTERNSHIP PROGRAMS\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/internship")
        wait = WebDriverWait(driver, 20)
        time.sleep(5)

        table = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
        )

        rows = table.find_elements(By.TAG_NAME, "tr")
        count = 1

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 7:
                output += (
                    f"Internship {count}\n"
                    f"Batch Name   : {cols[1].text.strip()}\n"
                    f"Duration     : {cols[2].text.strip()}\n"
                    f"Start Date   : {cols[3].text.strip()}\n"
                    f"End Date     : {cols[4].text.strip()}\n"
                    f"Time         : {cols[5].text.strip()}\n"
                    f"Fees         : Rs. {cols[6].text.strip()}\n\n"
                )
                count += 1

        if count == 1:
            output += "Internship data not available.\n\n"

    except Exception:
        output += "Internship data not available.\n\n"

    return output

 
def scrape_about(driver):
    output = "ABOUT SUNBEAM\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/about-us")
        time.sleep(5)

        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        seen = set()

        for p in paragraphs:
            text = p.text.strip()
            if text and text not in seen:
                output += text + "\n\n"
                seen.add(text)

        if not seen:
            output += "About content not available.\n\n"

    except Exception:
        output += "About content not available.\n\n"

    return output
 
def scrape_courses(driver):
    output = "MODULAR COURSES\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/modular-courses-home")
        time.sleep(8)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        all_links = driver.find_elements(By.TAG_NAME, "a")

        course_urls = []
        seen = set()

        for link in all_links:
            try:
                href = link.get_attribute("href")

                if not href or "/modular-courses/" not in href:
                    continue
                if "modular-courses-home" in href:
                    continue
                if href in seen:
                    continue

                seen.add(href)
                course_urls.append(href)

            except:
                continue

        count = 1
        for url in sorted(course_urls):
            try:
                driver.get(url)
                time.sleep(4)

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # ---------------- COURSE NAME (FIXED) ----------------
                course_name = ""
                try:
                    course_name = driver.find_element(By.TAG_NAME, "h1").text.strip()
                except:
                    try:
                        course_name = driver.title.split("|")[0].strip()
                    except:
                        course_name = url.split("/")[-1].replace("-", " ").title()

                # remove bad names like "COURSES"
                if course_name.lower() in ["courses", "course", "modular courses"]:
                    course_name = url.split("/")[-1].replace("-", " ").title()

                # ---------------- HEADER FORMAT (EXACT) ----------------
                output += "=" * 100 + "\n"
                output += f"COURSE {count}: {course_name}\n"
                output += "=" * 100 + "\n\n"

                body_text = driver.find_element(By.TAG_NAME, "body").text

                has_schedule = False

                batch_info = re.search(r'Batch Schedule\s*:?\s*(.+?)(?:\n|$)', body_text, re.IGNORECASE)
                if batch_info:
                    output += f"Batch Schedule : {batch_info.group(1).strip()}\n"
                    has_schedule = True

                schedule_info = re.search(r'(?:^|\n)Schedule\s*:?\s*(.+?)(?:\n|$)', body_text, re.IGNORECASE)
                if schedule_info:
                    output += f"Schedule       : {schedule_info.group(1).strip()}\n"
                    has_schedule = True

                duration_info = re.search(r'Duration\s*:?\s*(\d+\s*hrs?\.?)', body_text, re.IGNORECASE)
                if duration_info:
                    output += f"Duration       : {duration_info.group(1).strip()}\n"
                    has_schedule = True

                timings_info = re.search(r'Timings?\s*:?\s*(.+?)(?:\n|$)', body_text, re.IGNORECASE)
                if timings_info:
                    output += f"Timings        : {timings_info.group(1).strip()}\n"
                    has_schedule = True

                fees_info = re.search(r'Fees?\s*:?\s*(Rs\.?\s*[\d,]+/?-?\s*(?:\(.*?\))?)', body_text, re.IGNORECASE)
                if fees_info:
                    output += f"Fees           : {fees_info.group(1).strip()}\n"
                    has_schedule = True

                output += f"Link           : {url}\n"

                if has_schedule:
                    output += "\n" + "-" * 100 + "\n\n"

                # ---------------- PREREQUISITES ----------------
                prereq_match = re.search(
                    r'Prerequisites?:?\s*(.*?)(?=\n(?:Section|Module|Course Content|Syllabus|What You Will Learn)|$)',
                    body_text, re.IGNORECASE | re.DOTALL
                )

                if prereq_match:
                    prereq_lines = [
                        l.strip() for l in prereq_match.group(1).split('\n')
                        if l.strip() and len(l) > 5
                        and not any(x in l.lower() for x in
                                    ['view more', 'register', 'contact', 'phone', 'email', 'batch'])
                    ]

                    if prereq_lines:
                        output += "PREREQUISITES:\n"
                        for line in prereq_lines[:10]:
                            output += f"  • {line}\n"
                        output += "\n" + "-" * 100 + "\n\n"

                # ---------------- SYLLABUS ----------------
                output += "COURSE SYLLABUS:\n\n"

                section_pattern = re.compile(
                    r'((?:Section|Module|Unit|Chapter)\s+\d+)[:\s]*([^\n]+?)(?:\n|$)'
                    r'(.*?)(?=(?:Section|Module|Unit|Chapter)\s+\d+|Prerequisites|Fees|Batch Schedule|Register|Contact|$)',
                    re.IGNORECASE | re.DOTALL
                )

                sections = section_pattern.findall(body_text)

                if sections:
                    for sec_no, sec_title, sec_content in sections:
                        output += f"{sec_no}: {sec_title.strip()}\n"
                        lines = [
                            l.strip() for l in sec_content.split('\n')
                            if l.strip() and len(l) > 3
                            and not any(x in l.lower() for x in
                                        ['view more', 'register', 'contact', 'phone', 'email'])
                        ]
                        for line in lines[:25]:
                            output += f"  - {line}\n"
                        output += "\n"
                else:
                    paragraphs = driver.find_elements(By.TAG_NAME, "p")
                    added = 0
                    for p in paragraphs:
                        text = p.text.strip()
                        if len(text) > 40 and added < 15:
                            output += text + "\n\n"
                            added += 1

                output += "\n"
                count += 1

            except:
                continue

        if count == 1:
            output += "Course data not available.\n"

    except Exception as e:
        output += f"Course data not available. Error: {str(e)}\n"

    return output

def scrape_contact(driver):
    output = "CONTACT US\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/contact-us")
        time.sleep(5)
 
        body_text = driver.find_element(By.TAG_NAME, "body").text
         
        phone_pattern = re.compile(r'(?:\+91[-.\s]?)?(?:\d{10}|\d{5}[-.\s]?\d{5})')
        phones = phone_pattern.findall(body_text)
         
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(body_text)
         
        address_keywords = ['Address', 'Location', 'Office']
        address_lines = []
        
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        for p in paragraphs:
            text = p.text.strip()
            if any(keyword.lower() in text.lower() for keyword in address_keywords):
                if text and len(text) > 20:  
                    address_lines.append(text)
         
        try:
            contact_divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='contact'], div[class*='address']")
            for div in contact_divs:
                text = div.text.strip()
                if text and text not in address_lines:
                    address_lines.append(text)
        except:
            pass
         
        if phones:
            output += "Phone Numbers:\n"
            seen_phones = set()
            for phone in phones:
                if phone not in seen_phones and len(phone) >= 10:
                    output += f"  {phone}\n"
                    seen_phones.add(phone)
            output += "\n"
        
        if emails:
            output += "Email Addresses:\n"
            seen_emails = set()
            for email in emails:
                if email not in seen_emails:
                    output += f"  {email}\n"
                    seen_emails.add(email)
            output += "\n"
        
        if address_lines:
            output += "Address/Location:\n"
            for addr in address_lines[:3]:  
                output += f"  {addr}\n\n"
        
        if not phones and not emails and not address_lines:
            output += "Contact information not available.\n"

    except Exception as e:
        output += f"Contact information not available. Error: {str(e)}\n"

    return output
 
def main():
    driver = get_driver()

    print(scrape_internship(driver))
    print("=" * 100)

    print(scrape_about(driver))
    print("=" * 100)

    print(scrape_courses(driver))
    print("=" * 100)

    print(scrape_contact(driver))
    print("=" * 100)

    driver.quit()


if __name__ == "__main__":
    main()