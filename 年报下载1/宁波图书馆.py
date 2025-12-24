# -*- coding: utf-8 -*-
"""
宁波图书馆年报下载脚本
功能：从宁波图书馆官网下载去年的年报，并重命名为"宁波图书馆年份年报"格式
"""

import requests
import os
import time
import re
import urllib3
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_headers():
    """获取模拟浏览器的请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/pdf',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

def clean_filename(filename):
    """清理文件名，移除Windows不允许的字符"""
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '_', filename)
    cleaned = cleaned.strip(' .')
    if not cleaned:
        cleaned = "unnamed_file"
    return cleaned

def extract_year_from_text(text):
    """从文本中提取年份，优先提取完整的年份（如2023、2024）"""
    if not text:
        return None
    # 优先匹配完整的4位年份（2000-2099）
    year_match = re.search(r'(20[0-3]\d)', text)
    if year_match:
        return year_match.group(1)
    return None

def extract_year_from_url_params(url):
    """从URL参数中提取年份（特别是从filename参数）"""
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        # 检查filename参数
        if 'filename' in params:
            filename = params['filename'][0]
            year = extract_year_from_text(filename)
            if year:
                return year
    except:
        pass
    return None

def load_config(config_path="config.txt"):
    """读取配置文件"""
    config = {}
    try:
        if not os.path.exists(config_path):
            # 如果配置文件不存在，创建默认配置
            default_config = """# 配置文件
# 格式：key=value
# 支持使用 # 开头添加注释
# 支持空行

