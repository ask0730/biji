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

    def is_valid_journal_name(self, journal_name):
        """验证期刊名是否有效"""
        if not journal_name or len(journal_name) < 2:
            return False

        # 排除明显错误的期刊名
        invalid_patterns = [
            'HTML', 'CSS', 'JavaScript', 'PDF', 'DOC', 'DOCX', 'XLS', 'XLSX',
            'http', 'www', '.com', '.cn', '.org', '.net',
            '下载', '查看', '详情', '全文', '摘要', '链接', '点击',
            '作者', '发表', '出版', '编辑', '审稿',
            '第一页', '第二页', '上一页', '下一页',
            '搜索', '检索', '筛选', '排序',
            '首都图书馆', '公共图书馆', '服务', '管理', '工作', '分析', '探讨', '应用', '实践', '探索',
            '挑战', '对策', '背景', '融合', '技术', '传承', '智慧', '旅游'
        ]

        # 检查是否包含无效模式
        for pattern in invalid_patterns:
            if pattern.lower() in journal_name.lower():
                return False

        # 期刊名不应该全是数字或特殊字符
        if re.match(r'^[\d\s\-_\.]+$', journal_name):
            return False

        # 期刊名应该包含中文字符
        if not re.search(r'[\u4e00-\u9fa5]', journal_name):
            return False

        # 期刊名长度应该合理（根据图片中的期刊名，通常2-10个字符）
        if len(journal_name) > 15 or len(journal_name) < 2:
            return False

        # 期刊名不应该包含标点符号（除了常见的期刊符号）
        if re.search(r'[，。！？；：""''（）【】\(\)]+', journal_name):
            return False

        # 检查是否符合期刊名的常见模式
        valid_patterns = [
            r'.*阅读.*', r'.*学刊.*', r'.*学报.*', r'.*研究.*', r'.*杂志.*',
            r'.*期刊.*', r'.*通讯.*', r'.*文摘.*', r'.*评论.*', r'.*年鉴.*',
            r'.*参考.*', r'.*新书.*', r'.*文化.*', r'.*产业.*', r'.*管理.*',
            r'.*科技.*', r'.*学术.*', r'.*教育.*', r'.*信息.*'
        ]

        # 如果包含期刊关键词，更可能是有效期刊名
        for pattern in valid_patterns:
            if re.match(pattern, journal_name):
                return True

        # 对于简短的中文词汇（如"参考"、"年鉴编"），也可能是期刊名
        if len(journal_name) <= 6 and re.match(r'^[\u4e00-\u9fa5]+$', journal_name):
            return True

        return False
        
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

                            # 优先匹配完整日期格式 YYYY-MM-DD
                            date_match = re.search(r'(19|20)\d{2}-\d{1,2}-\d{1,2}', parent_text)
                            if date_match:
                                paper['publish_time'] = date_match.group()
                            else:
                                # 匹配年份
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
            # 提取标题和链接
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

            # 获取所有单元格
            cells = row.find_elements(By.TAG_NAME, "td")
            row_text = row.text

            # 分析整行文本，用于更好的字段识别
            row_text = row.text.strip()

            # 更精确的字段提取 - 基于CNKI实际页面结构
            for i, cell in enumerate(cells):
                cell_text = cell.text.strip()
                if not cell_text:
                    continue

                # 提取作者 - CNKI中作者通常在特定位置
                if not paper['authors']:
                    # 方法1: 查找明确标注作者的单元格
                    if '作者' in cell_text and ('作者:' in cell_text or '作者：' in cell_text):
                        authors = cell_text.replace('作者:', '').replace('作者：', '').strip()
                        if authors and not re.search(r'\d{4}', authors) and len(authors) < 100:
                            paper['authors'] = authors
                    # 方法2: 查找作者模式（排除标题）
                    elif (i >= 1 and cell_text != paper['title'] and  # 不是标题
                          not re.search(r'\d{4}', cell_text) and
                          not any(keyword in cell_text for keyword in ['来源', '期刊', '发表', '出版', '年', '月', '日', '学报', '研究', '杂志', '技术', '管理', '教育', '文化', '社会', '经济', '法学', '医学', '工程', '信息', '现代', '当代', '中国', '国际', '大学', '学院']) and
                          len(cell_text) < 80 and len(cell_text) > 1 and  # 合理的作者名长度
                          re.search(r'[\u4e00-\u9fa5]', cell_text)):  # 包含中文字符
                        # 进一步验证是否像作者名（通常较短，可能有分号）
                        if (';' in cell_text or '；' in cell_text or  # 多作者分隔符
                            (len(cell_text) >= 2 and len(cell_text) <= 30 and
                             not any(char in cell_text for char in ['（', '）', '(', ')', '【', '】', '[', ']']))):  # 不包含括号等
                            paper['authors'] = cell_text

                # 提取期刊名（来源）- CNKI中期刊信息的识别
                if not paper['journal']:
                    # 方法1: 查找明确标注来源的单元格
                    if '来源' in cell_text:
                        # 更精确的来源提取
                        if '来源:' in cell_text or '来源：' in cell_text:
                            # 提取来源后面的内容
                            journal_match = re.search(r'来源[：:]\s*([^，,；;\s]+)', cell_text)
                            if journal_match:
                                journal = journal_match.group(1).strip()
                            else:
                                journal = cell_text.replace('来源:', '').replace('来源：', '').strip()
                        else:
                            # 如果只是包含"来源"但没有冒号，可能是期刊名的一部分
                            journal = cell_text.strip()

                        # 移除日期部分
                        journal = re.sub(r'\s*(19|20)\d{2}[-年]\d{1,2}[-月]\d{1,2}[日]?.*', '', journal)
                        journal = re.sub(r'\s*(19|20)\d{2}.*', '', journal).strip()

                        # 验证期刊名的有效性
                        if journal and len(journal) > 1 and self.is_valid_journal_name(journal):
                            paper['journal'] = journal

                    # 方法2: 查找期刊模式 - 基于图片中的期刊名特征
                    elif (cell_text != paper['title'] and  # 不是标题
                          cell_text != paper['authors'] and  # 不是作者
                          not re.search(r'\d{4}', cell_text) and  # 不包含年份
                          len(cell_text) <= 15 and len(cell_text) >= 2 and  # 长度合理
                          re.search(r'[\u4e00-\u9fa5]', cell_text) and  # 包含中文
                          self.is_valid_journal_name(cell_text)):
                        paper['journal'] = cell_text

                    # 方法3: 位置推断（通常期刊名在第2-4列）
                    elif (i >= 1 and i <= 4 and not paper['journal'] and
                          cell_text != paper['title'] and  # 不是标题
                          cell_text != paper['authors'] and  # 不是作者
                          not re.search(r'\d{4}', cell_text) and
                          len(cell_text) <= 12 and len(cell_text) >= 2 and  # 期刊名通常较短
                          re.match(r'^[\u4e00-\u9fa5]+$', cell_text) and  # 纯中文
                          self.is_valid_journal_name(cell_text)):
                        paper['journal'] = cell_text

                # 提取发表时间 - 查找日期格式
                if not paper['publish_time'] and re.search(r'(19|20)\d{2}', cell_text):
                    # 优先匹配完整日期格式 YYYY-MM-DD
                    date_match = re.search(r'(19|20)\d{2}-\d{1,2}-\d{1,2}', cell_text)
                    if date_match:
                        paper['publish_time'] = date_match.group()
                    else:
                        # 匹配年份
                        year_match = re.search(r'(19|20)\d{2}', cell_text)
                        if year_match:
                            paper['publish_time'] = year_match.group()

            # 如果还没有找到发表时间，从整行文本中提取
            if not paper['publish_time']:
                # 优先匹配完整日期格式
                date_match = re.search(r'(19|20)\d{2}-\d{1,2}-\d{1,2}', row_text)
                if date_match:
                    paper['publish_time'] = date_match.group()
                else:
                    # 匹配年份
                    year_match = re.search(r'(19|20)\d{2}', row_text)
                    if year_match:
                        paper['publish_time'] = year_match.group()

            # 如果还没有找到期刊名，尝试从整行文本中提取
            if not paper['journal'] or paper['journal'] == '期刊':
                # 方法1: 从整行文本中查找"来源:"模式
                source_match = re.search(r'来源[：:]\s*([^，,；;\s\d]+)', row_text)
                if source_match:
                    journal_candidate = source_match.group(1).strip()
                    if self.is_valid_journal_name(journal_candidate):
                        paper['journal'] = journal_candidate

                # 方法2: 如果还没找到，查找期刊关键词
                if not paper['journal'] or paper['journal'] == '期刊':
                    row_parts = row_text.split()
                    for part in row_parts:
                        if (part != paper['title'] and part != paper['authors'] and
                            len(part) > 3 and len(part) < 30 and
                            not re.search(r'\d{4}', part) and
                            re.search(r'[\u4e00-\u9fa5]', part) and
                            any(keyword in part for keyword in ['学报', '研究', '杂志', '期刊', '学刊', '通讯', '文摘', '评论', '学术', '科学', '技术', '管理', '教育', '文化', '社会', '经济', '法学', '医学', '工程', '信息', '现代', '当代', '中国', '国际', '大学', '学院', '图书', '阅读', '知识', '智慧', '数字', '网络']) and
                            self.is_valid_journal_name(part)):
                            paper['journal'] = part
                            break

                # 方法3: 最后尝试更宽松的匹配
                if not paper['journal'] or paper['journal'] == '期刊':
                    # 查找可能的期刊名模式（中文词汇，不包含常见动词）
                    journal_candidates = re.findall(r'[\u4e00-\u9fa5]{2,15}', row_text)
                    for candidate in journal_candidates:
                        if (candidate != paper['title'] and candidate != paper['authors'] and
                            candidate not in ['首都图书馆', '公共图书馆', '图书馆', '这个', '那个', '可以', '应该', '需要', '进行', '实现', '提高', '发展', '建设', '完善', '加强', '服务', '管理', '工作', '研究', '分析', '探讨', '应用', '实践', '探索'] and
                            self.is_valid_journal_name(candidate)):
                            paper['journal'] = candidate
                            break

            # 清理数据
            for key in paper:
                if isinstance(paper[key], str):
                    paper[key] = re.sub(r'\s+', ' ', paper[key]).strip()

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
    
    def save_to_excel(self, papers, filename=None):
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"首都图书馆相关论文_{timestamp}.xlsx"
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
    print("🚀 开始运行CNKI论文抓取工具...")
    url = "https://kns.cnki.net/kns8s/defaultresult/index?crossids=YSTT4HG0%2CLSTPFY1C%2CJUP3MUPD%2CMPMFIG1A%2CWQ0UVIAA%2CBLZOG7CK%2CPWFIRAGL%2CEMRPGLPA%2CNLBO1Z6R%2CNN3FJMUV&korder=AF&kw=%E9%A6%96%E9%83%BD%E5%9B%BE%E4%B9%A6%E9%A6%86"

    try:
        print("📱 正在启动浏览器...")
        scraper = CNKISeleniumScraper()
        print("🔍 开始抓取论文数据...")
        papers = scraper.scrape_papers(url, max_pages=1)

        if papers:
            print(f"✅ 成功抓取到 {len(papers)} 篇论文")
            print("💾 正在保存到Excel文件...")
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
