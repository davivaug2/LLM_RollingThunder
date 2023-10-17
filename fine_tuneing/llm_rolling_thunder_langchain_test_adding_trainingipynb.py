# -*- coding: utf-8 -*-
"""llm_rolling_thunder_langchain_test_adding_trainingipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1VHsFL5VjdmJHODRfughY4nSkAWz2jgCE



Causal language modeling: the model has to predict the next token in the sentence (so the labels are the same as the inputs shifted to 
the right). To make sure the model does not cheat, 
it gets an attention mask that will prevent it to access the tokens after token i when trying to predict the token i+1 in the sentence.

"""

# DAVID VAUGHAN R 1166390,Roman Tait, Tucker Hoffnagle,Karlton Hall,Harrison Whitworth
# Rolling Thunder
# LLM for  Lockheed Martin

"""https://github.com/davivaug2/LLM_RollingThunder

known problem: Google colab free will run out of GPU memory if ask's too many question or certain questions. Run of Texas Tech High Performance Computeing Center matador with 1/2 GPU's to get around this issue

# **TO DO**
## Retrieval-augmented generation (RAG). Should return name of pdf not just page.Should not answer certain question.Should answer certain questions better
# Add a fine tuner. Find or make training data.
# somone should work on  some frontend

Maybe to Do
try different vector databases, embeddings,falcon 7b vs falcon instruct, maybe falcon 40B

# Next code Section is downloading all dependcies for Google Colab. Not Neccesarry on HPCC
"""

"""# Next code Section is importing depency on python
"""

from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
# from langchain.embeddings import HuggingFaceEmbeddings
 # changed
from langchain.embeddings import (
    #LlamaCppEmbeddings,
    HuggingFaceEmbeddings,
    SentenceTransformerEmbeddings
)

from langchain.chains import RetrievalQA
from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders.pdf import UnstructuredPDFLoader
 # changed
from langchain.document_loaders import (
    PyPDFLoader,
    DataFrameLoader,
    GitLoader
  )
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from huggingface_hub import notebook_login
from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForCausalLM
from langchain import HuggingFacePipeline
from langchain.text_splitter import CharacterTextSplitter

import textwrap
import sys
import torch # pipe
import textwrap
import os
NOT_DOWNLOADED_PDF = False
NODE = 1
cpu_per_node = 40
NUM_PROC = NODE * cpu_per_node

# for importing LLM from Huggingface
hug_write_toke = "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"
os.environ['HuggingFaceHub_API_Token']= hug_write_toke
from huggingface_hub import login

login(hug_write_toke)

"""# Next code Section is importing the PDF.Got some of the code from https://dev.to/seraph776/download-pdf-files-using-python-4064"""

import requests
def download_pdf_file(url: str) -> bool:
    """Download PDF from given URL to local directory.

    :param url: The url of the PDF file to be downloaded
    :return: True if PDF file was successfully downloaded, otherwise False.
    """

    # Request URL and get response object
    response = requests.get(url, stream=True)

    # isolate PDF filename from URL
    pdf_file_name = os.path.basename(url)
    if response.status_code == 200:
        # Save in current working directory
        filepath = os.path.join(os.getcwd(), pdf_file_name)
        with open(filepath, 'wb') as pdf_object:
            pdf_object.write(response.content)
            print(f'{pdf_file_name} was successfully saved!')
            return True
    else:
        print(f'Uh oh! Could not download {pdf_file_name},')
        print(f'HTTP response status code: {response.status_code}')
        return False