# 输出文件夹路径（必填）
# 示例：output_folder=D:\\Desktop\\图书馆年报
output_folder=D:\\Desktop\\图书馆年报
"""
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(default_config)
            print(f"✓ 已创建默认配置文件: {config_path}")
            print("  请编辑配置文件设置输出路径后重新运行")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    config[key] = value
    except Exception as e:
        print(f"✗ 读取配置文件失败: {e}")
        return None
    
    return config

def find_last_year_report(url, base_url):
    """在页面中查找去年的年报链接"""
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 使用requests方式直接查找
    print("正在访问页面查找年报...")
    session = requests.Session()
    session.headers.update(get_headers())
    
    try:
        # 尝试访问页面，如果http失败则尝试https
        print(f"正在访问页面: {url}")
        try:
            response = session.get(url, timeout=30, verify=False)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            # 如果http失败，尝试https
            if url.startswith('http://'):
                https_url = url.replace('http://', 'https://', 1)
                print(f"HTTP访问失败，尝试HTTPS: {https_url}")
                try:
                    response = session.get(https_url, timeout=30, verify=False)
                    response.raise_for_status()
                    url = https_url  # 更新url为https版本
                except requests.exceptions.RequestException as e2:
                    print(f"HTTPS访问也失败: {e2}")
                    raise
            else:
                raise
        
        response.encoding = response.apparent_encoding or 'utf-8'
        
        # 显示页面基本信息
        print(f"\n页面访问成功")
        print(f"页面大小: {len(response.text):,} 字符")
        print(f"页面编码: {response.encoding}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 检查页面标题
        title_tag = soup.find('title')
        if title_tag:
            print(f"页面标题: {title_tag.get_text().strip()}")
        
        print(f"\n查找 {last_year} 年的年报...")
        
        # 查找所有链接，查找同时包含"图书馆"和"决算"或"年报"的链接
        all_links = []
        
        # 查找所有a标签，检查文本或title属性中是否包含关键词
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text().strip()
            title = link.get('title', '')
            
            if not href:
                continue
            
            # 跳过javascript链接和无效链接
            if href.startswith('javascript:') or href.startswith('#') or href.strip() == '':
                continue
            
            # 检查链接文本或title属性中是否包含关键词
            check_text = text or title
            if not check_text:
                continue
            
            # 检查是否同时包含"图书馆"和"决算"，或者包含"图书馆"和"年报"
            has_library = '图书馆' in check_text
            has_juesuan = '决算' in check_text
            has_report = '年报' in check_text or '年度报告' in check_text
            
            # 必须包含"图书馆"，并且包含"决算"或"年报"
            if not (has_library and (has_juesuan or has_report)):
                continue
            
            # 构建完整URL
            full_url = urljoin(url, href)
            
            # 检查是否是PDF或DOCX文件
            is_pdf = full_url.lower().endswith('.pdf') or href.lower().endswith('.pdf')
            is_docx = full_url.lower().endswith('.docx') or href.lower().endswith('.docx')
            is_doc = full_url.lower().endswith('.doc') or href.lower().endswith('.doc')
            is_html = full_url.lower().endswith(('.html', '.htm', '.shtml')) or href.lower().endswith(('.html', '.htm', '.shtml'))
            
            # 提取年份
            year_in_text = extract_year_from_text(check_text)
            year_in_url_params = extract_year_from_url_params(full_url)
            year_in_url_path = extract_year_from_text(href)
            extracted_year = year_in_text or year_in_url_params or year_in_url_path
            
            all_links.append({
                'url': full_url,
                'text': check_text,
                'year': extracted_year,
                'is_pdf': is_pdf,
                'is_docx': is_docx,
                'is_doc': is_doc,
                'is_html': is_html,
                'is_report': True
            })
        
        # 打印所有找到的链接（用于调试）
        if all_links:
            print(f"找到 {len(all_links)} 个可能的链接")
            print("详细链接信息:")
            for link_info in all_links[:10]:  # 只显示前10个
                print(f"  - {link_info['text']} | 年份: {link_info['year']} | URL: {link_info['url'][:80]}")
        
        # 优先查找去年的年报
        last_year_links = []
        for link_info in all_links:
            # 更严格的年份匹配：必须完全匹配去年的年份
            if link_info['year'] == last_year_str:
                last_year_links.append(link_info)
        
        if last_year_links:
            # 优先选择PDF链接
            pdf_links = [link for link in last_year_links if link['is_pdf'] and link['url'].lower().endswith('.pdf')]
            if pdf_links:
                # 优先选择包含"年报"的PDF链接
                for link_info in pdf_links:
                    if '年报' in link_info['text'] or '年报' in link_info['url'] or '年度报告' in link_info['text']:
                        print(f"✓ 找到去年的年报PDF链接: {link_info['text']} (年份: {link_info['year']})")
                        print(f"  URL: {link_info['url']}")
                        return link_info['url'], link_info['year']
                # 如果没有明确标注"年报"的，返回第一个PDF链接
                print(f"✓ 找到去年的PDF链接: {pdf_links[0]['text']} (年份: {pdf_links[0]['year']})")
                print(f"  URL: {pdf_links[0]['url']}")
                return pdf_links[0]['url'], pdf_links[0]['year']
            
            # 如果没有PDF，尝试DOCX格式
            docx_links = [link for link in last_year_links if link['is_docx'] and link['url'].lower().endswith('.docx')]
            if docx_links:
                # 优先选择包含"年报"的DOCX链接
                for link_info in docx_links:
                    if '年报' in link_info['text'] or '年报' in link_info['url'] or '年度报告' in link_info['text']:
                        print(f"✓ 找到去年的年报DOCX链接: {link_info['text']} (年份: {link_info['year']})")
                        print(f"  URL: {link_info['url']}")
                        return link_info['url'], link_info['year']
                # 如果没有明确标注"年报"的，返回第一个DOCX链接
                print(f"✓ 找到去年的DOCX链接: {docx_links[0]['text']} (年份: {docx_links[0]['year']})")
                print(f"  URL: {docx_links[0]['url']}")
                return docx_links[0]['url'], docx_links[0]['year']
            
            # 如果没有DOCX，尝试DOC格式
            doc_links = [link for link in last_year_links if link['is_doc'] and link['url'].lower().endswith('.doc')]
            if doc_links:
                for link_info in doc_links:
                    if '年报' in link_info['text'] or '年报' in link_info['url'] or '年度报告' in link_info['text']:
                        print(f"✓ 找到去年的年报DOC链接: {link_info['text']} (年份: {link_info['year']})")
                        print(f"  URL: {link_info['url']}")
                        return link_info['url'], link_info['year']
                print(f"✓ 找到去年的DOC链接: {doc_links[0]['text']} (年份: {doc_links[0]['year']})")
                print(f"  URL: {doc_links[0]['url']}")
                return doc_links[0]['url'], doc_links[0]['year']
            
            # 优先处理HTML链接，进入页面查找PDF文档
            html_links = [link for link in last_year_links if link.get('is_html', False)]
            if html_links:
                print(f"找到 {len(html_links)} 个去年的HTML链接，正在进入页面查找PDF文档...")
                for link_info in html_links:
                    print(f"访问页面: {link_info['text']}")
                    html_url = link_info['url']
                    print(f"  URL: {html_url}")
                    try:
                        link_response = session.get(html_url, timeout=30, verify=False)
                        link_response.raise_for_status()
                        link_response.encoding = link_response.apparent_encoding or 'utf-8'
                        link_soup = BeautifulSoup(link_response.text, 'html.parser')
                        
                        # 在这个页面中查找文档链接（PDF/DOCX/DOC）
                        doc_candidates = []  # 存储找到的文档候选
                        
                        for doc_link in link_soup.find_all('a', href=True):
                            doc_href = doc_link.get('href')
                            doc_text = doc_link.get_text().strip()
                            doc_title = doc_link.get('title', '')
                            doc_check_text = doc_text or doc_title
                            
                            if not doc_href or doc_href.startswith('javascript:') or doc_href.startswith('#'):
                                continue
                            
                            doc_full_url = urljoin(html_url, doc_href)
                            
                            # 检查是否是文档文件（必须是真正的文档文件）
                            is_doc_file = (doc_full_url.lower().endswith(('.pdf', '.docx', '.doc')) or 
                                         doc_href.lower().endswith(('.pdf', '.docx', '.doc')))
                            
                            # 只处理真正的文档文件
                            if not is_doc_file:
                                continue
                            
                            # 检查是否包含年报相关关键词
                            doc_keywords = ['年报', '年度报告', '决算', '报告', '附件', '下载']
                            has_report_keyword = any(keyword in doc_check_text or keyword in doc_href.lower() for keyword in doc_keywords)
                            
                            # 检查年份
                            doc_year = extract_year_from_text(doc_check_text) or extract_year_from_text(doc_href) or extract_year_from_url_params(doc_full_url)
                            
                            # 记录所有找到的文档
                            doc_candidates.append({
                                'url': doc_full_url,
                                'text': doc_check_text,
                                'year': doc_year,
                                'has_keyword': has_report_keyword,
                                'is_pdf': doc_full_url.lower().endswith('.pdf')
                            })
                        
                        # 优先选择PDF格式且包含关键词的文档
                        for candidate in doc_candidates:
                            if candidate['is_pdf'] and candidate['has_keyword'] and (candidate['year'] == last_year_str or not candidate['year']):
                                print(f"✓ 在页面找到年报PDF: {candidate['text']}")
                                print(f"  URL: {candidate['url']}")
                                return candidate['url'], candidate['year'] or last_year_str
                        
                        # 其次选择任何PDF文档
                        for candidate in doc_candidates:
                            if candidate['is_pdf'] and (candidate['year'] == last_year_str or not candidate['year']):
                                print(f"✓ 在页面找到PDF文档: {candidate['text']}")
                                print(f"  URL: {candidate['url']}")
                                return candidate['url'], candidate['year'] or last_year_str
                        
                        # 最后选择其他格式的文档
                        for candidate in doc_candidates:
                            if candidate['has_keyword'] and (candidate['year'] == last_year_str or not candidate['year']):
                                print(f"✓ 在页面找到年报文档: {candidate['text']}")
                                print(f"  URL: {candidate['url']}")
                                return candidate['url'], candidate['year'] or last_year_str
                        
                        # 如果都没找到，尝试查找所有文档链接（不限制年份）
                        if doc_candidates:
                            # 优先PDF
                            for candidate in doc_candidates:
                                if candidate['is_pdf']:
                                    print(f"✓ 在页面找到PDF文档（未验证年份）: {candidate['text']}")
                                    print(f"  URL: {candidate['url']}")
                                    return candidate['url'], candidate['year'] or last_year_str
                            # 其他格式
                            print(f"✓ 在页面找到文档（未验证年份）: {doc_candidates[0]['text']}")
                            print(f"  URL: {doc_candidates[0]['url']}")
                            return doc_candidates[0]['url'], doc_candidates[0]['year'] or last_year_str
                        
                        # 如果没找到文档链接，尝试查找iframe或embed标签中的PDF
                        for iframe in link_soup.find_all(['iframe', 'embed']):
                            src = iframe.get('src') or iframe.get('data-src')
                            if src:
                                iframe_url = urljoin(html_url, src)
                                if iframe_url.lower().endswith(('.pdf', '.docx', '.doc')):
                                    print(f"✓ 在页面找到文档（iframe）: {iframe_url}")
                                    return iframe_url, last_year_str
                        
                        # 尝试在页面文本中查找PDF URL（可能以文本形式存在）
                        page_text = link_soup.get_text()
                        pdf_url_pattern = r'https?://[^\s<>"]+\.pdf'
                        pdf_matches = re.findall(pdf_url_pattern, page_text, re.IGNORECASE)
                        if pdf_matches:
                            for pdf_url in pdf_matches:
                                if last_year_str in pdf_url:
                                    print(f"✓ 在页面文本中找到PDF URL: {pdf_url}")
                                    return pdf_url, last_year_str
                        
                        if not doc_candidates:
                            print(f"  在页面未找到文档链接")
                    except Exception as e:
                        print(f"  访问页面失败: {e}")
                        continue
            
            # 如果还是没有找到，返回第一个有效的去年的文档链接（必须是文档文件，不能是HTML页面）
            valid_doc_links = [link for link in last_year_links 
                             if not link['url'].startswith('javascript:') 
                             and (link['is_pdf'] or link['is_docx'] or link['is_doc'])]
            if valid_doc_links:
                print(f"✓ 找到去年的文档链接: {valid_doc_links[0]['text']} (年份: {valid_doc_links[0]['year']})")
                return valid_doc_links[0]['url'], valid_doc_links[0]['year']
        
        # 如果没有找到去年的年报，列出所有找到的链接供参考
        report_links = [link for link in all_links if (link['is_pdf'] or link['is_docx'] or link['is_doc'] or link['is_report']) and ('年报' in link['text'] or '年报' in link['url'])]
        if report_links:
            print(f"\n⚠️  未找到 {last_year} 年的年报，但找到其他年份的年报:")
            for link_info in report_links:
                print(f"    {link_info['text']} (年份: {link_info['year'] or '未知年份'})")
            print(f"\n✗ 未找到 {last_year} 年的年报，下载失败")
        else:
            print("✗ 未找到年报链接")
        
        return None
        
    except Exception as e:
        print(f"✗ 查找年报链接失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

def download_pdf(url, filename, save_dir):
    """下载文件（支持PDF、DOCX、DOC等格式）"""
    try:
        session = requests.Session()
        session.headers.update(get_headers())
        
        # 检查是否是PDF查看器页面，如果是则提取实际的PDF URL
        url_lower = url.lower()
        original_url = url
        if 'viewer.html' in url_lower or ('viewer' in url_lower and '?file=' in url_lower):
            # 尝试从URL参数中提取PDF文件路径
            try:
                from urllib.parse import urlparse, parse_qs, unquote
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                
                # 查找file参数
                if 'file' in params:
                    pdf_path = unquote(params['file'][0])  # URL解码
                    # 构建完整的PDF URL
                    if pdf_path.startswith('http'):
                        actual_pdf_url = pdf_path
                    elif pdf_path.startswith('/'):
                        # 绝对路径，使用base URL
                        base_url = f"{parsed.scheme}://{parsed.netloc}"
                        actual_pdf_url = urljoin(base_url, pdf_path)
                    else:
                        # 相对路径
                        actual_pdf_url = urljoin(url, pdf_path)
                    
                    print(f"检测到PDF查看器页面")
                    print(f"  原始URL: {original_url}")
                    print(f"  提取的PDF路径: {pdf_path}")
                    print(f"  实际PDF URL: {actual_pdf_url}")
                    url = actual_pdf_url
                else:
                    print(f"⚠️  警告: 未找到file参数，尝试直接访问查看器页面")
            except Exception as e:
                print(f"⚠️  提取PDF路径失败: {e}，尝试直接访问")
                import traceback
                traceback.print_exc()
        
        print(f"正在下载: {url}")
        response = session.get(url, stream=True, timeout=60, verify=False)
        response.raise_for_status()
        
        # 检查内容类型和文件扩展名
        content_type = response.headers.get('Content-Type', '').lower()
        url_lower = url.lower()
        
        # 检查是否是HTML文件，如果是则拒绝下载（除非是查看器页面）
        if 'text/html' in content_type and 'viewer' not in url_lower and not url_lower.endswith('.pdf'):
            print(f"✗ 错误: URL指向的是HTML页面，不是文档文件")
            print(f"  请检查页面中是否有PDF/DOCX/DOC文档链接")
            return False
        
        # 根据URL确定文件扩展名
        if url_lower.endswith('.docx'):
            file_ext = '.docx'
        elif url_lower.endswith('.doc'):
            file_ext = '.doc'
        elif url_lower.endswith('.pdf'):
            file_ext = '.pdf'
        else:
            # 根据Content-Type判断
            if 'word' in content_type or 'document' in content_type:
                if 'openxml' in content_type or 'docx' in content_type:
                    file_ext = '.docx'
                else:
                    file_ext = '.doc'
            elif 'pdf' in content_type:
                file_ext = '.pdf'
            else:
                file_ext = '.pdf'  # 默认使用pdf
        
        # 确保文件名有正确的扩展名
        if not filename.lower().endswith(('.pdf', '.docx', '.doc')):
            filename = filename + file_ext
        elif not filename.lower().endswith(file_ext):
            # 如果扩展名不匹配，替换为正确的扩展名
            filename = os.path.splitext(filename)[0] + file_ext
        
        # 清理文件名
        filename = clean_filename(filename)
        
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, filename)
        
        # 如果文件已存在，先删除
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  已删除已存在的文件: {filename}")
            except:
                pass
        
        # 保存文件
        file_size = 0
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    file_size += len(chunk)
        
        # 验证文件是否成功保存
        if not os.path.exists(file_path):
            print(f"✗ 文件保存失败: {file_path}")
            return False
        
        actual_size = os.path.getsize(file_path)
        print(f"✓ 下载成功: {filename}")
        print(f"  文件大小: {actual_size:,} 字节 ({actual_size/1024/1024:.2f} MB)")
        print(f"  保存路径: {file_path}")
        
        session.close()
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 下载失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("宁波图书馆年报下载工具")
    print("=" * 60)
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.txt")
    
    # 读取配置文件
    config = load_config(config_path)
    if config is None:
        return
    
    # 获取输出路径
    output_folder = config.get("output_folder", "").strip()
    if not output_folder:
        print("✗ 错误: 配置文件中未设置 output_folder")
        print("  请在配置文件中设置输出路径")
        return
    
    # 获取去年的年份
    current_year = int(time.strftime('%Y'))
    last_year = current_year - 1
    last_year_str = str(last_year)
    
    # 宁波图书馆年报页面URL
    report_page_url = "https://www.nblib.cn/category/194"
    base_url = "https://www.nblib.cn"
    
    print(f"目标年份: {last_year}年")
    print(f"输出路径: {output_folder}")
    print("-" * 60)
    
    # 查找年报链接
    result = find_last_year_report(report_page_url, base_url)
    
    if not result:
        print("\n✗ 未找到年报链接，下载失败")
        return
    
    # 处理返回值：可能是(url, year)元组或只有url
    if isinstance(result, tuple):
        file_url, actual_year = result
        # 使用实际找到的年份，而不是预设的去年年份
        if actual_year and actual_year != last_year_str:
            print(f"⚠️  注意：找到的是 {actual_year} 年的年报，不是 {last_year_str} 年的")
            # 如果找到的不是去年的，询问是否继续
            if actual_year < last_year_str:
                print(f"⚠️  这是前年的年报，是否继续下载？")
                # 继续下载，但使用实际年份
                year_for_filename = actual_year
            else:
                year_for_filename = actual_year
        else:
            year_for_filename = last_year_str
    else:
        file_url = result
        year_for_filename = last_year_str
    
    # 生成文件名，使用实际找到的年份
    # 根据URL确定文件扩展名
    if file_url.lower().endswith('.docx'):
        file_ext = '.docx'
    elif file_url.lower().endswith('.doc'):
        file_ext = '.doc'
    elif file_url.lower().endswith('.pdf'):
        file_ext = '.pdf'
    else:
        file_ext = '.pdf'  # 默认使用pdf
    
    filename = f"宁波图书馆{year_for_filename}年年报{file_ext}"
    filename = clean_filename(filename)
    
    print(f"\n文件名: {filename}")
    print("-" * 60)
    
    # 下载文件
    success = download_pdf(file_url, filename, output_folder)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ 下载完成")
        print("=" * 60)
        print(f"文件已保存到: {os.path.join(output_folder, filename)}")
    else:
        print("\n" + "=" * 60)
        print("✗ 下载失败")
        print("=" * 60)

if __name__ == "__main__":
    main()

