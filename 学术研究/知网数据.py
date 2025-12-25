# -*- coding: utf-8 -*-
import time
import pandas as pd
import re
import sys
import io
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 设置标准输出编码为UTF-8，避免Windows下emoji字符编码错误
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

class CNKIDataScraper:
    def __init__(self):
        self.driver = None
        self.papers_data = []

    def setup_driver(self):
        """设置Chrome浏览器驱动"""
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
        """等待搜索结果加载"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            # 等待tbody加载
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
            # 等待至少有一个class="name"的元素（论文名）
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody .name")))
            return True
        except TimeoutException:
            print("等待结果超时")
            return False
        except Exception as e:
            print(f"等待结果失败: {e}")
            return False

    def extract_papers_from_page(self):
        """从当前页面提取论文信息"""
        papers = []
        
        try:
            # 查找tbody中的所有行
            tbody = self.driver.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            
            for row in rows:
                paper = self.extract_paper_from_row(row)
                if paper and paper['title']:
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"提取论文信息失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def extract_paper_from_row(self, row):
        """从表格行中提取论文信息"""
        paper = {
            'title': '',
            'authors': '',
            'journal': '',
            'publish_time': '',
            'link': ''
        }

        try:
            # 提取论文名和链接（class="name"的a标签）
            try:
                name_element = row.find_element(By.CSS_SELECTOR, ".name")
                # 查找name元素内的a标签
                link_element = name_element.find_element(By.TAG_NAME, "a")
                paper['title'] = link_element.text.strip()
                paper['link'] = link_element.get_attribute('href') or ''
            except NoSuchElementException:
                # 如果找不到，尝试其他方式
                try:
                    name_element = row.find_element(By.CSS_SELECTOR, ".name")
                    paper['title'] = name_element.text.strip()
                    # 尝试在name元素内查找链接
                    try:
                        link_element = name_element.find_element(By.TAG_NAME, "a")
                        paper['link'] = link_element.get_attribute('href') or ''
                    except:
                        pass
                except:
                    return None

            if not paper['title']:
                return None

            # 提取作者（class="author"）
            try:
                author_element = row.find_element(By.CSS_SELECTOR, ".author")
                paper['authors'] = author_element.text.strip()
            except NoSuchElementException:
                paper['authors'] = ''

            # 提取期刊名（class="source"）
            try:
                source_element = row.find_element(By.CSS_SELECTOR, ".source")
                paper['journal'] = source_element.text.strip()
            except NoSuchElementException:
                paper['journal'] = ''

            # 提取发表时间（class="date"）
            try:
                date_element = row.find_element(By.CSS_SELECTOR, ".date")
                date_text = date_element.text.strip()
                # 提取日期格式
                date_match = re.search(r'(19|20)\d{2}-\d{1,2}-\d{1,2}', date_text)
                if date_match:
                    paper['publish_time'] = date_match.group()
                else:
                    # 尝试提取年份
                    year_match = re.search(r'(19|20)\d{2}', date_text)
                    if year_match:
                        paper['publish_time'] = year_match.group()
                    else:
                        paper['publish_time'] = date_text
            except NoSuchElementException:
                paper['publish_time'] = ''

            # 清理数据
            for key in paper:
                if isinstance(paper[key], str):
                    paper[key] = re.sub(r'\s+', ' ', paper[key]).strip()

            return paper

        except Exception as e:
            # 如果提取失败，返回None
            return None

    def apply_date_filter(self, start_year, end_year):
        """在CNKI页面上应用日期筛选"""
        try:
            time.sleep(2)
            
            # 尝试通过左侧筛选栏设置发表时间
            try:
                time_filter_xpaths = [
                    "//div[contains(@class, 'filter')]//a[contains(text(), '发表时间')]",
                    "//div[contains(@class, 'filter')]//a[contains(text(), '时间范围')]",
                    "//span[contains(text(), '发表时间')]",
                    "//label[contains(text(), '发表时间')]"
                ]
                
                for xpath in time_filter_xpaths:
                    try:
                        time_filter = self.driver.find_element(By.XPATH, xpath)
                        if time_filter.is_displayed():
                            self.driver.execute_script("arguments[0].click();", time_filter)
                            time.sleep(1)
                            break
                    except:
                        continue
            except:
                pass
            
            # 尝试直接操作年份输入框
            try:
                start_inputs = [
                    "input[name*='start']",
                    "input[name*='begin']",
                    "input[id*='start']",
                    "input[id*='YearFrom']"
                ]
                
                for selector in start_inputs:
                    try:
                        start_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if start_input.is_displayed():
                            start_input.clear()
                            start_input.send_keys(str(start_year))
                            time.sleep(0.5)
                            break
                    except:
                        continue
                
                end_inputs = [
                    "input[name*='end']",
                    "input[name*='finish']",
                    "input[id*='end']",
                    "input[id*='YearTo']"
                ]
                
                for selector in end_inputs:
                    try:
                        end_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if end_input.is_displayed():
                            end_input.clear()
                            end_input.send_keys(str(end_year))
                            time.sleep(0.5)
                            break
                    except:
                        continue
                
                # 尝试点击"确定"或"检索"按钮
                confirm_xpaths = [
                    "//button[contains(text(), '确定')]",
                    "//button[contains(text(), '检索')]",
                    "//a[contains(text(), '检索')]"
                ]
                
                for xpath in confirm_xpaths:
                    try:
                        confirm_btn = self.driver.find_element(By.XPATH, xpath)
                        if confirm_btn.is_displayed():
                            self.driver.execute_script("arguments[0].click();", confirm_btn)
                            time.sleep(3)
                            break
                    except:
                        continue
                        
            except Exception as e:
                print(f"设置日期筛选时出错: {e}")
            
            return True
            
        except Exception as e:
            print(f"应用日期筛选失败: {e}")
            return False

    def filter_papers_by_year(self, papers, target_year):
        """过滤论文，只保留指定年份的论文"""
        filtered = []
        for paper in papers:
            publish_time = paper.get('publish_time', '')
            if not publish_time:
                continue
            
            year_match = re.search(r'(19|20)\d{2}', str(publish_time))
            if year_match:
                year = int(year_match.group())
                if year == target_year:
                    filtered.append(paper)
        
        return filtered

    def scrape_papers(self, url, max_pages=10, target_year=None):
        """抓取论文数据"""
        if not self.setup_driver():
            return []
        
        try:
            print(f"🌐 正在访问链接: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # 如果指定了目标年份，尝试在页面上设置时间筛选
            if target_year:
                print(f"📅 正在设置时间筛选：{target_year}年")
                self.apply_date_filter(target_year, target_year)
                time.sleep(3)
            
            all_papers = []
            
            for page in range(1, max_pages + 1):
                print(f"📄 正在抓取第 {page} 页...")
                
                if page > 1:
                    try:
                        # 查找下一页按钮
                        next_button = None
                        
                        # 方法1: 查找class="pagesnums"且文本为"下一页"
                        try:
                            next_button = self.driver.find_element(By.XPATH, "//a[@class='pagesnums' and text()='下一页']")
                        except:
                            pass
                        
                        # 方法2: 查找包含"下一"文本的链接
                        if not next_button:
                            try:
                                next_button = self.driver.find_element(By.XPATH, "//a[@class='pagesnums' and contains(text(), '下一')]")
                            except:
                                pass
                        
                        # 方法3: 查找所有pagesnums链接
                        if not next_button:
                            try:
                                pagesnums_links = self.driver.find_elements(By.CSS_SELECTOR, "a.pagesnums")
                                for link in pagesnums_links:
                                    if link.text.strip() == "下一页" or "下一" in link.text:
                                        next_button = link
                                        break
                            except:
                                pass
                        
                        if next_button:
                            if next_button.is_displayed():
                                self.driver.execute_script("arguments[0].click();", next_button)
                                print(f"📄 翻到第 {page} 页...")
                                time.sleep(3)
                            else:
                                print(f"⚠️ 下一页按钮不可见，停止翻页")
                                break
                        else:
                            print(f"⚠️ 未找到下一页按钮，可能已到最后一页")
                            break
                            
                    except Exception as e:
                        print(f"⚠️ 翻页失败: {e}")
                        break
                
                if self.wait_for_results():
                    papers = self.extract_papers_from_page()
                    if papers:
                        all_papers.extend(papers)
                        print(f"✅ 第 {page} 页提取到 {len(papers)} 篇论文")
                    else:
                        if page > 1:
                            break
                else:
                    break
                
                if page < max_pages:
                    time.sleep(2)
            
            # 如果指定了目标年份，再次过滤数据确保准确性
            if target_year:
                print(f"🔍 正在过滤数据，只保留{target_year}年的论文...")
                all_papers = self.filter_papers_by_year(all_papers, target_year)
                print(f"✅ 过滤后剩余 {len(all_papers)} 篇论文")
            
            self.papers_data = all_papers
            return all_papers
            
        except Exception as e:
            print(f"抓取过程失败: {e}")
            import traceback
            traceback.print_exc()
            return []
        
        finally:
            if self.driver:
                self.driver.quit()

    def save_to_excel(self, papers, filename=None):
        """保存数据到Excel文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"知网数据_{timestamp}.xlsx"
        
        if not papers:
            print("没有数据可保存")
            return False
        
        try:
            data = []
            for paper in papers:
                data.append({
                    '作者': paper.get('authors', ''),
                    '论文名': paper.get('title', ''),
                    '期刊名': paper.get('journal', ''),
                    '发表时间': paper.get('publish_time', ''),
                    '链接': paper.get('link', '')
                })
            
            df = pd.DataFrame(data)
            df.to_excel(filename, index=False, engine='openpyxl')
            print(f"✅ 数据已保存到: {filename}")
            return True
            
        except Exception as e:
            print(f"保存失败: {e}")
            return False