# RAW FILE
# https://githubraw.com/
pf1 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-20-1_1.pdf'
pf2 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-20-2.pdf'
pf3 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-20-3.PDF'
pf4 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-20-9.pdf'
pf5 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-25-107.pdf'
pf6 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-25-195.pdf'
pf7 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-25-4.pdf'
pf8 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-35A-39_1.PDF'
pf9 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-35D-54.pdf'
pf10 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-5-15.PDF'
pf11 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-5-18.pdf'
pf12 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-5-19.pdf'
pf13 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-5-1_1.PDF'
pf14 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/00-5-3.pdf'
pf15 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/1-1-300.PDF'
pf16 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/33-1-37-2.pdf'
pf17 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/33-1-37-3.pdf'
pf18 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/33-1-37-4.pdf'
pf19 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/33B-1-1_R14-compressed.pdf'
pf20 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-021019-1-1B-50.pdf'
pf21 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-082216-00-80G-1.pdf'
pf22 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-082416-00-85B-3.pdf'
pf23 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-082416-1-1A-1.pdf'
pf24 ='https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-082516-33-1-37-1.pdf'
pf25 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-112818-00-85A-03-1.pdf'
pf26 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-131009-054.PDF'
pf27 = 'https://cdn.githubraw.com/davivaug2/LLM_RollingThunder/main/folder1/AFD-191106-00-5-16.pdf'
list_pdf = {pf1,pf2,pf3,pf4,pf5,pf6,pf7,pf8,pf9,pf10,pf11,pf12,pf13,pf14,pf15,pf16,pf17,pf18,pf19,pf20,pf21
            ,pf22,pf23,pf24,pf25,pf26,pf27}
if(NOT_DOWNLOADED_PDF == True):
   for pd in list_pdf:
      download_pdf_file(pd)


name1 = '00-20-1_1.pdf'
name2 = '00-20-2.pdf'
name3 = '00-20-3.PDF'
name4 = '00-20-9.pdf'
name5 = '00-25-107.pdf'
name6 = '00-25-195.pdf'
name7 = '00-25-4.pdf'
name8 = '00-35A-39_1.PDF'
name9 = '00-35D-54.pdf'
name10 = '00-5-15.PDF'
name11 = '00-5-18.pdf'
name12 = '00-5-19.pdf'
name13 = '00-5-1_1.PDF'
name14 = '00-5-3.pdf'
name15 = '1-1-300.PDF'
name16 = '33-1-37-2.pdf'
name17 = '33-1-37-3.pdf'
name19 = '33-1-37-4.pdf'
name19 = '33B-1-1_R14-compressed.pdf'
name20 = 'AFD-021019-1-1B-50.pdf'
name21 = 'AFD-082216-00-80G-1.pdf'
name22 = 'AFD-082416-00-85B-3.pdf'
name23 = 'AFD-082416-1-1A-1.pdf'
name24 = 'AFD-082516-33-1-37-1.pdf'
name25 = 'AFD-112818-00-85A-03-1.pdf'
name26 = 'AFD-131009-054.PDF'
name27 = 'AFD-191106-00-5-16.pdf'
list_name = {name1,name2,name3,name4,name5,name6,name7 ,name8,name9,name10,name11,name12 ,
             name13 ,name14 ,name15 ,name16,name17 ,name19 ,name19 ,name20 ,name21 ,name22,name23,name24,name25 ,name26 ,name27}

"""# Next code Section is for takeing the PDF's and vectorize them for a database. Got some of the code from https://colab.research.google.com/drive/1Z9R5wSF9tF_4bxYSXVKmOHM2gu7B7QVQ#scrollTo=NvEsaUTrReEG"""



def get_pdf_splits(pdf_file):
  """Function takes in the pdf data and returns the
  splits so for further processing can be done."""

  loader = PyPDFLoader(pdf_file)
  pages = loader.load_and_split()

  textSplit = RecursiveCharacterTextSplitter(chunk_size=150,
                                             chunk_overlap=15,
                                             length_function=len)
  doc_list = []
  #Pages will be list of pages, so need to modify the loop
  for pg in pages:
    pg_splits = textSplit.split_text(pg.page_content)
    doc_list.extend(pg_splits)

  return doc_list



"""# IMPLEMENT THIS
## https://colab.research.google.com/github/huggingface/notebooks/blob/main/examples/language_modeling.ipynb
"""

# !pip install pypdf

'''
from pypdf import PdfWriter

merger = PdfWriter()

for pdf in list_name:
    merger.append(pdf)

merger.write("merged.pdf")
merger.close()
'''

#pdf_docs = get_pdf_splits("merged.pdf")

