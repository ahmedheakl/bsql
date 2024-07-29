# Business SQL Analysis Tool

## Overview

This Business SQL Analysis Tool is a powerful, AI-driven application designed to streamline data analysis processes for business users. By leveraging natural language processing and multiple AI models, it transforms user questions into SQL queries, executes them, and provides insightful visualizations and follow-up questions.

## Features

- **Natural Language to SQL**: Converts user questions into SQL queries using the SQLCoder model.
- **Automated Data Retrieval**: Executes SQL queries on a connected database and fetches relevant data.
- **Intelligent Data Visualization**: Generates appropriate charts and graphs based on the query results.
- **AI-Powered Data Insights**: Utilizes DeepSeek model to provide statistical summaries and data descriptions.
- **Dynamic Follow-up Questions**: Generates relevant follow-up questions using the Llama 2 model to encourage deeper data exploration.
- **Interactive User Interface**: Built with Streamlit for a seamless and user-friendly experience.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite (in-memory)
- **AI Models**:
  - SQLCoder for SQL generation
  - DeepSeek for data insights
  - Llama 2 for follow-up questions
- **Data Visualization**: Vega-Lite

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/business-sql-analysis-tool.git
   ```

2. Navigate to the project directory:
   ```
   cd business-sql-analysis-tool
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Ensure you have the necessary API endpoints set up for the AI models.

## Usage

1. Place your CSV data files in the `data` folder.

2. Run the Streamlit app:
   ```
   streamlit run main_app.py
   ```

3. Open your web browser and navigate to the provided local URL (usually `http://localhost:8501`).

4. Enter your business question in natural language and explore the results!

## Configuration

- Adjust the `MAX_UNIQUE` constant to control the number of sample values displayed in the schema.
- Modify the `API` constant to point to your inference API endpoint.
- Customize the `DATASET_PATH` if you want to change the location of your data files.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- SQLCoder, DeepSeek, and Llama 2 for providing the AI models used in this project.
- Streamlit for the excellent web app framework.
- Vega-Lite for the data visualization capabilities.
