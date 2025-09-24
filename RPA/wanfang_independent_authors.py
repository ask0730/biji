#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
万方数据独立作者元素爬虫
专门处理每个作者都是独立span元素的情况
"""

import time
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class IndependentAuthorWanfangScraper:
    def __init__(self):
        self.driver = None
        self.papers_data = []

    def setup_driver(self):
        """设置浏览器驱动"""
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
            self.driver.implicitly_wait(5)
            return True
            
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            return False
    
    def wait_for_page_load(self, timeout=30):
        """等待页面加载完成"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            
            # 等待关键元素加载
            selectors = [
                ".title-area",  # 标题区域
                ".author-area",  # 作者区域
                ".right-content",  # 主要内容区域
                "body"  # 确保body加载
            ]
            
            for selector in selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"页面元素加载完成: {selector}")
                    break
                except TimeoutException:
                    continue
            
            # 额外等待确保动态内容加载
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"等待页面加载失败: {e}")
            return False
    
    def extract_authors_from_author_area(self, author_area):
        """从author-area中提取所有独立作者"""
        authors_list = []
        
        try:
            print("🔍 查找独立作者元素...")
            
            # 方法1: 查找所有 .authors 元素（每个作者一个独立的span）
            authors_elements = author_area.find_elements(By.CSS_SELECTOR, ".authors")
            
            if authors_elements:
                print(f"找到 {len(authors_elements)} 个独立的作者元素")
                for i, element in enumerate(authors_elements):
                    author_text = element.text.strip()
                    if author_text and len(author_text) >= 2:
                        # 过滤掉时间信息（包含年份的内容）
                        if re.search(r'(19|20)\d{2}.*期|年|月|日', author_text):
                            print(f"  跳过时间信息: {author_text}")
                            continue
                        
                        # 过滤掉明显不是作者名的内容
                        skip_keywords = ['期', '年', '月', '日', '卷', '页', '来源', '期刊', '发表']
                        if any(keyword in author_text for keyword in skip_keywords):
                            print(f"  跳过非作者内容: {author_text}")
                            continue
                        
                        authors_list.append(author_text)
                        print(f"  作者 {i+1}: {author_text}")
            
            # 方法2: 如果没找到独立的作者元素，尝试查找单个 .authors 元素
            if not authors_list:
                print("未找到独立作者元素，尝试查找单个作者元素...")
                try:
                    authors_element = author_area.find_element(By.CSS_SELECTOR, ".authors")
                    authors_text = authors_element.text.strip()
                    
                    if authors_text:
                        # 尝试用分隔符分割
                        authors_list = self.split_authors_text(authors_text)
                        print(f"从单个元素分割得到 {len(authors_list)} 个作者")
                        
                except NoSuchElementException:
                    print("未找到 .authors 元素")
            
            # 方法3: 尝试其他可能的选择器
            if not authors_list:
                print("尝试其他作者选择器...")
                alternative_selectors = [
                    ".author",
                    ".author-name", 
                    ".author-list",
                    "span[class*='author']",
                    "div[class*='author']",
                    ".author-info",
                    ".author-detail"
                ]
                
                for selector in alternative_selectors:
                    try:
                        elements = author_area.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            print(f"使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                            for element in elements:
                                author_text = element.text.strip()
                                if author_text and len(author_text) >= 2:
                                    authors_list.append(author_text)
                            if authors_list:
                                break
                    except Exception as e:
                        continue
            
            # 方法4: 如果还是没找到，尝试从整个author-area中提取
            if not authors_list:
                print("尝试从整个author-area文本中提取...")
                author_area_text = author_area.text.strip()
                print(f"author-area文本: {author_area_text[:100]}...")
                
                # 查找作者模式（中文姓名）
                author_patterns = [
                    r'作者[：:]\s*([^，,；;\n\r]+)',
                    r'著者[：:]\s*([^，,；;\n\r]+)',
                    r'作者\s+([^，,；;\n\r]+)',
                    r'著者\s+([^，,；;\n\r]+)'
                ]
                
                for pattern in author_patterns:
                    match = re.search(pattern, author_area_text)
                    if match:
                        authors_text = match.group(1).strip()
                        authors_list = self.split_authors_text(authors_text)
                        print(f"通过正则表达式找到 {len(authors_list)} 个作者")
                        break
            
            # 清理和格式化作者信息
            if authors_list:
                # 去重并过滤
                filtered_authors = []
                for author in authors_list:
                    author = author.strip()
                    if (len(author) >= 2 and len(author) <= 20 and 
                        not re.search(r'[\d\s\-_\.\(\)\[\]{}]', author) and
                        not any(keyword in author for keyword in ['作者', '著者', '来源', '期刊', '发表', '时间', '年份', '期', '卷', '页'])):
                        filtered_authors.append(author)
                
                authors_text = ';'.join(filtered_authors)
                print(f"✅ 最终提取到 {len(filtered_authors)} 个作者: {authors_text}")
                return authors_text
            else:
                print("❌ 未找到任何作者信息")
                return ""
                
        except Exception as e:
            print(f"提取作者信息时出错: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def split_authors_text(self, authors_text):
        """分割作者文本"""
        if not authors_text:
            return []
        
        # 尝试不同的分隔符
        separators = ['；', '，', ';', ',', ' ']
        
        for separator in separators:
            if separator in authors_text:
                authors_list = [author.strip() for author in authors_text.split(separator) if author.strip()]
                if len(authors_list) > 1:
                    return authors_list
        
        # 如果没有分隔符，返回单个作者
        return [authors_text.strip()]
    
    def find_all_paper_elements(self):
        """查找所有论文元素"""
        print("🔍 查找所有论文元素...")
        
        # 尝试多种选择器来找到所有论文
        selectors_to_try = [
            ".title-area",  # 主要选择器
            ".right-content .title-area",  # 在right-content中
            "[class*='title-area']"  # 包含title-area的类
        ]
        
        all_title_areas = []
        for selector in selectors_to_try:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
                    all_title_areas.extend(elements)
                else:
                    print(f"选择器 '{selector}' 未找到元素")
            except Exception as e:
                print(f"选择器 '{selector}' 出错: {e}")
        
        # 去重
        unique_elements = []
        seen_elements = set()
        for element in all_title_areas:
            try:
                element_id = element.get_attribute('outerHTML')
                if element_id not in seen_elements:
                    seen_elements.add(element_id)
                    unique_elements.append(element)
            except:
                continue
        
        print(f"去重后找到 {len(unique_elements)} 个唯一的 title-area")
        return unique_elements
    
    def extract_paper_from_elements(self, title_area, author_area=None):
        """从元素中提取论文信息"""
        paper = {
            'title': '',
            'authors': '',
            'authors_count': 0,
            'first_author': '',
            'all_authors': [],
            'journal': '',
            'publish_time': '',
            'link': ''
        }
        
        try:
            # 提取标题
            try:
                title_element = title_area.find_element(By.CSS_SELECTOR, ".title")
                paper['title'] = title_element.text.strip()
                
                # 获取标题链接
                try:
                    title_link = title_element.find_element(By.TAG_NAME, "a")
                    if title_link:
                        paper['link'] = title_link.get_attribute('href')
                except NoSuchElementException:
                    pass
                    
            except NoSuchElementException:
                print("未找到 .title")
                return None
            
            # 如果没有提供author_area，尝试查找
            if not author_area:
                author_area = self.find_author_area_for_title(title_area)
            
            if author_area:
                # 使用专门的作者提取器
                authors_text = self.extract_authors_from_author_area(author_area)
                paper['authors'] = authors_text
                
                if authors_text:
                    authors_list = authors_text.split(';')
                    paper['authors_count'] = len(authors_list)
                    paper['first_author'] = authors_list[0] if authors_list else ''
                    paper['all_authors'] = authors_list
                else:
                    paper['authors_count'] = 0
                    paper['first_author'] = ''
                    paper['all_authors'] = []
                
                # 提取期刊名
                try:
                    journal_element = author_area.find_element(By.CSS_SELECTOR, ".periodical-title")
                    paper['journal'] = journal_element.text.strip()
                except NoSuchElementException:
                    print("未找到 .periodical-title")
                
                # 提取时间 - 从所有 .authors 元素中查找时间信息
                try:
                    # 查找所有 .authors 元素
                    all_authors_elements = author_area.find_elements(By.CSS_SELECTOR, ".authors")
                    
                    for element in all_authors_elements:
                        time_text = element.text.strip()
                        
                        # 检查是否包含时间信息
                        if re.search(r'(19|20)\d{2}.*期|年|月|日', time_text):
                            # 从时间文本中提取年份
                            date_patterns = [
                                r'(19|20)\d{2}[-年]\d{1,2}[-月]\d{1,2}[日]?',
                                r'(19|20)\d{2}年\d{1,2}期',
                                r'(19|20)\d{2}年\d{1,2}月',
                                r'(19|20)\d{2}年',
                                r'(19|20)\d{2}'
                            ]
                            
                            for pattern in date_patterns:
                                match = re.search(pattern, time_text)
                                if match:
                                    paper['publish_time'] = match.group()
                                    print(f"找到时间: {paper['publish_time']}")
                                    break
                            
                            if paper['publish_time']:
                                break
                    
                    if not paper['publish_time']:
                        print("未找到时间信息")
                            
                except Exception as e:
                    print(f"提取时间信息时出错: {e}")
            
            # 清理数据
            for key in paper:
                if isinstance(paper[key], str):
                    paper[key] = re.sub(r'\s+', ' ', paper[key]).strip()
            
            return paper if paper['title'] else None
            
        except Exception as e:
            print(f"提取论文信息时出错: {e}")
            return None
    
    def find_author_area_for_title(self, title_area):
        """为title-area查找对应的author-area"""
        try:
            # 方法1: 查找父元素的兄弟元素
            parent = title_area.find_element(By.XPATH, "..")
            author_area = parent.find_element(By.CSS_SELECTOR, ".author-area")
            return author_area
        except NoSuchElementException:
            try:
                # 方法2: 查找下一个兄弟元素
                author_area = title_area.find_element(By.XPATH, "following-sibling::*[contains(@class, 'author-area')]")
                return author_area
            except NoSuchElementException:
                try:
                    # 方法3: 查找包含 title-area 的父元素，然后查找 author-area
                    container = title_area.find_element(By.XPATH, "ancestor::*[contains(@class, 'item') or contains(@class, 'result') or contains(@class, 'paper')]")
                    author_area = container.find_element(By.CSS_SELECTOR, ".author-area")
                    return author_area
                except NoSuchElementException:
                    return None
    
    def extract_all_papers(self):
        """提取所有论文"""
        papers = []
        
        try:
            print("🔍 开始提取所有论文...")
            
            # 查找所有title-area
            title_areas = self.find_all_paper_elements()
            
            if not title_areas:
                print("❌ 未找到任何 title-area")
                return []
            
            # 同时查找所有author-area
            author_areas = self.driver.find_elements(By.CSS_SELECTOR, ".author-area")
            print(f"找到 {len(author_areas)} 个 author-area")
            
            # 提取每篇论文
            for i, title_area in enumerate(title_areas):
                try:
                    print(f"\n{'='*50}")
                    print(f"处理论文 {i+1}/{len(title_areas)}")
                    
                    # 尝试找到对应的author-area
                    author_area = None
                    
                    # 如果author-area数量与title-area相同，按索引匹配
                    if len(author_areas) == len(title_areas):
                        author_area = author_areas[i]
                        print(f"通过索引匹配找到 author-area {i+1}")
                    else:
                        # 否则尝试其他方法
                        author_area = self.find_author_area_for_title(title_area)
                        if author_area:
                            print("通过DOM关系找到 author-area")
                    
                    # 提取论文信息
                    paper = self.extract_paper_from_elements(title_area, author_area)
                    
                    if paper and paper['title']:
                        papers.append(paper)
                        print(f"✅ 成功提取论文 {len(papers)}: {paper['title'][:50]}...")
                        print(f"   作者: {paper['authors']} (共{paper['authors_count']}人)")
                        print(f"   期刊: {paper['journal']}")
                        print(f"   时间: {paper['publish_time']}")
                    else:
                        print(f"❌ 论文 {i+1} 提取失败")
                    
                    # 限制处理数量
                    if len(papers) >= 20:
                        print("达到提取数量限制，停止提取")
                        break
                        
                except Exception as e:
                    print(f"处理论文 {i+1} 时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\n🎉 总共成功提取 {len(papers)} 篇论文")
            
            # 统计作者信息
            total_authors = sum(paper['authors_count'] for paper in papers)
            multi_author_papers = sum(1 for paper in papers if paper['authors_count'] > 1)
            
            print(f"📊 统计信息:")
            print(f"   总论文数: {len(papers)}")
            print(f"   总作者数: {total_authors}")
            print(f"   多作者论文: {multi_author_papers} 篇")
            print(f"   单作者论文: {len(papers) - multi_author_papers} 篇")
            
            return papers
            
        except Exception as e:
            print(f"提取所有论文失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_first_page(self, url):
        """抓取第一页论文数据"""
        if not self.setup_driver():
            return []
        
        try:
            print(f"正在访问: {url}")
            self.driver.get(url)
            
            if not self.wait_for_page_load():
                print("页面加载失败")
                return []
            
            # 提取所有论文
            papers = self.extract_all_papers()
            
            self.papers_data = papers
            return papers
            
        except Exception as e:
            print(f"抓取过程失败: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_to_excel(self, papers, filename=None):
        """保存数据到Excel文件"""
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"万方数据论文_独立作者_{timestamp}.xlsx"
        
        if not papers:
            print("没有数据可保存")
            return False
        
        try:
            data = []
            for paper in papers:
                data.append({
                    '作者(arrayAuthor)': paper.get('authors', ''),
                    '作者数量': paper.get('authors_count', 0),
                    '第一作者': paper.get('first_author', ''),
                    '所有作者': ';'.join(paper.get('all_authors', [])),
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
    print("🚀 万方数据独立作者元素爬虫")
    print("=" * 50)
    print("专门处理每个作者都是独立span元素的情况")
    print("结构: <span class='authors'>张靖</span>")
    print("      <span class='authors'>陆思晓</span>")
    print("      <span class='authors'>方家忠</span>")
    print("=" * 50)
    
    url = "https://s.wanfangdata.com.cn/paper?q=%E4%BD%9C%E8%80%85%E5%8D%95%E4%BD%8D%3A%E9%A6%96%E9%83%BD%E5%9B%BE%E4%B9%A6%E9%A6%86&p=1"

    try:
        print("📱 正在启动浏览器...")
        scraper = IndependentAuthorWanfangScraper()
        print("🔍 开始抓取论文数据...")
        papers = scraper.scrape_first_page(url)

        if papers:
            print(f"✅ 成功抓取到 {len(papers)} 篇论文")
            
            # 显示论文信息
            print("\n📋 抓取到的论文:")
            for i, paper in enumerate(papers, 1):
                print(f"\n第 {i} 篇:")
                print(f"标题: {paper.get('title', 'N/A')}")
                print(f"作者: {paper.get('authors', 'N/A')} (共{paper.get('authors_count', 0)}人)")
                print(f"第一作者: {paper.get('first_author', 'N/A')}")
                print(f"期刊: {paper.get('journal', 'N/A')}")
                print(f"时间: {paper.get('publish_time', 'N/A')}")
                print(f"链接: {paper.get('link', 'N/A')[:50]}...")
            
            print("\n💾 正在保存数据...")
            scraper.save_to_excel(papers)
            print("🎉 抓取完成！")
        else:
            print("❌ 没有抓取到数据")

    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