# add all document chinks
all_doc = []
for name in list_name:
  pdf_docs = get_pdf_splits(name)
  all_doc.append(pdf_docs)

flat_list = [item for sublist in all_doc for item in sublist]

import random
random.shuffle(flat_list)
#chunk_size = 600
#chunked_list = [flat_list[i:i+chunk_size] for i in range(0, len(flat_list), chunk_size)]
#print(len(chunked_list))
length = len(flat_list) // 5
test_set, train_set = flat_list[:length], flat_list[length:]

print(len(test_set))
print(len(train_set))

######
model_name = "tiiuae/falcon-7b-instruct"
#
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(examples):
    return tokenizer(examples["text"])

from datasets import load_dataset

print(len(train_set))
with open('train.txt', 'w') as outfile:
  outfile.write('\n'.join(str(i) for i in train_set))
outfile.close()
print(len(test_set))
with open('test.txt', 'w') as outfile:
  outfile.write('\n'.join(str(i) for i in test_set))
outfile.close()

dataset = load_dataset('text', data_files={'train': ['train.txt'], 'validation': 'test.txt'})

tokenized_datasets = dataset.map(tokenize_function, batched=True, num_proc=NUM_PROC, remove_columns=["text"])

block_size = 128

def group_texts(examples):
    # Concatenate all texts.
    concatenated_examples = {k: sum(examples[k], []) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    # We drop the small remainder, we could add padding if the model supported it instead of this drop, you can
        # customize this part to your needs.
    total_length = (total_length // block_size) * block_size
    # Split by chunks of max_len.
    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()
    return result

lm_datasets = tokenized_datasets.map(
    group_texts,
    batched=True,
    batch_size=1000,
    num_proc=NUM_PROC,
)
#lm_datasets = lm_datasets.shuffle(seed=42).select([i for i in range(1000)])  # Adjust the number of examples
from transformers import AutoModelForCausalLM ,BitsAndBytesConfig
# MAYBE CHAGE AutoModelForCausalLM to AutoModelForQuestionAnswering ?
#model_to_be_modified = AutoModelForCausalLM.from_pretrained(model_name,device_map ='auto',trust_remote_code=True)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    llm_int8_enable_fp32_cpu_offload=True
)
bnb_config2 = BitsAndBytesConfig(
    llm_int8_enable_fp32_cpu_offload=True
)
"""
model_to_be_modified = AutoModelForCausalLM.from_pretrained(
    model_name,device_map="auto"
)
model_to_be_modified = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
model_to_be_modified = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    trust_remote_code=True
)

"""
model_to_be_modified = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config2,
    device_map="auto",
    trust_remote_code=True
)




from transformers import Trainer, TrainingArguments

"""
training_args = TrainingArguments(
    f"{model_name}-finetuned_falcon_airforce_pdf",
    evaluation_strategy = "epoch",
    learning_rate=2e-5,
    weight_decay=0.01,
    push_to_hub=True,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=2,
)
    #
    #
"""
training_args = TrainingArguments(
    f"{model_name}-finetuned_falcon_airforce_pdf",
    evaluation_strategy = "epoch",
    learning_rate=2e-5,
    weight_decay=0.01,
    push_to_hub=True,
)


    #
    #
"""
trainer = Trainer(
    model=model_to_be_modified,
    args=training_args,
    train_dataset=lm_datasets["train"],
    eval_dataset=lm_datasets["validation"],
    gradient_accumulation_steps=2,
    max_split_size_mb=64,
)
"""
trainer = Trainer(
    model=model_to_be_modified,
    args=training_args,
    train_dataset=lm_datasets["train"],
    eval_dataset=lm_datasets["validation"],
    
)

    #
# torch.cuda.set_per_process_memory_fraction(0.8)
trainer.train()

import math
eval_results = trainer.evaluate()
print(f"Perplexity: {math.exp(eval_results['eval_loss']):.2f}")



"""# Next code Section is loading LLM and vector database and running LLM. Got some of the code from  
https://medium.com/@nageshmashette32/building-a-document-based-question-answering-system-with-langchain-using-open-source-llm-model-3b49c0d4a8b8
"""

print("DONE")

