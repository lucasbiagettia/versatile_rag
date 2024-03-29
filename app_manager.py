import os
import time
from src.faiss_embedder import EmbeddingsProvider
from src.qa_chain import QuestionAnsweringChain
from src.embedding_model_manager import EmbeddingModel
from src.data_processor import TxtProcessor
from src.db_manager import PosgresManager

class AppManager:

    _instance = None  

    def __new__(cls, db_name):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name):
        if self._initialized:
            return
        self._initialized = True

        self.db_manager = PosgresManager(db_name)
        self.db_manager.create_table_with_id_name()
        self.knowledge_base = None
        self.embeddings = None

    def get_entry_name(self, document,model_name,splitter):
        table_name = " - ".join([document, model_name, splitter])
        return table_name
    def get_embed_table_name(self, index):
        return "embed" + str(index)

    def add_document(self, document, embedding_model_name, splitter):
        file_name, file_extension = os.path.splitext(document.name)
        self.db_manager.insert_tabular_data(file_name, embedding_model_name, splitter)
        index = self.db_manager.get_index_by_name(file_name, embedding_model_name, splitter)
        embedding_model = EmbeddingModel(embedding_model_name)
        data_processor = TxtProcessor(document, embedding_model)
        df = data_processor.get_processed_data()
        dim = embedding_model.get_embedding_dim()
        table_name = self.get_embed_table_name(index)
        self.db_manager.create_table(table_name, dim)
        self.db_manager.insert_data(df, table_name)
    
    def make_question(self, document, question, embedding_model_name, inference_model_name):
        table_name = self.get_embed_table_name(document[0]) 
        embedding_model = EmbeddingModel(embedding_model_name)
        embedding = embedding_model.get_embedding(question)
        sim_docs = self.db_manager.get_similar_docs(embedding, 5, table_name)
        inference_model = QuestionAnsweringChain(inference_model_name)
        ans = inference_model.answer_question(question, sim_docs)
        return ans

    def add_document_using_faiss(self, document, embedding_model_name, splitter):
        embed_provider = EmbeddingsProvider( embedding_model_name, document)
        while not embed_provider.initialized:
            time.sleep(100)
        self.embeddings, self.knowledge_base = embed_provider.get_embeddings()

    def make_question_using_faiss(self, document, question, embedding_model_name, inference_model_name):
        documents = self.knowledge_base.similarity_search(question, k=5)
        sim_docs = [document.page_content for document in documents]
        inference_model = QuestionAnsweringChain(inference_model_name)
        ans = inference_model.answer_question(question, sim_docs)
        return ans





    def get_all_documents(self):
        entries = self.db_manager.get_all_entries()
        return entries