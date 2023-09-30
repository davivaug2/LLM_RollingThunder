# -*- coding: utf-8 -*-
"""llm_rolling_thunder_langchain_test.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VfVMSvrKAmlgOcc9yOjBNC-TITuZZhpc
"""


#!pip install

import os
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from huggingface_hub import notebook_login
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain import HuggingFacePipeline
from langchain.text_splitter import CharacterTextSplitter
import textwrap
import sys
import os

hug_write_toke = "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"

import os
os.environ['HuggingFaceHub_API_Token']= hug_write_toke
from langchain.document_loaders.pdf import UnstructuredPDFLoader

loader = UnstructuredPDFLoader('33B-1-1_R14-compressed.pdf')
documents = loader.load()

text_splitter=CharacterTextSplitter(separator='\n',
                                    chunk_size=1000,
                                    chunk_overlap=50)
text_chunks=text_splitter.split_documents(documents)



embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2',model_kwargs={'device': 'cuda'})



vectorstore=FAISS.from_documents(text_chunks, embeddings)

model = "tiiuae/falcon-7b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model)

import torch

pipe = pipeline("text-generation",
                model=model,
                tokenizer= tokenizer,
                torch_dtype=torch.bfloat16,
                device_map="auto",
                max_new_tokens = 1024,
                do_sample=True,
                top_k=10,
                num_return_sequences=1,
                eos_token_id=tokenizer.eos_token_id
                )

llm=HuggingFacePipeline(pipeline=pipe, model_kwargs={'temperature':0})

chain =  RetrievalQA.from_chain_type(llm=llm, chain_type = "stuff",return_source_documents=True, retriever=vectorstore.as_retriever())

query = "What is introduction to Liquid Penetrant Inspection?"
result=chain({"query": query}, return_only_outputs=True)
wrapped_text = textwrap.fill(result['result'], width=500)
wrapped_text

print(wrapped_text)
print(result['source_documents'])

query2 = "How can I be happy?"
result2=chain({"query": query2}, return_only_outputs=True)
wrapped_text2 = textwrap.fill(result2['result'], width=500)
wrapped_text2


file1 = open("Output.txt", "w")
file1.write(wrapped_text+'\n'+wrapped_text)
file1.close()