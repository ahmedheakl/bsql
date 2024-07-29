import pandas as pd
import warnings

class Summarizer:
    def __init__(self, n_samples:int=5, mix_unique:int=10):
        self.summary = None
        self.n_samples = n_samples
        self.mix_unique = mix_unique

    def check_type(self, dtype, value):
        """Cast value to the right type to ensure it is JSON serializable"""
        if "float" in str(dtype):
            return float(value)
        elif "int" in str(dtype):
            return int(value)
        else:
            return value

    def get_missing_data(self, column:str, df:pd.DataFrame, properties:dict, summary_str:str):
        properties["missing_values"] = df[column].isnull().sum()
        properties["missing_percentage"] = (
            properties["missing_values"] / len(df) * 100
        )
        summary_str += f"  * Number of Missing Values: {properties['missing_values']}\n"
        summary_str += f"  * Missing Values Percentage: {properties['missing_percentage']}\n"

        return properties, summary_str

    def describe_numeric(self, column:str, df:pd.DataFrame, dtype:str, properties:dict, summary_str:str):
        properties["mean"] = self.check_type(dtype, df[column].mean())
        properties["std"] = self.check_type(dtype, df[column].std())
        properties["min"] = self.check_type(dtype, df[column].min())
        properties["25th_percentile"] = self.check_type(dtype, df[column].quantile(0.25))
        properties["50th_percentile"] = self.check_type(dtype, df[column].quantile(0.50))
        properties["75th_percentile"] = self.check_type(dtype, df[column].quantile(0.75))
        properties["max"] = self.check_type(dtype, df[column].max())
        summary_str += f"  * Mean: {properties['mean']}\n"
        summary_str += f"  * STD: {properties['std']}\n"
        summary_str += f"  * Min: {properties['min']}\n"
        summary_str += f"  * 25th Percentile: {properties['25th_percentile']}\n"
        summary_str += f"  * 50th Percentile: {properties['50th_percentile']}\n"
        summary_str += f"  * 75th Percentile: {properties['75th_percentile']}\n"
        summary_str += f"  * Max: {properties['max']}\n"

        return properties, summary_str

    def describe_date(self, column:str, df:pd.DataFrame, properties:dict, summary_str:str):
        properties["min_date"] = df[column].min()
        summary_str += f"  * Min Date: {properties['min_date']}\n"
        properties["max_date"] = df[column].max()
        summary_str += f"  * Max Date: {properties['max_date']}\n"

        return properties, summary_str

    def describe_categorical(self, column:str, df:pd.DataFrame, properties:dict, summary_str:str):
        properties["categories"] = df[column].cat.categories.tolist()
        summary_str += f"  * Categories: {properties['categories']}\n"

        return properties, summary_str

    def get_samples(self, column:str, df:pd.DataFrame, properties:dict, summary_str:str):
        num_unique_values = df[column][df[column].notnull()].unique()
        if len(num_unique_values) > self.mix_unique:
            samples = (
                pd.Series(num_unique_values)
                .sample(self.n_samples)
                .tolist()
            )
            properties["example samples"] = samples
            summary_str += f"  * Column Samples: {properties['example samples']}\n"

        else:
            samples = num_unique_values.tolist()
            properties["unique values"] = samples
            summary_str += f"  * All Unique Values: {properties['unique values']}\n"

        return properties, summary_str

    def get_general_properties(self, column:str, dtype:str, df:pd.DataFrame, properties:dict, summary_str:str):
        properties["dtype"] = str(dtype)
        summary_str += f"  * Data Type: {properties['dtype']}\n"

        properties["num_unique_values"] = df[column].nunique()
        summary_str += f"  * Number of Unique Values: {properties['num_unique_values']}\n"

        return properties, summary_str

    def get_max_min_correspondence(self, column, df, properties_list, summary_str):
        properties_list[column]["corresponding_to_max"] = {}
        properties_list[column]["corresponding_to_min"] = {}
        corresponding_str = ""

        i = 1
        for num_column in df.columns:
            if pd.api.types.is_numeric_dtype(df[num_column].dtype):
                max_idx = df[num_column].idxmax()
                min_idx = df[num_column].idxmin()

                if max_idx != min_idx:
                    corresponding_max = df.iloc[max_idx]
                    corresponding_min = df.iloc[min_idx]

                    properties_list[column]["corresponding_to_max"][num_column] = {
                        "value": corresponding_max[column],
                        "max_value": corresponding_max[num_column],
                    }

                    properties_list[column]["corresponding_to_min"][num_column] = {
                        "value": corresponding_min[column],
                        "min_value": corresponding_min[num_column],
                    }

                    corresponding_str += (
                        f"    {i}) For {num_column}, the value '{corresponding_max[column]}' "
                        f"corresponds to the Max value '{corresponding_max[num_column]}'\n"
                        f"    The value '{corresponding_min[column]}' corresponds to the Min value "
                        f"'{corresponding_min[num_column]}'\n"
                    )
                    i += 1

        if corresponding_str:
            summary_str += f"  * Values corresponding to Minimum and Maximum in other numeric columns:\n"
            summary_str += corresponding_str

        return properties_list, summary_str

    def get_value_counts(self, column: str, df: pd.DataFrame, properties_list: dict, summary_str: str):
        summary_str += f"  * Value counts in the column:\n"
        num_unique_values = df[column][df[column].notnull()].unique()
        value_counts = df[column].value_counts()

        if len(num_unique_values) <= self.mix_unique:
            properties_list[column]["value_counts"] = {}
            properties_list[column]["value_counts"]["all_value_counts"] = dict(value_counts)
            for k, v in dict(value_counts).items():
                summary_str += f"    {k}: {v}\n"
        else:
            properties_list[column]["value_counts"] = {}
            top_values = dict(value_counts.head(self.mix_unique // 2))
            bottom_values = dict(value_counts.tail(self.mix_unique // 2))

            properties_list[column]["value_counts"][f"top_{self.mix_unique}_counts"] = top_values
            properties_list[column]["value_counts"][f"bottom_{self.mix_unique}_counts"] = bottom_values

            summary_str += f"    Top {self.mix_unique} values:\n"
            for k, v in top_values.items():
                summary_str += f"      {k}: {v}\n"

            summary_str += f"    Bottom {self.mix_unique} values:\n"
            for k, v in bottom_values.items():
                summary_str += f"      {k}: {v}\n"

        return properties_list, summary_str


    def summarize(self, df:pd.DataFrame, n_samples:int=5):
        """Get properties of each column in a pandas DataFrame"""
        summary_str = ""
        df = df.convert_dtypes()
        properties_list = {}

        for column in df.columns:
            summary_str += f"Column Name: {column}\n"
            dtype = df[column].dtype
            properties = {}

            # General properties for all data types
            properties, summary_str = self.get_general_properties(column, dtype, df, properties, summary_str)

            # Missing values
            properties, summary_str = self.get_missing_data(column, df, properties, summary_str)

            # Get samples
            if df[column].notnull().any():
                properties, summary_str = self.get_samples(column, df, properties, summary_str)

            # Statistical properties for numeric columns
            if pd.api.types.is_numeric_dtype(dtype):
                properties, summary_str = self.describe_numeric(column, df, dtype, properties, summary_str)

            # Date-related properties
            if pd.api.types.is_datetime64_any_dtype(dtype):
                properties, summary_str = self.describe_date(column, df, properties, summary_str)

            # Categorical properties
            if isinstance(dtype, pd.CategoricalDtype):
                properties, summary_str = self.describe_categorical(column, df, properties, summary_str)

            properties_list[column] = properties

            # Get corresponding Min/Max
            if not pd.api.types.is_numeric_dtype(df[column].dtype):
                properties_list, summary_str = self.get_max_min_correspondence(column, df, properties_list, summary_str)
                properties_list, summary_str = self.get_value_counts(column, df, properties_list, summary_str)

            summary_str += f"\n"

        return summary_str, properties_list