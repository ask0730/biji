import re
import sys
from datetime import datetime, timedelta

def filter_library_data(data_array, filter_pattern=None, keyword_pattern=None):
    """
    图书馆数据处理插件：过滤数组和提取关键信息
    
    Args:
        data_array (list): 原始数据数组，格式为 [[标题, 链接, 日期], ...]
        filter_pattern (str): 过滤模式，如果为None则使用默认模式
        keyword_pattern (str): 关键词模式，如果为None则使用默认模式
    
    Returns:
        list: 处理后的数据数组，格式为 [[标题, 链接, 日期, 关键信息], ...]
    """
    try:
        # 默认过滤模式（匹配服务通知相关标题）
        if filter_pattern is None:
            filter_pattern = r"(?:公告|通告|通知|开放|开馆|闭馆|临时闭馆|暂停|恢复|扩大|调整|优化|规范|延长|新增|推出|免除|外借|借阅|阅览|预约|续借|通借通还|逾期|滞还|滞纳|欠费|押金|读者卡|一卡通|借阅证|读者证|社保证|社会保障卡|证卡|卡证|坐席|区域|占座|座位|积分|信用积分|未成年|儿童|青少年|幼儿|婴幼儿|母婴|孩子|老年人|老年群体|残疾|残障|视障|听障)"
        
        # 默认关键词模式（匹配服务类型和人群）
        if keyword_pattern is None:
            keyword_pattern = r"(?:文献服务|证卡服务|费用免除服务|其他服务|未成年|老年人|残障|普通读者)"
        
        # 第一步：过滤数组
        filtered_data = []
        for item in data_array:
            if len(item) >= 1:  # 确保至少有标题
                title = item[0]
                if re.search(filter_pattern, title):
                    filtered_data.append(item)
        
        print(f"过滤后剩余 {len(filtered_data)} 条记录")
        
        # 第二步：提取关键信息
        processed_data = []
        for item in filtered_data:
            keywords = []
            
            # 遍历每个元素查找关键词
            for element in item:
                if isinstance(element, str):
                    matches = re.findall(keyword_pattern, element)
                    for match in matches:
                        if match not in keywords:
                            keywords.append(match)
            
            # 添加关键信息到结果中
            if keywords:
                item_with_keywords = item + ["，".join(keywords)]
            else:
                item_with_keywords = item + [""]
            
            processed_data.append(item_with_keywords)
        
        print(f"处理完成，共 {len(processed_data)} 条记录")
        return processed_data
        
    except Exception as e:
        print(f"处理数据时发生错误: {e}")
        return []

def filter_by_date_range(data_array, days_back=7):
    """
    按日期范围过滤数据
    
    Args:
        data_array (list): 数据数组，格式为 [[标题, 链接, 日期, 关键信息], ...]
        days_back (int): 向前查找的天数，默认7天
    
    Returns:
        list: 过滤后的数据数组
    """
    try:
        # 计算日期范围
        current_date = datetime.now()
        yesterday = current_date - timedelta(days=1)
        start_date = current_date - timedelta(days=days_back)
        
        # 格式化日期字符串
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        start_date_str = start_date.strftime("%Y-%m-%d")
        
        print(f"过滤日期范围: {start_date_str} 到 {yesterday_str}")
        
        filtered_data = []
        for item in data_array:
            if len(item) >= 3:  # 确保有日期字段
                date_str = item[2].strip()
                formatted_date = ""
                
                # 处理不同日期格式
                if re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", date_str):
                    # yyyy-mm-dd 格式
                    parts = date_str.split("-")
                    if len(parts) == 3:
                        year, month, day = parts
                        formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
                elif re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", date_str):
                    # yyyy/mm/dd 格式
                    parts = date_str.split("/")
                    if len(parts) == 3:
                        year, month, day = parts
                        formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
                elif re.match(r"^\d{4}\.\d{1,2}\.\d{1,2}$", date_str):
                    # yyyy.mm.dd 格式
                    parts = date_str.split(".")
                    if len(parts) == 3:
                        year, month, day = parts
                        formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                
                # 检查日期是否在范围内
                if formatted_date and start_date_str <= formatted_date <= yesterday_str:
                    filtered_data.append(item)
        
        print(f"日期过滤后剩余 {len(filtered_data)} 条记录")
        return filtered_data
        
    except Exception as e:
        print(f"日期过滤时发生错误: {e}")
        return []

def add_library_name(data_array, library_name="上海图书馆"):
    """
    为数据添加图书馆名称列
    
    Args:
        data_array (list): 数据数组
        library_name (str): 图书馆名称
    
    Returns:
        list: 添加图书馆名称后的数据数组
    """
    try:
        result = []
        for item in data_array:
            new_item = [library_name] + item
            result.append(new_item)
        
        print(f"已为 {len(result)} 条记录添加图书馆名称")
        return result
        
    except Exception as e:
        print(f"添加图书馆名称时发生错误: {e}")
        return []

def main():
    """主函数：处理命令行参数或使用默认值"""
    # 默认测试数据
    test_data = [
        ["关于暂停国家数字图书馆APP在线办证功能的通知", "https://www.nlc.cn/web/dsb_zx/zxgg/20250731_2647288.shtml", "2025-07-31"],
        ["测试记录1", "https://example.com/1", "2025/08/07"],
        ["测试记录2", "https://example.com/2", "2025/8/7"],
        ["测试记录3", "https://example.com/3", "2024-09-05"],
        ["匹配记录1", "https://example.com/4", "2025-08-06"],
        ["匹配记录2", "https://example.com/5", "2025.08.07"],
        ["匹配记录3", "https://example.com/6", "2025/8/6"]
    ]
    
    print("图书馆数据处理插件")
    print("=" * 50)
    
    # 处理数据
    print("1. 过滤数组...")
    filtered_data = filter_library_data(test_data)
    
    print("2. 按日期过滤...")
    date_filtered_data = filter_by_date_range(filtered_data)
    
    print("3. 添加图书馆名称...")
    final_data = add_library_name(date_filtered_data)
    
    print("=" * 50)
    print("处理结果:")
    for i, item in enumerate(final_data, 1):
        print(f"{i}. {item}")
    
    return final_data

if __name__ == "__main__":
    main()
