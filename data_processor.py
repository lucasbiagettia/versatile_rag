import csv
import json
import tqdm

class DataProcessor:
    @staticmethod
    def order_data(csv_file, column_names):
        result_list = []

        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Read the header

            if all(column in header for column in column_names):
                for i, row in enumerate(csv_reader):

                    values = [row[header.index(column)] for column in column_names]
                    result_list.append(tuple(values))
            else:
                raise Exception("One or more specified columns are not present in the file.")

        return result_list

    @staticmethod
    def split_into_batches(text, words_per_batch=20):
        embeds =[]
        words = text.split()
        for i in range(0, len(words), words_per_batch):
            batch = " ".join(words[i:i+words_per_batch])
            embeds.append(batch)
        return embeds

    @staticmethod
    def add_field_to_json(json_str, value):
        json_data = json.loads(json_str)
        json_data['chunk'] = value
        del json_data['link']
        del json_data['author']
        del json_data['metadata']
        return json.dumps(json_data).replace('"', "'")



    @staticmethod
    def data2vector2(data, vectorizer):
        result_list = []
        for metadata, text in tqdm.tqdm(data, desc="Processing data"):
            chunks = DataProcessor.split_into_batches(text)  # Use the class name
            for chunk in chunks:
                result_list.append((DataProcessor.add_field_to_json(metadata, chunk), vectorizer.get_embedding(chunk)))  # Use the class name

        return result_list
