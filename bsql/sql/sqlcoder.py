"""Implementation for SQLCoder model"""

import re

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from bsql.model import Model


class SQLCoder(Model):
    """SQLCoder model"""

    model_name = "defog/sqlcoder-7b-2"

    def _load_model(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
            use_cache=True,
        )

    def inference(self, question: str, schema: str) -> str:
        """Run model inference"""
        self.load_model()
        prompt = """### Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
This query will run on a database whose schema is represented in this string:
{schema}
### SQL
Given the database schema, here is the SQL query that answers `{question}`:
```sql
""".format(
            question=question, schema=schema
        )
        assert self.tokenizer, "Please load the model first"
        assert self.model, "Please load the model first"
        eos_token_id = self.tokenizer.eos_token_id
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda")
        generated_ids = self.model.generate(
            **inputs,
            num_return_sequences=1,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id,
            max_new_tokens=400,
            do_sample=False,
            num_beams=1,
        )
        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

        def postgres_to_sqlite(query: str) -> str:
            substitutions = [
                (r"ilike", "LIKE"),
                (r"serial\s*$", "INTEGER PRIMARY KEY AUTOINCREMENT"),
                (r"start\s+with\s+(\d+)", "CHECK (id >= \\1)"),
            ]

            for pattern, replacement in substitutions:
                query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

            return query

        postgres_query = outputs[0].split("```sql")[-1].rstrip("```")
        query = postgres_to_sqlite(postgres_query)
        return query
