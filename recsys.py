
def build_preferences_prompt(user_items):
  
  persona = 'You are an investment specialist, tell me what are my preferences and explain them.'
  prompt = '''The funds I apply are (applied funds): {}.

What are the most important features for me apply in funds based on my applied funds (summarize my preferences and explain step-by-step)?
Answer:'''.format( ', '.join(user_items) )

  return [{"role":"system", "content": persona}, {"role":"user","content": prompt}]



def build_recommendation_prompt(user_items,candidate_set, preferences_completion, n_items=5):
    
    persona = f'You are an investment specialist, based on my preferences, recommend {n_items} funds to me invest and explain the recommendations'

    prompt = f'''The available funds (CANDIDATE SET) are: {', '.join(candidate_set)}.

Recommend {n_items} funds from the CANDIDATE SET based on my preferences and similarity with the funds I have.
Format: [position. recommended fund name: recommendation reason] as follow:
1. Recommended item 1: recommendation reason 1.
2. Recommended item 2: recommendation reason 2.

Answer:'''

    prefs_prompt = build_preferences_prompt(user_items)

    recsys_prompt = [
        {"role": "system", "content": persona},
        {"role": "user", "content": prefs_prompt[1]['content']},
        {"role": "assistant", "content": preferences_completion },
        {"role": "user", "content": prompt}
    ]
    return recsys_prompt


### GPT request

import time
from openai import OpenAI
import os

def ask_to_gpt(messages, gpt_model='gpt-4-turbo',max_tokens=2048,temperature=0,n_retry=5):

    client = OpenAI(
        api_key = os.getenv('OPENAI_API')
    )
    
    print("================ OpenAI API call =================")
    print(" > Model: ", gpt_model)
    print(" > temperature: ", temperature)
    print(" > max_tokens: ", max_tokens)
    print("==================== Request =====================")
    #print(json.dumps(messages, indent=2))

    while n_retry:
        try:
            print('Please wait...')
            response = client.chat.completions.create(
                  model=gpt_model,
                  messages=messages,
                  max_tokens=max_tokens,  
                  temperature=temperature,# [0-2]
                  top_p=1,                
                  frequency_penalty=0,    # [-2, 2]
                  presence_penalty=0,     # [-2,2]
                  n = 1,                  # [>1]
              )
            print("==================== Answer ======================")
    
            #display(response.choices[0].message.content)
            print("==================== Stats =======================")
            print(dict(response).get('usage'))
            print("==================================================")
            chat_completion = {
                "prompt": messages,
                "completion": response,
            }
            return chat_completion
        except Exception as e:
            print(f"An exception occurred in the GPT request: {str(e)}")
            if n_retry > 0:
                print('Trying request GPT again in few seconds!\nWait...')
            else:
                raise f"The trying limit was reached.\nExiting... with the error: {str(e)}"
            
            n_retry -= 1
            time.sleep(5) # Wait 5 seconds
            print('Trying again!')
