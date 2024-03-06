import openai
import time
import os

def build_preferences_prompt(user_items):
  
  persona = 'You are an investment specialist, tell me what are my preferences and explain them.'
  prompt = '''The funds I apply are (applied funds): {}.

What are the most important features for me apply in funds based on my applied funds (summarize my preferences and explain step-by-step)?
Answer:'''.format( ', '.join(user_items) )

  return [{"role":"system", "content": persona}, {"role":"user","content": prompt}]



def build_recommendation_prompt(user_items,candidate_set, preferences_completion, n_items=5):
    
    persona = f'You are an investment specialist, based on my preferences, recommend {n_items} funds to me invest and explain the recommendations'

    prompt = f'''The available funds (CANDIDATE SET) are: {', '.join(candidate_set)}.

Recommend {n_items} funds from the CANDIDATE SET based on my preferences and similarity with the funds I have (Format: [no. recommended fund name: recommendation reason]).

Answer:'''

    prefs_prompt = build_preferences_prompt(user_items)

    recsys_prompt = [
        {"role": "system", "content": persona},
        {"role": "user", "content": prefs_prompt[1]['content']},
        {"role": "assistant", "content": preferences_completion },
        {"role": "user", "content": prompt}
    ]
    return recsys_prompt


def ask_to_gpt(messages,model='gpt-4-turbo-preview', max_tokens=2048,temperature=0,n_retry=5):
    openai.api_key = os.getenv('OPENAI_API')
 
    print("================ OpenAI API call =================")
    print(" > Model: ", model)
    print(" > temperature: ", temperature)
    print(" > max_tokens: ", max_tokens)
    print("==================== Request =====================")
    #print(messages)

    while n_retry:
        try:
            print('Please wait...')
            response = openai.ChatCompletion.create(
                  model=model,
                  messages=messages,
                  max_tokens=max_tokens,  # Limitando a interação
                  temperature=temperature,# Grau de liberdade/aleatoriedade [0-2]
                  top_p=1,                # Até qual probabilidade de tokens deve ser considerada
                  frequency_penalty=0,    # [-2, 2]: valores positivos penalizam a repetição de tokens
                  presence_penalty=0,     # [-2,2]: penalizam tokens que já apareceram no texto, valores positivos aumentam a probabilidade de tratar sobre novos tópicos
                  n = 1,                  # Número máximo de respostas a serem geradas (gerar opções > 1?)
              )
            print("==================== Answer ======================")
            #print(response['choices'][0]['message']['content']) # Se parâmetro 'n' mudar, haverá mais de uma posição no vetor de respostas (não apenas a 0)
            #display(Markdown(response['choices'][0]['message']['content']))
            print("==================== Stats =======================")
            print(response['usage'])
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