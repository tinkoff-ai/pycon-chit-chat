from pathlib import Path

from pydantic import BaseSettings


class TelegramSettings(BaseSettings):
    token: str = None
    
    def __post_init__(self):
        if self.token is None:
            raise ValueError("token is required")
        
    class Config:
        env_prefix = 'TG_'


class ModelSettings(BaseSettings):
    generator_model_path: str = 'tinkoff-ai/ruDialoGPT-medium'
    crossencoder_model_path: str = 'tinkoff-ai/response-quality-classifier-large'
    toxicity_classifier_model_path: str = 'tinkoff-ai/response-toxicity-classifier-base'
    max_toxicity_score: float = 0.5
    
    class Config:
        env_prefix = 'MODEL_'
    
    
class GenerationSettings(BaseSettings):
    max_new_tokens: int = 40
    repetition_penalty: float = 2.5
    do_sample: bool = True
    top_k: int = 10
    top_p: float = 0.98
    temperature: float = 0.8
    num_beams: int = 5
    no_repeat_ngram_size: int = 4
    length_penalty: float = 2.0
    num_return_sequences: int = 5

    class Config:
        env_prefix = 'GENERATION_'
