import time
import pandas as pd
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WanfangDataScraper:
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
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            return True
            
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            return False

    def wait_for_results(self, timeout=30):
        """等待搜索结果加载"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            # 等待万方数据的关键元素加载
            selectors = [
                ".title-area",
                ".right-content",
                ".result-item",
                "[class*='result']",
                "[class*='paper']"
            ]
            
            for selector in selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"页面元素加载完成: {selector}")
                    break
                except TimeoutException:
                    continue
            
            time.sleep(3)  # 额外等待动态内容加载
            return True
            
        except Exception as e:
            print(f"等待结果失败: {e}")
            return False

    def extract_paper_from_element(self, element):
        """从列表页元素中点击标题进入详情页并提取论文信息"""
        list_page_url = None
        try:
            # 保存当前URL，用于返回列表页
            list_page_url = self.driver.current_url
            
            # 查找并点击 .title-area 下的 .title 元素
            try:
                title_element = element.find_element(By.CSS_SELECTOR, "span.title, .title")
                
                # 滚动到元素可见
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", title_element)
                time.sleep(0.5)
                
                # 点击标题进入详情页
                # 在点击前保存列表页URL，用于返回
                list_page_url = self.driver.current_url
                
                try:
                    # 尝试直接点击
                    title_element.click()
                except:
                    # 如果直接点击失败，使用JavaScript点击
                    self.driver.execute_script("arguments[0].click();", title_element)
                
                # 等待页面跳转到详情页
                # 等待足够的时间让页面跳转和内容加载
                print("  等待页面跳转...")
                time.sleep(5)  # 等待页面跳转
                
                # 检查URL是否改变（用于提示，但不影响后续操作）
                current_url = self.driver.current_url
                if current_url != list_page_url:
                    print(f"  已跳转到详情页")
                else:
                    print(f"  继续等待页面加载...")
                    time.sleep(3)  # 再等待一下
                
                # 无论URL是否检测到变化，都继续尝试提取（因为点击后应该已经跳转了）
                
                # 从详情页提取信息
                paper = self.extract_paper_from_detail_page()
                
                # 返回列表页
                if list_page_url:
                    self.driver.get(list_page_url)
                    time.sleep(2)
                    
                    # 等待列表页重新加载
                    try:
                        wait = WebDriverWait(self.driver, 10)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".title-area")))
                    except TimeoutException:
                        pass
                
                return paper
                
            except NoSuchElementException:
                print("  未找到标题元素")
                return None
                
        except Exception as e:
            print(f"  点击标题进入详情页时出错: {e}")
            # 尝试返回列表页
            try:
                if list_page_url:
                    self.driver.get(list_page_url)
                    time.sleep(2)
            except:
                pass
            return None

    def extract_papers_from_page(self):
        """从当前页面提取论文信息"""
        papers = []
        
        try:
            # 查找所有论文项
            # 万方数据可能使用多种结构，尝试不同的选择器
            paper_elements = []
            
            # 方法1: 查找 .title-area
            try:
                title_areas = self.driver.find_elements(By.CSS_SELECTOR, ".title-area")
                if title_areas:
                    paper_elements = title_areas
                    print(f"找到 {len(paper_elements)} 个 .title-area 元素")
            except:
                pass
            
            # 方法2: 如果没找到，尝试其他选择器
            if not paper_elements:
                try:
                    result_items = self.driver.find_elements(By.CSS_SELECTOR, ".result-item, [class*='result-item'], [class*='paper-item']")
                    if result_items:
                        paper_elements = result_items
                        print(f"找到 {len(paper_elements)} 个结果项")
                except:
                    pass
            
            # 方法3: 查找包含标题的容器
            if not paper_elements:
                try:
                    # 查找所有包含链接的容器
                    containers = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='item'], div[class*='result'], div[class*='paper']")
                    paper_elements = [c for c in containers if c.find_elements(By.CSS_SELECTOR, ".title, a[href*='detail'], a[href*='paper']")]
                    print(f"找到 {len(paper_elements)} 个可能的论文容器")
                except:
                    pass
            
            # 保存列表页URL
            list_page_url = self.driver.current_url
            
            # 提取每篇论文
            total_count = len(paper_elements)
            for i in range(total_count):
                try:
                    print(f"正在处理第 {i+1}/{total_count} 篇论文...")
                    
                    # 每次循环前重新获取元素（因为页面可能被重新加载）
                    try:
                        current_elements = self.driver.find_elements(By.CSS_SELECTOR, ".title-area")
                        if not current_elements:
                            # 如果找不到，尝试其他选择器
                            current_elements = self.driver.find_elements(By.CSS_SELECTOR, ".result-item, [class*='result-item'], [class*='paper-item']")
                        
                        if i < len(current_elements):
                            element = current_elements[i]
                        else:
                            print(f"  第 {i+1} 个元素不存在，跳过")
                            continue
                    except Exception as e:
                        print(f"  重新获取元素失败: {e}")
                        # 尝试重新加载列表页
                        try:
                            self.driver.get(list_page_url)
                            time.sleep(3)
                            current_elements = self.driver.find_elements(By.CSS_SELECTOR, ".title-area")
                            if i < len(current_elements):
                                element = current_elements[i]
                            else:
                                continue
                        except:
                            continue
                    
                    # 提取论文信息
                    paper = self.extract_paper_from_element(element)
                    if paper and paper['title']:
                        papers.append(paper)
                        print(f"✅ 第 {i+1} 篇论文提取成功: {paper['title'][:50]}...")
                    else:
                        print(f"⚠️ 第 {i+1} 篇论文提取失败")
                        
                except Exception as e:
                    print(f"提取第 {i+1} 篇论文时出错: {e}")
                    # 确保返回列表页
                    try:
                        if self.driver.current_url != list_page_url:
                            self.driver.get(list_page_url)
                            time.sleep(2)
                    except:
                        pass
                    continue
            
            return papers
            
        except Exception as e:
            print(f"提取论文信息失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def extract_paper_from_detail_page(self):
        """从详情页提取论文信息"""
        paper = {
            'title': '',
            'authors': '',
            'journal': '',
            'publish_time': '',
            'link': ''
        }

        try:
            # 提取论文名（span.detailTitleCN）
            try:
                title_element = self.driver.find_element(By.CSS_SELECTOR, "span.detailTitleCN")
                paper['title'] = title_element.text.strip()
            except NoSuchElementException:
                print("  未找到论文名")
                return None

            # 提取链接（当前URL）
            paper['link'] = self.driver.current_url

            # 提取作者（div.author.detailTitle 下的 a 标签的 span 里）
            try:
                author_div = self.driver.find_element(By.CSS_SELECTOR, "div.author.detailTitle")
                author_links = author_div.find_elements(By.TAG_NAME, "a")
                
                authors_list = []
                for author_link in author_links:
                    try:
                        # 查找 a 标签内的 span
                        author_span = author_link.find_element(By.TAG_NAME, "span")
                        author_name = author_span.text.strip()
                        if author_name:
                            authors_list.append(author_name)
                    except NoSuchElementException:
                        # 如果没有span，直接取a标签的文本
                        author_name = author_link.text.strip()
                        if author_name:
                            authors_list.append(author_name)
                
                paper['authors'] = ';'.join(authors_list)
            except NoSuchElementException:
                print("  未找到作者信息")
                paper['authors'] = ''

            # 提取期刊名（class="periodicalName" 的 a 标签里）
            try:
                journal_element = self.driver.find_element(By.CSS_SELECTOR, "a.periodicalName, .periodicalName a")
                paper['journal'] = journal_element.text.strip()
            except NoSuchElementException:
                # 尝试其他可能的选择器
                try:
                    journal_element = self.driver.find_element(By.CSS_SELECTOR, "[class*='periodicalName'] a")
                    paper['journal'] = journal_element.text.strip()
                except:
                    print("  未找到期刊名")
                    paper['journal'] = ''

            # 提取发表时间（class="publish list" 下的 class="itemUrl"）
            try:
                publish_list = self.driver.find_element(By.CSS_SELECTOR, ".publish.list")
                item_url = publish_list.find_element(By.CSS_SELECTOR, ".itemUrl")
                paper['publish_time'] = item_url.text.strip()
            except NoSuchElementException:
                # 尝试其他可能的选择器
                try:
                    publish_list = self.driver.find_element(By.CSS_SELECTOR, "[class*='publish'][class*='list']")
                    item_url = publish_list.find_element(By.CSS_SELECTOR, "[class*='itemUrl']")
                    paper['publish_time'] = item_url.text.strip()
                except:
                    print("  未找到发表时间")
                    paper['publish_time'] = ''

            # 清理数据
            for key in paper:
                if isinstance(paper[key], str):
                    paper[key] = re.sub(r'\s+', ' ', paper[key]).strip()

            return paper

        except Exception as e:
            print(f"  提取详情页信息时出错: {e}")
            return None

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

    def scrape_papers(self, url, max_pages=1, target_year=None):
        """抓取论文数据"""
        if not self.setup_driver():
            return []
        
        try:
            print(f"🌐 正在访问链接: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            print(f"📄 正在抓取数据...")
            
            all_papers = []
            if self.wait_for_results():
                papers = self.extract_papers_from_page()
                if papers:
                    all_papers = papers
                    print(f"✅ 提取到 {len(papers)} 篇论文")
            
            # 如果指定了目标年份，过滤数据
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
            filename = f"万方数据_{timestamp}.xlsx"
        
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


def build_url_with_year(base_url, year):
    """构建包含指定年份的URL"""
    # 将URL中的Date:2024-2024或Date%3A2024-2024替换为指定年份
    # 注意：URL中可能使用URL编码，%3A是冒号的编码
    new_url = base_url
    
    # 处理URL编码的情况：Date%3A2024-2024
    if 'Date%3A' in new_url:
        new_url = re.sub(r'Date%3A\d{4}-\d{4}', f'Date%3A{year}-{year}', new_url)
    # 处理未编码的情况：Date:2024-2024
    elif 'Date:' in new_url:
        new_url = re.sub(r'Date:\d{4}-\d{4}', f'Date:{year}-{year}', new_url)
    else:
        # 如果没有Date参数，添加它（使用URL编码格式）
        if '?' in new_url:
            new_url = f"{new_url}&Date%3A{year}-{year}"
        else:
            new_url = f"{new_url}?Date%3A{year}-{year}"
    
    return new_url


def main():
    """主函数"""
    print("🚀 开始运行万方数据抓取工具...")
    
    # 万方数据链接
    base_url = "https://s.wanfangdata.com.cn/paper?q=%28%E4%BD%9C%E8%80%85%E5%8D%95%E4%BD%8D%3A%E9%A6%96%E9%83%BD%E5%9B%BE%E4%B9%A6%E9%A6%86%29%20Date%3A2022-2022&p=1&s=100"
    
    # 获取去年的年份
    current_year = datetime.now().year
    last_year = current_year - 1
    print(f"📅 目标时间范围：{last_year}年（去年）")
    
    # 构建包含去年年份的URL
    url = build_url_with_year(base_url, last_year)
    print(f"🔗 目标URL: {url}")
    
    try:
        scraper = WanfangDataScraper()
        print(f"🔍 开始抓取{last_year}年的论文数据...")
        papers = scraper.scrape_papers(url, max_pages=10, target_year=last_year)
        
        if papers:
            print(f"✅ 成功抓取到 {len(papers)} 篇{last_year}年的论文")
            print("💾 正在保存到Excel文件...")
            scraper.save_to_excel(papers, filename=f"万方数据_{last_year}年.xlsx")
            print("🎉 抓取完成！")
        else:
            print(f"❌ 没有抓取到{last_year}年的数据")
    
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

