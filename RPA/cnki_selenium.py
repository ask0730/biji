import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class CNKISeleniumScraper:
    def __init__(self):
        self.driver = None
        self.papers_data = []
        
    def setup_driver(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
            
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            return False
    
    def wait_for_results(self, timeout=30):
        try:
            wait = WebDriverWait(self.driver, timeout)
            selectors = [
                "#gridTable",
                ".gridTable",
                "#briefBox",
                ".result-table-list",
                "table[class*='result']",
                "tr[class*='result']"
            ]
            
            for selector in selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return True
                except TimeoutException:
                    continue
            
            time.sleep(5)
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            if tables:
                return True
            
            links = self.driver.find_elements(By.TAG_NAME, "a")
            paper_links = [link for link in links if link.text and len(link.text) > 10]
            if paper_links:
                return True
            
            return False
            
        except Exception as e:
            print(f"等待结果失败: {e}")
            return False
    
    def extract_papers_from_page(self):
        papers = []
        
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    paper = self.extract_paper_from_row(row)
                    if paper and paper['title']:
                        papers.append(paper)
            
            if not papers:
                links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        if (text and len(text) > 10 and 
                            href and ('detail' in href or 'kcms' in href)):
                            
                            paper = {
                                'title': text,
                                'authors': '',
                                'journal': '',
                                'publish_time': '',
                                'link': href
                            }
                            
                            parent = link.find_element(By.XPATH, "..")
                            parent_text = parent.text
                            
                            year_match = re.search(r'(19|20)\d{2}', parent_text)
                            if year_match:
                                paper['publish_time'] = year_match.group()
                            
                            papers.append(paper)
                            
                    except Exception:
                        continue
            
            return papers
            
        except Exception as e:
            print(f"提取论文信息失败: {e}")
            return []
    
    def extract_paper_from_row(self, row):
        paper = {
            'title': '',
            'authors': '',
            'journal': '',
            'publish_time': '',
            'link': ''
        }
        
        try:
            links = row.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute('href')
                text = link.text.strip()
                
                if text and len(text) > 10 and href:
                    paper['title'] = text
                    paper['link'] = href
                    break
            
            if not paper['title']:
                return None
            
            cells = row.find_elements(By.TAG_NAME, "td")
            row_text = row.text
            
            for i, cell in enumerate(cells):
                cell_text = cell.text.strip()
                if not cell_text:
                    continue
                
                if i == 1 or '作者' in cell_text:
                    paper['authors'] = cell_text.replace('作者:', '').strip()
                elif i == 2 or '期刊' in cell_text or '来源' in cell_text:
                    paper['journal'] = cell_text.replace('期刊:', '').replace('来源:', '').strip()
                elif re.search(r'(19|20)\d{2}', cell_text):
                    year_match = re.search(r'(19|20)\d{2}', cell_text)
                    if year_match:
                        paper['publish_time'] = year_match.group()
            
            if not paper['publish_time']:
                year_match = re.search(r'(19|20)\d{2}', row_text)
                if year_match:
                    paper['publish_time'] = year_match.group()
            
            return paper
            
        except Exception as e:
            return None
    
    def scrape_papers(self, url, max_pages=3):
        if not self.setup_driver():
            return []
        
        try:
            self.driver.get(url)
            time.sleep(3)
            
            all_papers = []
            
            for page in range(1, max_pages + 1):
                if page > 1:
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".but-r, .next, [title='下一页']")
                        if next_button.is_enabled():
                            next_button.click()
                            time.sleep(3)
                        else:
                            break
                    except NoSuchElementException:
                        break
                
                if self.wait_for_results():
                    papers = self.extract_papers_from_page()
                    if papers:
                        all_papers.extend(papers)
                    else:
                        if page > 1:
                            break
                else:
                    break
                
                if page < max_pages:
                    time.sleep(2)
            
            self.papers_data = all_papers
            return all_papers
            
        except Exception as e:
            print(f"抓取过程失败: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_to_excel(self, papers, filename="首都图书馆相关论文.xlsx"):
        if not papers:
            print("没有数据可保存")
            return False
        
        try:
            data = []
            for paper in papers:
                data.append({
                    '作者(arrayAuthor)': paper.get('authors', ''),
                    '论文名(arrayTitle)': paper.get('title', ''),
                    '期刊名(arrayJournal)': paper.get('journal', ''),
                    '发表时间(arrayTime)': paper.get('publish_time', ''),
                    '链接(arrayHref)': paper.get('link', '')
                })
            
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"数据已保存到: {filename}")
            return True
            
        except Exception as e:
            print(f"保存失败: {e}")
            return False

def main():
    url = "https://kns.cnki.net/kns8s/defaultresult/index?crossids=YSTT4HG0%2CLSTPFY1C%2CJUP3MUPD%2CMPMFIG1A%2CWQ0UVIAA%2CBLZOG7CK%2CPWFIRAGL%2CEMRPGLPA%2CNLBO1Z6R%2CNN3FJMUV&korder=AF&kw=%E9%A6%96%E9%83%BD%E5%9B%BE%E4%B9%A6%E9%A6%86"
    
    try:
        scraper = CNKISeleniumScraper()
        papers = scraper.scrape_papers(url, max_pages=1)
        
        if papers:
            scraper.save_to_excel(papers)
        else:
            print("没有抓取到数据")
            
    except Exception as e:
        print(f"程序执行失败: {e}")

if __name__ == "__main__":
    main()
