# -*- coding: utf-8 -*-
"""
功能：读取原始CSV，分析message的情感，仅输出3个字段（情感倾向、强度、严格限制的情感大类）
情感大类限制：愉悦、满意、烦躁、失望、无情绪（可在代码中修改）
"""

import json
import requests
import random
from tqdm import tqdm
import time
import pandas as pd
from typing import Dict

# -------------------------- 1. 基础配置（需修改2处：API密钥、文件路径） --------------------------
# 1.1 DeepSeek API配置（替换为你的密钥）
DEEPSEEK_API_KEY = "sk-YOURAPI"  # 必须替换！
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 1.2 文件路径（替换为你的原始CSV和输出路径）
INPUT_CSV_PATH = "南京景区-天气-社媒情感融合表.csv"    # 你的输入CSV路径
OUTPUT_CSV_PATH = "情感分析结果（限制情感大类）.csv"  # 输出路径（加后缀区分旧结果）

# 1.3 核心：预设情感大类（可根据需求修改，模型必须从这里选）
ALLOWED_EMOTIONS = ["愉悦", "悲伤","怀旧", "烦躁", "失望","无情绪"]

# 1.4 情感分析示例（严格使用预设的情感大类，引导模型输出）
EMOTION_FEW_SHOT = [
    {
        "input": {"id": "1", "message": "老街书店很有复古感，木质香气很舒服"},
        "output": {"sentiment": "正面", "intensity": 8, "emotion_type": "愉悦"}  # 符合ALLOWED_EMOTIONS
    },
    {
        "input": {"id": "2", "message": "景区人太多，排队2小时体验差"},
        "output": {"sentiment": "负面", "intensity": 7, "emotion_type": "烦躁"}  # 符合ALLOWED_EMOTIONS
    },
    {
        "input": {"id": "3", "message": "今天气温15℃，东南风2级"},
        "output": {"sentiment": "中性", "intensity": 0, "emotion_type": "无情绪"}  # 符合ALLOWED_EMOTIONS
    }
]

# -------------------------- 2. 核心函数（严格限制情感大类） --------------------------
def call_deepseek_emotion(text: str, sample_id: str) -> Dict:
    """调用API分析情感，确保emotion_type仅来自ALLOWED_EMOTIONS"""
    # 构建提示词（强制要求情感大类从预设列表选择）
    prompt = f"""你是情感分析助手，仅输出JSON格式结果（无任何额外文字），含3个字段：
1. sentiment：情感倾向（仅"正面"/"负面"/"中性"）
2. intensity：情感强度（0-10整数，0=无情绪，10=最强）
3. emotion_type：具体情感，**必须从[{','.join(ALLOWED_EMOTIONS)}]中选择1个**（禁止自定义）

参考示例：
{json.dumps(EMOTION_FEW_SHOT, ensure_ascii=False, indent=2)}

现在分析：
id：{sample_id}
message：{text}

仅返回JSON（不要加其他内容，emotion_type必须在允许的列表中）："""

    # API请求配置
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # 低随机性，确保严格遵循规则
        "max_tokens": 500
    }

    # 3次重试机制
    for _ in range(3):
        try:
            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            result = json.loads(response.json()["choices"][0]["message"]["content"].strip())
            
            # 关键：验证emotion_type是否合规，不合规则强制修正为"无情绪"
            if result.get("emotion_type") not in ALLOWED_EMOTIONS:
                result["emotion_type"] = "无情绪"
            
            return {
                "sentiment": result.get("sentiment", "中性"),
                "intensity": int(result.get("intensity", 0)) if str(result.get("intensity", 0)).isdigit() else 0,
                "emotion_type": result["emotion_type"]  # 已确保合规
            }
        except Exception as e:
            time.sleep(5)
            continue
    
    # 多次失败返回默认值（合规）
    return {"sentiment": "中性", "intensity": 0, "emotion_type": "无情绪"}

def process_csv_emotion():
    """读取CSV→分析情感（限制大类）→保存结果"""
    # 1. 读取原始CSV
    try:
        df = pd.read_csv(INPUT_CSV_PATH, encoding="utf-8-sig")
    except FileNotFoundError:
        print(f"错误：原始CSV文件没找到 → {INPUT_CSV_PATH}")
        return
    except Exception as e:
        print(f"读取CSV失败：{str(e)}")
        return

    # 检查必要字段
    if not all(col in df.columns for col in ["mid", "message"]):
        print("错误：原始CSV缺少'mid'或'message'字段")
        return

    # 2. 批量分析（逐行处理）
    emotion_list = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="分析情感中（限制大类）"):
        message = str(row["message"]).strip()
        mid = str(row["mid"])
        
        # 处理空message
        if not message or message in ["nan", "None"]:
            emotion_list.append({"sentiment": "中性", "intensity": 0, "emotion_type": "无情绪"})
            time.sleep(0.5)
            continue
        
        # 调用API（已限制情感大类）
        emotion_res = call_deepseek_emotion(message, mid)
        emotion_list.append(emotion_res)
        time.sleep(1)  # 避免API频率限制

    # 3. 合并结果并保存
    emotion_df = pd.DataFrame(emotion_list)
    df_final = pd.concat([df, emotion_df], axis=1)
    
    try:
        df_final.to_csv(OUTPUT_CSV_PATH, index=False, encoding="utf-8-sig")
        print(f"\n✅ 处理完成！")
        print(f"📁 新CSV路径：{OUTPUT_CSV_PATH}")
        print(f"🔍 情感大类限制为：{ALLOWED_EMOTIONS}")
        print(f"🔍 新增字段：sentiment、intensity、emotion_type（严格限制）")
    except Exception as e:
        print(f"保存CSV失败：{str(e)}")

# -------------------------- 3. 运行入口 --------------------------
if __name__ == "__main__":
    random.seed(42)
    process_csv_emotion()