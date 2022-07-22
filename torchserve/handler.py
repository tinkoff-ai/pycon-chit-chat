import json
import logging
from typing import Dict, List, Union

import transformers
from ts.context import Context
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)
logger.info('Transformers version %s', transformers.__version__)


class SomeHandler(BaseHandler):
    def __init__(self) -> None:
        super().__init__()
        self.tokenizer = None

    def initialize(self, context: Context) -> None:
        self.manifest = context.manifest
        properties = context.system_properties
        model_dir = properties['model_dir']  # automatically passed by torchserve

        logger.info('>>> PROPERTIES: %s', properties)
        logger.info('>>> MANIFEST: %s', self.manifest)

        self.initialized = True

    @staticmethod
    def get_text_from_data(data: List[Dict[str, Union[str, bytes, bytearray]]]) -> str:
        if len(data) > 1:
            raise ValueError('Generation for multiple promts is not supported yet')

        request = data[0]
        text = request.get('text') or request.get('body')
        text = text.decode('utf-8') if isinstance(text, (bytes, bytearray)) else text
        logger.info('>>> Recieved text: %s', text)
        return text

    def handle(self, data: List[Dict[str, Union[str, bytes, bytearray]]], context: Context) -> List[str]:
        self.context = context
        text = self.get_text_from_data(data)
        return [json.dumps(text, ensure_ascii=False)]
