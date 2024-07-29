"""Vega-Lite generator"""

import torch
from transformers import AutoTokenizer, BitsAndBytesConfig
from llama_index.llms.huggingface import HuggingFaceLLM, PromptTemplate

from bsql.model import Model


class VegaLite(Model):
    """Vega-Lite generator

    Args:
        model_name: base model name.

    Returns:
        A Vega-Lite json string.
    """

    def __init__(self, model_name="codellama/CodeLlama-7b-Instruct-hf"):
        super().__init__()
        self.model_name = model_name
        self.is_loaded = False

    def _load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            load_in_8bit_fp32_cpu_offload=True,
        )

        self.model = HuggingFaceLLM(
            model_name=self.model_name,
            tokenizer=self.tokenizer,
            query_wrapper_prompt=PromptTemplate("{query_str}"),
            max_new_tokens=512,
            model_kwargs={"quantization_config": quantization_config},
            generate_kwargs={
                "num_return_sequences": 1,
                "eos_token_id": self.tokenizer.eos_token_id,
                "pad_token_id": self.tokenizer.eos_token_id,
                "do_sample": False,
                "num_beams": 1,
            },
            device_map="auto",
        )
        self.is_loaded = True

    def _generate_vega(self, prompt: str) -> str:
        if not self.is_loaded:
            self._load_model()

        response = self.model.complete(prompt).text.strip()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        return response

    def inference(self, question: str, data_sample: str) -> str:
        """Generate a Vega-Lite json based on the provided data (sample => 5 samples) and question.

        Args:
            question: original user's question.
            data_sample: sample of the data .

        Returns:
            A Vega-Lite json string.
            # An Altair Chart object.
        """

        prompt = f"""
        Generate an insightful Vega-Lite visualization (Bar Chart, Pie Chart, Line Chart, etc.) that effectively illustrates the data and addresses the user's query.
        Ensure the Vega-Lite specification accurately represents the provided data and makes the visualization intuitive and informative.
        Pay meticulous attention to the specification's structure, including encoding, mark type, and any data transformations.
        Add a clear "title" to the visualization based on the data insights and the question.
        Generate only ONE proper json string, no text. Do NOT involve multiple charts such as "hconcat", "vconcat", "layer", "facet", "repeat", "concat", or "resolve".

        Consider the following guidelines for selecting the appropriate chart type:
        - For categorical data with distinct categories and proportions (Percentages), consider using a Pie Chart for better representation.
        - For numerical data with comparisons or trends over time, a Line Chart or Bar Chart might be more suitable.
        - If the data involves showing proportions or percentages of a whole, a Pie Chart could be effective.
        - For showing distributions or comparisons across categories, a Bar Chart might provide clearer insights.

        Question: {question}

        Data Sample: {data_sample}

        Vega-Lite Json:
        """

        vega_lite_generated = self._generate_vega(prompt)

        # you have to run this function as it replaces the data sample provided with the actual data
        # vega_lite_json = prepare_vega(vega_lite_generated)

        return vega_lite_generated
