import streamlit as st
# import faiss
import pickle
import numpy as np
import openai
import pandas as pd



openai.api_type = "azure"
openai.api_base = "https://ai-shilpiprd0731ai141105200266.openai.azure.com/"
openai.api_version = "2024-12-01-preview"
# openai.api_key = 
deployment = "gpt-4.1-firstproject"

# # Ask model function
# from openai import AzureOpenAI


# # Initialize the AzureOpenAI client
# client = AzureOpenAI(
#     api_version=api_version,
#     azure_endpoint=endpoint,
#     api_key=subscription_key,
# )

def classify_description(description):

    prompt = (
        "You are an AI assistant that helps to categorize description into one of the three types: "
        "Fraud, Merchant Error, or Friendly Fraud.\n\n"
        "Fraud refers to unauthorized use. "
        "Merchant Error refers to overcharges, non-delivery, or double billing. "
        "Friendly Fraud refers to customer mistakes or buyer’s remorse (e.g., forgetting they subscribed).\n\n"
        f"Classify the following description:\n{description}\n\n"
        "Respond only with: Fraud, Merchant Error, or Friendly Fraud."
    )

    # response = client.chat.completions.create(
    response = openai.ChatCompletion.create(
        deployment_id = deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that classifies disputes."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=300,
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        # model=deploymen
    )
    print('this is response insidde function')

    return response.choices[0].message.content.strip()

def recommend_action(description, priority, dispute_category):

    prompt = ("You are a smart recommendation engine for a customer support team.\n\n"
        "Given the following dispute details:\n"
        f"- Description: {description}\n"
        f"- Priority: {priority}\n"
        f"- Dispute Category: {dispute_category}\n\n"
        "Please recommend:\n"
        "1. Which team should handle this (Fraud Team, Merchant Support, or General Support)?\n"
        "2. Should the case be escalated or marked routine?\n"
        "3. What immediate action should the team take."
    )

    # response = client.chat.completions.create(
    response = openai.ChatCompletion.create(
        deployment_id = deployment,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that classifies disputes."},
            {"role": "user", "content": prompt}
        ],
        max_completion_tokens=300,
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        # model=deploymen
    )
    print('this is response insidde function')

    return response.choices[0].message.content.strip()
