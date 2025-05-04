import numpy as np
# from sentence_transformers import SentenceTransformer
import openai
import pandas as pd

openai.api_type = "azure"
openai.api_base = "https://ai-shilpiprd0731ai141105200266.openai.azure.com/"
openai.api_version = "2024-12-01-preview"
openai.api_key = "9KVVf4ugt3DVbbP8E1fh8LHoEdCRgZz3xE9T17p7RNMBHNVAcQ3gJQQJ99BDACHYHv6XJ3w3AAAAACOGf1UT"
deployment = "gpt-4.1-firstproject"

def state_eligibility(applicant_income, no_dependables, additional_income, loan_period, cibil, loan_amount):

    prompt = (
        "You are a smart loan approval engine for customers.\n\n"
        "Given the following customer details:\n"
        f"- The amount of money that the user wants to take loan for is: {loan_amount}\n"
        f"- Applicant Income (amount earned by the loan applier): {applicant_income}\n"
        f"- No. of Dependables (number of people in the applicant's family): {no_dependables}\n"
        f"- Additional Income (other income sources): {additional_income}\n"
        f"- Loan Period (in months): {loan_period}\n"
        f"- CIBIL Score (credit score out of 900): {cibil}\n\n"
        "Please recommend if the loan should get approved or not. "
        "If Approved, just respond with one word: Approved. Otherwise, First respond with Not Approved, then also explain the minimum eligibility criteria for loan to get passed"
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