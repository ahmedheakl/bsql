text2code_template = "### Instruction: given the dataframe called {} with the following column and there respective types: {} and {} rows.generate a relevant plot using matplotlib which can be a count plot, pie chart, or a histogram. generate only the code without any other text. plot descriptive data plots like histograms if the column is of type float, and pie charts and countplots if the column types are categorical.generate only the code for only one plot. ### Response:"
# """<|im_start|>system
# Your job is to provide a code to visualize the data that answer the user's question. Your code should be a function plot(data: pd.DataFrame) that takes in a pandas DataFrame as an argument and returns a matplotlib plot. You MUST return a full program. DO NOT include any preamble text. Do not include explanations or prose.<|im_end|>
# <|im_start|>user
# ### Question:
# {question_small}

# ### Data Summary:
# {data_summary[1]}
# <|im_end|>
# <|im_start|>assistant"""
