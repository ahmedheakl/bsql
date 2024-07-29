"""Implementation of Data2Viz class using LLaMa-2 model"""

from typing import List
import re
import warnings

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from bsql.model import Model

warnings.filterwarnings("ignore")


hf_token = "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"


class Data2Viz(Model):
    """Data to Visualization class implementation using LLaMa-2 model"""

    model_name = "meta-llama/Llama-2-7b-chat-hf"

    def __init__(self, model_name="meta-llama/Llama-2-7b-chat-hf"):
        super().__init__()
        self.model_name = model_name
        self.is_loaded = False

    def _load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            token=hf_token,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            use_cache=True,
            token=hf_token,
        )
        self.is_loaded = True

    def inference(self, query_result: dict) -> str:
        """Chat based inference for generating visualization code

        Args:
            query_result (dict): Top 5 rows of the query result in dictionary format

        Returns:
            str: The generated code
        """
        prompt = f"""System: Use the given data to generate Python code that produces a suitable Matplotlib figure that describes the data.\
        The code should create and call a function that takes in the data and returns a matplotlib figure. You should not use non-existent matplotlib methods.
        The dataframe is saved in a pandas dataframe named result_df. Increase the figure's length and/or width if it contains several ticks.
        The data is stored in a pandas dataframe and not a csv file.

        Query Result: {query_result}

        Assistant:
        """
        prompt = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(prompt, return_tensors="pt").to(
            "cuda"
        )
        generated_ids = self.model.generate(
            inputs,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=550,
            temperature=0.95,
            do_sample=False,
            top_k=1,
            repetition_penalty=1,
            num_beams=1,
        )
        print("model generated")
        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        response = outputs[0]
        print("response returned")
        return response

    def generate_visualization(self, query_result: dict) -> str:
        """Generate visualization from the query result

        Args:
            query_result (dict): Top 5 rows of the query result in dictionary format

        Returns:
            str: The generated code
        """
        code = self.inference(query_result)
        three_dashs = [m.start() for m in re.finditer("```", code)]
        start, end = three_dashs
        df_name = "result_df"
        extracted_code = (
            code[start + 9 : end]
            .strip()
            .replace(" df", " " + df_name)
            .replace("=df", "=" + df_name)
        )
        return extracted_code

    def extract_questions(self, text: str) -> List[str]:
        """Extract questions from the given text"""
        # Define a regular expression pattern to match the questions
        pattern = r"\d+\.\s(.*?)\n\n"
        questions = re.findall(pattern, text)

        return questions

    def generate_followup_questions(self, question: str) -> List[str]:
        """Chat based inference for generating recommended follow up questions

        Args:
            query_result (str): last asked question to the model

        Returns:
            List: List of three recommended questions
        """
        if not self.is_loaded:
            self._load_model()

        prompt = f"""System: Use the given question to generate three questions you recommend to explore a database. us the provided question style.\
        to generated qestions in the same style. Try to generated questions that can be ploted by a python code to be visualy explored .\
        the provided questions is {question}
        Assistant:
        """
        prompt = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(prompt, return_tensors="pt").to(
            "cuda"
        )
        generated_ids = self.model.generate(
            inputs,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=550,
            temperature=0.95,
            do_sample=False,
            top_k=1,
            repetition_penalty=1,
            num_beams=1,
        )
        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        response = outputs[0]
        rec_questions = self.extract_questions(response)
        return rec_questions
