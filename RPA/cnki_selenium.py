#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CNKI论文信息抓取工具 - Selenium版本
抓取首都图书馆相关论文信息（仅第一页）
"""

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

class CNKISeleniumScraper:
    def __init__(self):
        self.driver = None
        self.papers_data = []
        
    def setup_driver(self):
        """设置Chrome浏览器"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            # 不使用无头模式，这样可以看到浏览器操作
            # chrome_options.add_argument('--headless')
            
            # 设置用户代理
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            
            print("✅ Chrome浏览器启动成功")
            return True
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            print("💡 请确保已安装Chrome浏览器和ChromeDriver")
            return False
    
    def wait_for_results(self, timeout=30):
        """等待搜索结果加载"""
        try:
            print("⏳ 等待搜索结果加载...")
            
            # 等待结果容器出现
            wait = WebDriverWait(self.driver, timeout)
            
            # 尝试多个可能的选择器
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
                    element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    print(f"✅ 找到结果容器: {selector}")
                    return True
                except TimeoutException:
                    continue
            
            print("⚠️ 未找到标准结果容器，尝试查找其他元素...")
            
            # 等待页面完全加载
            time.sleep(5)
            
            # 检查是否有任何表格或列表
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            if tables:
                print(f"✅ 找到 {len(tables)} 个表格")
                return True
            
            # 检查是否有链接
            links = self.driver.find_elements(By.TAG_NAME, "a")
            paper_links = [link for link in links if link.text and len(link.text) > 10]
            if paper_links:
                print(f"✅ 找到 {len(paper_links)} 个可能的论文链接")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 等待结果失败: {e}")
            return False
    
    def extract_papers_from_page(self):
        """从当前页面提取论文信息"""
        papers = []
        
        try:
            # 方法1: 尝试从表格中提取
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    paper = self.extract_paper_from_row(row)
                    if paper and paper['title']:
                        papers.append(paper)
            
            # 方法2: 如果表格方法没有结果，尝试查找所有链接
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
                            
                            # 尝试从父元素获取更多信息
                            parent = link.find_element(By.XPATH, "..")
                            parent_text = parent.text
                            
                            # 提取年份
                            year_match = re.search(r'(19|20)\d{2}', parent_text)
                            if year_match:
                                paper['publish_time'] = year_match.group()
                            
                            papers.append(paper)
                            
                    except Exception:
                        continue
            
            print(f"📄 当前页面提取到 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            print(f"❌ 提取论文信息失败: {e}")
            return []
    
    def extract_paper_from_row(self, row):
        """从表格行提取论文信息"""
        paper = {
            'title': '',
            'authors': '',
            'journal': '',
            'publish_time': '',
            'link': ''
        }
        
        try:
            # 查找标题链接
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
            
            # 获取行的所有单元格
            cells = row.find_elements(By.TAG_NAME, "td")
            row_text = row.text
            
            # 尝试提取作者、期刊、时间等信息
            # 这里需要根据实际的页面结构调整
            for i, cell in enumerate(cells):
                cell_text = cell.text.strip()
                if not cell_text:
                    continue
                
                # 简单的启发式规则
                if i == 1 or '作者' in cell_text:
                    paper['authors'] = cell_text.replace('作者:', '').strip()
                elif i == 2 or '期刊' in cell_text or '来源' in cell_text:
                    paper['journal'] = cell_text.replace('期刊:', '').replace('来源:', '').strip()
                elif re.search(r'(19|20)\d{2}', cell_text):
                    year_match = re.search(r'(19|20)\d{2}', cell_text)
                    if year_match:
                        paper['publish_time'] = year_match.group()
            
            # 如果没有从单元格获取到信息，尝试从整行文本提取
            if not paper['publish_time']:
                year_match = re.search(r'(19|20)\d{2}', row_text)
                if year_match:
                    paper['publish_time'] = year_match.group()
            
            return paper
            
        except Exception as e:
            return None
    
    def scrape_papers(self, url, max_pages=3):
        """抓取论文信息"""
        if not self.setup_driver():
            return []
        
        try:
            print(f"🎯 开始访问: {url}")
            self.driver.get(url)
            
            # 等待页面加载
            time.sleep(3)
            
            all_papers = []
            
            for page in range(1, max_pages + 1):
                print(f"\n📄 正在处理第 {page} 页...")
                
                if page > 1:
                    # 尝试点击下一页
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".but-r, .next, [title='下一页']")
                        if next_button.is_enabled():
                            next_button.click()
                            time.sleep(3)
                        else:
                            print("❌ 没有更多页面")
                            break
                    except NoSuchElementException:
                        print("❌ 找不到下一页按钮")
                        break
                
                # 等待结果加载
                if self.wait_for_results():
                    papers = self.extract_papers_from_page()
                    if papers:
                        all_papers.extend(papers)
                        print(f"✅ 第 {page} 页成功提取 {len(papers)} 篇论文")
                    else:
                        print(f"⚠️ 第 {page} 页没有提取到论文")
                        if page > 1:
                            break
                else:
                    print(f"❌ 第 {page} 页加载失败")
                    break
                
                # 页面间延迟
                if page < max_pages:
                    time.sleep(2)
            
            self.papers_data = all_papers
            print(f"\n🎉 抓取完成！共获取 {len(all_papers)} 篇论文")
            return all_papers
            
        except Exception as e:
            print(f"❌ 抓取过程失败: {e}")
            return []
        
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 浏览器已关闭")
    
    def save_to_excel(self, papers, filename="首都图书馆相关论文.xlsx"):
        """保存到Excel"""
        if not papers:
            print("❌ 没有数据可保存")
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
            
            print(f"✅ 数据已保存到: {filename}")
            print(f"📊 共保存 {len(data)} 条记录")
            return True
            
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            return False

def main():
    """主函数"""
    url = "https://kns.cnki.net/kns8s/defaultresult/index?crossids=YSTT4HG0%2CLSTPFY1C%2CJUP3MUPD%2CMPMFIG1A%2CWQ0UVIAA%2CBLZOG7CK%2CPWFIRAGL%2CEMRPGLPA%2CNLBO1Z6R%2CNN3FJMUV&korder=AF&kw=%E9%A6%96%E9%83%BD%E5%9B%BE%E4%B9%A6%E9%A6%86"
    
    print("🚀 CNKI论文信息抓取工具 - Selenium版本")
    print("=" * 60)
    print(f"🔍 搜索关键词: 首都图书馆")
    print(f"🌐 目标网站: CNKI中国知网")
    print("=" * 60)
    
    try:
        scraper = CNKISeleniumScraper()
        papers = scraper.scrape_papers(url, max_pages=1)
        
        if papers:
            # 显示前几条数据
            print(f"\n📋 数据预览 (前3条):")
            for i, paper in enumerate(papers[:3], 1):
                print(f"\n{i}. 📄 {paper['title'][:60]}...")
                print(f"   👤 作者: {paper['authors'][:40]}...")
                print(f"   📖 期刊: {paper['journal'][:40]}...")
                print(f"   📅 时间: {paper['publish_time']}")
                print(f"   🔗 链接: {paper['link'][:60]}...")
            
            # 保存数据
            success = scraper.save_to_excel(papers)
            
            if success:
                print(f"\n🎉 任务完成！")
            else:
                print(f"\n⚠️ 数据抓取成功，但保存失败")
        else:
            print(f"\n❌ 没有抓取到数据")
            
    except Exception as e:
        print(f"\n💥 程序执行失败: {e}")

if __name__ == "__main__":
    main()
