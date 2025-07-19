import os
import pickle
from typing import Dict, Any

from ..config import FAQ_DATA_PATH


def load_faq_data(file_path: str = None) -> dict:
    """
    FAQ 데이터 로드
    """
    path = file_path or FAQ_DATA_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"파일이 존재하지 않음: {path}")
    
    with open(path, 'rb') as f:
        data = pickle.load(f)

    if not data:
        raise ValueError("데이터가 비어있음")

    print(f"FAQ 로드 완료: {len(data)}건")
    return data


def get_sample_faq(data: dict, n: int = 5) -> dict:
    """
    faq 샘플 확인용
    """
    if n >= len(data):
        return data
    sample_keys = list(data.keys())[:n]
    return {k: data[k] for k in sample_keys}
