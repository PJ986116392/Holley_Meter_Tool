import glob,os,re

def process_all_txt_files(folder_path):
    """
    处理指定文件夹内所有txt文件
    """
    # 获取所有txt文件路径
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    
    if not txt_files:
        print(f"在文件夹 {folder_path} 中未找到txt文件")
        return
    
    print(f"找到 {len(txt_files)} 个txt文件:")
    
    for file_path in txt_files:
        print(f"\n处理文件: {os.path.basename(file_path)}")
        
        # 在这里调用你的数据处理函数
        process_single_file(file_path)

def process_single_file(file_path):
    """
    处理单个文件
    """
    try:
        # 这里是你的数据处理逻辑
        output_filename = f"extracted_{os.path.basename(file_path)}"
        output_path = os.path.join(os.path.dirname(file_path), output_filename)
        
        # 调用之前的数据提取函数
        result = extract_bushound_data(file_path, output_path)
        
        print(f"  成功处理，提取了 {len(result)} 条数据")
        print(f"  输出文件: {output_filename}")
        
    except Exception as e:
        print(f"  处理文件时出错: {e}")


def extract_bushound_data(input_file, output_file):
    """
    从BusHound抓包数据中提取数据长度和数据内容
    
    Args:
        input_file: 输入文件名
        output_file: 输出文件名
    """
    
    # 正则表达式匹配数据行
    # 匹配格式: 设备号 地址 长度 数据 描述...
    pattern = r'^\s*(\d+)\s+([0-9a-fA-F]+)\s+(([0-9a-fA-F]+\s+)+)\s+([0-9a-fA-F\s]+)\s+[^\d]'
    
    extracted_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 跳过注释行和空行
            if line.strip() and not line.startswith(('Device', '------', 'Bus Hound')):
                match = re.search(pattern, line)
                if match:
                    length = int(match.group(2).strip())
                    data = match.group(3).strip()
                    # 数据校验
                    data_len = int(len(data.replace(' ',''))/2)
                    if length == data_len:
                        # 清理数据中的多余空格
                        data = re.sub(r'\s+', ' ', data)
                        
                        extracted_data.append(f"{length} {data}")
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in extracted_data:
            f.write(item + '\n')
    
    return extracted_data

# 使用示例
if __name__ == "__main__":
        process_all_txt_files(r"G:")
