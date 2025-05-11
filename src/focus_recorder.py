import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class FocusRecorder:
    def __init__(self, data_dir: str = "dirty"):
        """
        初始化专注记录器
        :param data_dir: 存储专注记录数据的目录
        """
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _get_today_file_path(self) -> str:
        """
        获取今天的记录文件路径
        :return: 文件路径
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.data_dir, f"{today}.json")

    def _load_today_records(self) -> List[Dict]:
        """
        加载今天的记录
        :return: 记录列表
        """
        file_path = self._get_today_file_path()
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_records(self, records: List[Dict]):
        """
        保存记录到文件
        :param records: 记录列表
        """
        file_path = self._get_today_file_path()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

    def add_focus_record(self, 
                        focus_goal: str,
                        start_time: datetime,
                        end_time: datetime,
                        duration_minutes: int,
                        notes: Optional[str] = None):
        """
        添加一条专注记录
        :param focus_goal: 专注目标
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param duration_minutes: 专注时长（分钟）
        :param notes: 备注（可选）
        """
        records = self._load_today_records()
        
        record = {
            "focus_goal": focus_goal,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration_minutes,
            "notes": notes,
            "record_time": datetime.now().isoformat()
        }
        
        records.append(record)
        self._save_records(records)

    def get_today_records(self) -> List[Dict]:
        """
        获取今天的专注记录
        :return: 记录列表
        """
        return self._load_today_records()

    def get_records_by_date(self, date: str) -> List[Dict]:
        """
        获取指定日期的专注记录
        :param date: 日期字符串，格式为 YYYY-MM-DD
        :return: 记录列表
        """
        file_path = os.path.join(self.data_dir, f"{date}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return [] 