def main():
    """主函数"""
    print("🚀 开始运行知网数据抓取工具...")
    
    # 知网链接
    url = "https://kns.cnki.net/kns8s/defaultresult/index?crossids=YSTT4HG0%2CLSTPFY1C%2CJUP3MUPD%2CMPMFIG1A%2CWQ0UVIAA%2CBLZOG7CK%2CPWFIRAGL%2CEMRPGLPA%2CNLBO1Z6R%2CNN3FJMUV&korder=AF&kw=%E9%A6%96%E9%83%BD%E5%9B%BE%E4%B9%A6%E9%A6%86"
    
    # 获取去年的年份
    current_year = datetime.now().year
    last_year = current_year - 1
    print(f"📅 目标时间范围：{last_year}年（去年）")
    
    try:
        scraper = CNKIDataScraper()
        print(f"🔍 开始抓取{last_year}年的论文数据...")
        papers = scraper.scrape_papers(url, max_pages=10, target_year=last_year)
        
        if papers:
            print(f"✅ 成功抓取到 {len(papers)} 篇{last_year}年的论文")
            print("💾 正在保存到Excel文件...")
            scraper.save_to_excel(papers, filename=f"知网数据_{last_year}年.xlsx")
            print("🎉 抓取完成！")
        else:
            print(f"❌ 没有抓取到{last_year}年的数据")
    
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

