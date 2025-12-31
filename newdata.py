from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from urllib.parse import urljoin, urlparse

def get_driver():
    options = Options()
    options.add_argument("--headless=new")     
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def scrape_internship(driver):
    output = "=" * 120 + "\n"
    output += "INTERNSHIP PROGRAMS\n"
    output += "=" * 120 + "\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/internship")
        wait = WebDriverWait(driver, 20)
        time.sleep(5)
 
        try:
            internship_link = driver.find_element(By.LINK_TEXT, "INTERNSHIP")
            internship_link.click()
            time.sleep(2)
        except:
            pass
 
        try:
            accordion_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-controls='collapseSix']"))
            )
            accordion_button.click()
            time.sleep(2)
 
            accordion_content = wait.until(
                EC.visibility_of_element_located((By.ID, "collapseSix"))
            )
 
            rows = accordion_content.find_elements(By.XPATH, ".//tbody/tr")
            
            if rows:
                output += "╔" + "═" * 118 + "╗\n"
                output += "║" + " " * 35 + "AVAILABLE INTERNSHIP PROGRAMS" + " " * 54 + "║\n"
                output += "╚" + "═" * 118 + "╝\n\n"

                headers = ["Technology", "Aim", "Prerequisite", "Learning", "Location"]
                 
                col_width = 23
                header_line = "┌" + "┬".join("─" * col_width for _ in headers) + "┐\n"
                output += header_line
                
                header_content = "│" + "│".join(f"{h:^{col_width}}" for h in headers) + "│\n"
                output += header_content
                
                separator_line = "├" + "┼".join("─" * col_width for _ in headers) + "┤\n"
                output += separator_line
 
                count = 0
                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 5:
                        row_data = [col.text.strip() for col in cols[:5]]
 
                        wrapped_data = []
                        max_lines = 1
                        for cell in row_data:
                            lines = []
                            words = cell.split()
                            current_line = ""
                            for word in words:
                                if len(current_line) + len(word) + 1 <= col_width - 2:
                                    current_line += word + " "
                                else:
                                    if current_line:
                                        lines.append(current_line.strip())
                                    current_line = word + " "
                            if current_line:
                                lines.append(current_line.strip())
                            wrapped_data.append(lines if lines else [""])
                            max_lines = max(max_lines, len(lines))
                         
                        for line_idx in range(max_lines):
                            line_parts = []
                            for cell_lines in wrapped_data:
                                if line_idx < len(cell_lines):
                                    line_parts.append(f"{cell_lines[line_idx]:<{col_width-2}}")
                                else:
                                    line_parts.append(" " * (col_width-2))
                            output += "│ " + " │ ".join(line_parts) + " │\n"
                        
                        count += 1
                        if count < len(rows):
                            output += separator_line
 
                bottom_line = "└" + "┴".join("─" * col_width for _ in headers) + "┘\n"
                output += bottom_line
                
                output += f"\n✅ Total Programs: {count}\n\n"
        except Exception as e:
            output += f"⚠️  Available Internship Programs table not found: {str(e)}\n\n"
 
        try:
            output += "╔" + "═" * 118 + "╗\n"
            output += "║" + " " * 38 + "INTERNSHIP BATCHES SCHEDULE" + " " * 53 + "║\n"
            output += "╚" + "═" * 118 + "╝\n\n"
 
            table_div = wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            
            rows2 = table_div.find_elements(By.XPATH, ".//tbody/tr")
            
            if rows2:
                headers2 = ["Sr.No", "Batch", "Duration", "Start Date", "End Date", "Time", "Fees", "Brochure"]
                widths = [8, 20, 12, 12, 12, 12, 12, 12]
                
                header_line = "┌" + "┬".join("─" * w for w in widths) + "┐\n"
                output += header_line
                
                header_content = "│" + "│".join(f"{h:^{w}}" for h, w in zip(headers2, widths)) + "│\n"
                output += header_content
                
                separator_line = "├" + "┼".join("─" * w for w in widths) + "┤\n"
                output += separator_line

                count = 0
                for row in rows2:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 7:
                        row_data = []
                        for i, col in enumerate(cols[:8]):
                            text = col.text.strip()
                            if i < len(widths):
                                if len(text) > widths[i] - 2:
                                    text = text[:widths[i]-5] + "..."
                            row_data.append(text)
                         
                        while len(row_data) < 8:
                            row_data.append("")
                        
                        row_line = "│" + "│".join(f"{cell:^{w}}" for cell, w in zip(row_data[:8], widths)) + "│\n"
                        output += row_line
                        count += 1
 
                bottom_line = "└" + "┴".join("─" * w for w in widths) + "┘\n"
                output += bottom_line
                
                output += f"\n✅ Total Batches: {count}\n"
            else:
                output += "No batch schedule data available.\n"
                
        except Exception as e:
            output += f"⚠️  Batch schedule table not found: {str(e)}\n"

    except Exception as e:
        output += f"❌ Error scraping internship data: {str(e)}\n"

    output += "\n"
    return output

