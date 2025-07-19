import re
import tiktoken
from typing import List, Tuple, Dict, Any

from ..config import MAX_TOKENS_PER_CHUNK, OVERLAP_RATIO, EMBEDDING_MODEL


def split_into_sentences(text: str) -> list:
    """
    문단 -> 문장 단위 split
    chunking 전 문장 단위로 나누기
    """
    pattern = r'(?<=[.!?])\s+|(?<=[\.\?\!]["\'])\s+|(?<=다\.)\s+|(?<=요\.)\s+|(?<=니다\.)\s+|(?<=세요\.)\s+'
    return [s.strip() for s in re.split(pattern, text) if s.strip()]



def count_tokens(text: str, model: str = EMBEDDING_MODEL) -> int:
    """
    토큰 수 계산
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def chunk_qna_with_overlap(
    question: str, 
    answer: str, 
    max_tokens: int = MAX_TOKENS_PER_CHUNK, 
    overlap_ratio: float = OVERLAP_RATIO, 
    model: str = EMBEDDING_MODEL
) -> List[Tuple[str, str]]:
    """
    Q+A를 청킹하고, 오버랩 적용
    -> 청크 단위로 임베딩 생성
    """
    question_tokens = count_tokens(question, model)
    answer_tokens = count_tokens(answer, model)
    
    # 질문과 답변을 합쳐도 최대 토큰 수를 넘지 않으면 그대로 반환
    if question_tokens + answer_tokens <= max_tokens:
        return [(question, answer)]
 
    if question_tokens > max_tokens // 2:
        raise ValueError(f"{question_tokens} 토큰 (최대 {max_tokens//2})")

    answer_sentences = split_into_sentences(answer)

    sentence_tokens = [count_tokens(s, model) for s in answer_sentences]
    
    chunks = []
    available_tokens = max_tokens - question_tokens  
    
    current_chunk = []
    current_tokens = 0
    
    for i, (sentence, tokens) in enumerate(zip(answer_sentences, sentence_tokens)):
        if current_tokens + tokens <= available_tokens:
            current_chunk.append(sentence)
            current_tokens += tokens
        else:
            
            if current_chunk:
                chunks.append((question, " ".join(current_chunk)))
    
            current_chunk = [sentence]
            current_tokens = tokens
            
            if tokens > available_tokens:
                words = sentence.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = count_tokens(word + " ", model)
                    if temp_tokens + word_tokens <= available_tokens:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                    else:
                        chunks.append((question, " ".join(temp_chunk)))
                        temp_chunk = [word]
                        temp_tokens = word_tokens
                
                if temp_chunk:
                    current_chunk = temp_chunk
                    current_tokens = temp_tokens
                else:
                    current_chunk = []
                    current_tokens = 0
    
    if current_chunk:
        chunks.append((question, " ".join(current_chunk)))
    
    if len(chunks) > 1 and overlap_ratio > 0:
        overlapped_chunks = [chunks[0]]
        
        for i in range(1, len(chunks)):
            prev_answer = chunks[i-1][1]
            curr_answer = chunks[i][1]
            
            prev_sentences = split_into_sentences(prev_answer)
            
            overlap_count = max(1, int(len(prev_sentences) * overlap_ratio))
            
            overlap_sentences = prev_sentences[-overlap_count:] if overlap_count < len(prev_sentences) else prev_sentences
            
            overlapped_answer = " ".join(overlap_sentences) + " " + curr_answer
            
            while count_tokens(overlapped_answer, model) + question_tokens > max_tokens and overlap_sentences:
                overlap_sentences = overlap_sentences[1:]  # 첫 번째 오버랩 문장 제거
                overlapped_answer = " ".join(overlap_sentences) + " " + curr_answer
            
            overlapped_chunks.append((question, overlapped_answer))
        
        return overlapped_chunks
    
    return chunks


def process_qna_dict(
    qna_dict: dict,
    max_tokens: int = MAX_TOKENS_PER_CHUNK,
    overlap_ratio: float = OVERLAP_RATIO,
    model: str = EMBEDDING_MODEL
) -> dict:
    """
    청크에 question id 부여
    """
    result = {}
    chunk_id = 0

    for q, a in qna_dict.items():
        chunks = chunk_qna_with_overlap(q, a, max_tokens, overlap_ratio, model)
        for cq, ca in chunks:
            result[chunk_id] = {
                "question": cq,
                "answer": ca,
                "original_question": q
            }
            chunk_id += 1

    return result