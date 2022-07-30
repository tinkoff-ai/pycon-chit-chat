from pathlib import Path
from typing import List
import torch

from transformers import (
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer
)

from tg_bot.settings import GenerationSettings


class Responder:
    def __init__(
    self, 
    generator_model_path: str, 
    crossencoder_model_path: str,
    toxicity_classifier_path: str,
    max_toxicity_score: float
    ):
        self._generator = AutoModelForCausalLM.from_pretrained(generator_model_path)
        self._generator_tokenizer = AutoTokenizer.from_pretrained(generator_model_path)    

        self._crossencoder = AutoModelForSequenceClassification.from_pretrained(crossencoder_model_path)
        self._crossencoder_tokenizer = AutoTokenizer.from_pretrained(crossencoder_model_path)

        self._toxicity_classifier = AutoModelForSequenceClassification.from_pretrained(toxicity_classifier_path)
        self._toxicity_tokenizer = AutoTokenizer.from_pretrained(toxicity_classifier_path)

        self._max_toxicity_score = max_toxicity_score

    def respond(self, dialog: List[str], generation_settings: GenerationSettings) -> str:
        text = self._prepare_dialog(dialog)
        responses = self._generate_candidates(text, generation_settings)
        filtered_responses = self._filter_toxic_responses(responses)
        best_response = self._choose_best_response(filtered_responses)
        return best_response.split('@@ВТОРОЙ@@')[0]

    def _prepare_dialog(self, dialog: List[str]) -> str:
        FIRST_SPEAKER_TOKEN = '@@ПЕРВЫЙ@@'
        SECOND_SPEAKER_TOKEN = '@@ВТОРОЙ@@'

        text = ''
        for i, replic in enumerate(dialog):
            if i % 2 == 0:
                speaker = FIRST_SPEAKER_TOKEN
            else:
                speaker = SECOND_SPEAKER_TOKEN
            text += f' {speaker} {replic.strip()}'

        final_token = FIRST_SPEAKER_TOKEN if i % 2 == 0 else SECOND_SPEAKER_TOKEN
        text += f' {final_token}'
        return text.strip()

    def _generate_candidates(self, text: str, generation_settings: GenerationSettings) -> List[str]:
        tokenized_text = self._generator_tokenizer(text, return_tensors='pt')
        input_size = tokenized_text.input_ids.size(1)
        generations = self._generator.generate(
            **tokenized_text, 
            max_new_tokens=generation_settings.max_new_tokens,
            repetition_penalty=generation_settings.repetition_penalty,
            do_sample=generation_settings.do_sample,
            top_k=generation_settings.top_k,
            top_p=generation_settings.top_p,
            temperature=generation_settings.temperature,
            num_beams=generation_settings.num_beams,
            no_repeat_ngram_size=generation_settings.no_repeat_ngram_size,
            length_penalty=generation_settings.length_penalty,
            num_return_sequences=generation_settings.num_return_sequences,
        )
        generations = generations[:, input_size:]
        generations = list(map(self._generator_tokenizer.decode, generations))
        return generations

    def _filter_toxic_responses(self, responses: List[str]) -> List[str]:
        tokenized_responses = self._toxicity_tokenizer(responses, return_tensors='pt', padding='longest')
        logits = self._toxicity_classifier(**tokenized_responses).logits
        probas = torch.softmax(logits, dim=-1).cpu().detach().numpy()
        toxicity_scores = 1 - probas[:, 0]
        return [response for response, tox_score in zip(responses, toxicity_scores) if tox_score < self._max_toxicity_score]

    def _choose_best_response(self, responses: List[str]) -> str:
        tokenized_responses = self._crossencoder_tokenizer(responses, return_tensors='pt', padding='longest')
        logits = self._crossencoder(**tokenized_responses).logits
        scores = torch.sigmoid(logits).cpu().detach().numpy().mean(axis=1)
        scores_argmax = scores.argmax(axis=0)
        return responses[scores_argmax.item()]