def scrape_about(driver):
    output = "=" * 120 + "\n"
    output += "ABOUT SUNBEAM\n"
    output += "=" * 120 + "\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/about-us")
        time.sleep(5)
 
        content_selectors = [
            (By.CLASS_NAME, "about-content"),
            (By.CLASS_NAME, "content"),
            (By.TAG_NAME, "article"),
            (By.ID, "about"),
        ]
        
        content_found = False
        for selector_type, selector_value in content_selectors:
            try:
                content_div = driver.find_element(selector_type, selector_value)
                paragraphs = content_div.find_elements(By.TAG_NAME, "p")
                if paragraphs:
                    for p in paragraphs:
                        text = p.text.strip()
                        if len(text) > 20:
                            output += text + "\n\n"
                    content_found = True
                    break
            except:
                continue

        if not content_found:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            seen = set()
            for p in paragraphs:
                text = p.text.strip()
                if text and len(text) > 20 and text not in seen:
                    if not any(skip in text.lower() for skip in ['cookie', 'privacy policy', 'terms', 'copyright', '©']):
                        output += text + "\n\n"
                        seen.add(text)
 
        headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3, h4")
        if headings:
            output += "\n" + "-" * 120 + "\n"
            output += "KEY SECTIONS:\n"
            output += "-" * 120 + "\n"
            for h in headings:
                text = h.text.strip()
                if text and len(text) > 3:
                    output += f"• {text}\n"

    except Exception as e:
        output += f"Error scraping about page: {str(e)}\n"

    output += "\n"
    return output

def scrape_all_course_categories(driver):
    output = "MODULAR COURSES\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/modular-courses-home")
        time.sleep(8)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        all_links = driver.find_elements(By.TAG_NAME,"a")

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
    output = "=" * 120 + "\n"
    output += "CONTACT INFORMATION\n"
    output += "=" * 120 + "\n\n"

    try:
        driver.get("https://www.sunbeaminfo.in/contact-us")
        time.sleep(5)

        body_text = driver.find_element(By.TAG_NAME, "body").text

        phone_pattern = re.compile(r'(?:\+91[-.\s]?)?(?:\d{10}|\d{5}[-.\s]?\d{5}|\d{3}[-.\s]?\d{3}[-.\s]?\d{4})')
        phones = phone_pattern.findall(body_text)

        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(body_text)

        address_elements = driver.find_elements(By.CSS_SELECTOR, "address, .address, .location, .contact-info")
        addresses = []
        for elem in address_elements:
            text = elem.text.strip()
            if len(text) > 20:
                addresses.append(text)

        if not addresses:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for p in paragraphs:
                text = p.text.strip()
                if any(keyword in text.lower() for keyword in ['address', 'office', 'location', 'pune', 'karad', 'hinjewadi']):
                    if len(text) > 20:
                        addresses.append(text)

        if phones:
            output += "📞 PHONE NUMBERS:\n"
            output += "-" * 120 + "\n"
            seen = set()
            for phone in phones:
                if phone not in seen and len(phone) >= 10:
                    output += f"   {phone}\n"
                    seen.add(phone)
            output += "\n"

        if emails:
            output += "📧 EMAIL ADDRESSES:\n"
            output += "-" * 120 + "\n"
            seen = set()
            for email in emails:
                if email not in seen:
                    output += f"   {email}\n"
                    seen.add(email)
            output += "\n"

        if addresses:
            output += "📍 OFFICE LOCATIONS:\n"
            output += "-" * 120 + "\n"
            for i, addr in enumerate(addresses[:5], 1):
                output += f"\nLocation {i}:\n{addr}\n"

        social_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='facebook'], a[href*='twitter'], a[href*='linkedin'], a[href*='instagram'], a[href*='youtube']")
        if social_links:
            output += "\n🌐 SOCIAL MEDIA:\n"
            output += "-" * 120 + "\n"
            seen = set()
            for link in social_links:
                href = link.get_attribute('href')
                if href and href not in seen:
                    output += f"   {href}\n"
                    seen.add(href)

    except Exception as e:
        output += f"Error scraping contact information: {str(e)}\n"

    output += "\n"
    return output

def scrape_additional_pages(driver):
    """Scrape additional informational pages"""
    output = "=" * 120 + "\n"
    output += "ADDITIONAL INFORMATION\n"
    output += "=" * 120 + "\n\n"

    additional_urls = [
        "https://www.sunbeaminfo.in/placements",
        "https://www.sunbeaminfo.in/gallery",
        "https://www.sunbeaminfo.in/testimonials",
        "https://www.sunbeaminfo.in/faculty",
    ]

    for url in additional_urls:
        try:
            driver.get(url)
            time.sleep(5)

            page_title = url.split("/")[-1].replace("-", " ").title()
            output += "\n" + "-" * 120 + "\n"
            output += f"{page_title.upper()}\n"
            output += "-" * 120 + "\n\n"

            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            for p in paragraphs[:10]:
                text = p.text.strip()
                if len(text) > 30:
                    output += text + "\n\n"

            lists = driver.find_elements(By.TAG_NAME, "li")
            if lists:
                for li in lists[:20]:
                    text = li.text.strip()
                    if len(text) > 10:
                        output += f"  • {text}\n"

        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            continue

    return output

def main():
    print("Starting comprehensive Sunbeam website scraping...")
    print("=" * 120)
    
    driver = get_driver()
    output = ""

    try:
        print("\n1. Scraping Internship Programs...")
        internship = scrape_internship(driver)
        print(internship)
        output += internship

        print("\n2. Scraping About Section...")
        about = scrape_about(driver)
        print(about)
        output += about

        print("\n3. Scraping All Courses (This may take a while)...")
        courses = scrape_all_course_categories(driver)
        print(courses)
        output += courses

        print("\n4. Scraping Contact Information...")
        contact = scrape_contact(driver)
        print(contact)
        output += contact

        print("\n5. Scraping Additional Pages...")
        additional = scrape_additional_pages(driver)
        print(additional)
        output += additional

    except Exception as e:
        print(f"\n Error during scraping: {str(e)}")
    
    finally:
        driver.quit()

        with open("datascraping_complete.txt", "w", encoding="utf-8") as f:
            f.write(output)

        print("\n" + "=" * 120)
        print(" Scraping completed successfully!")
        print(f" Data saved to: datascraping_complete.txt")
        print(f" Total output size: {len(output)} characters")
        print("=" * 120)

if __name__ == "__main__":
    main()