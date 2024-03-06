import os
import psycopg2
from psycopg2.extras import Json


def check_login(token):
  conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    sslmode='require'
  )

  cur = conn.cursor()
  cur.execute(f"SELECT login_count FROM mvp_access WHERE token='{token}'")

  query_result = cur.fetchall()
  if len(query_result) == 1:
    cur.execute(f"UPDATE mvp_access SET login_count = '{query_result[0][0]+1}', last_use_at=CURRENT_TIMESTAMP WHERE token='{token}'")
    conn.commit()
    cur.close()
    conn.close()
    return True
  else:
    cur.close()
    conn.close()
    return False
  
def get_users():
  conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    sslmode='require'
  )

  cur = conn.cursor()
  cur.execute(f"SELECT DISTINCT(user_id) FROM users ORDER BY user_id")
  
  query_result = cur.fetchall()

  cur.close()
  conn.close()

  return [x[0] for x in query_result]

def get_plans():
  conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    sslmode='require'
  )

  cur = conn.cursor()
  cur.execute(f"SELECT user_id, instrument_name_clean as fund_name FROM users AS u LEFT JOIN saks_funds AS f ON u.applied_fund = f.id")

  q_result_applied_users = cur.fetchall()

  #print(q_result_applied_users)

  cur.execute(f"SELECT instrument_name_clean AS fund_name FROM saks_funds")
  q_result_all_plans = cur.fetchall()
  #print(q_result_all_plans)

  cur.close()
  conn.close()

  funds_list = []
  for item in q_result_all_plans:
    funds_list.append(item[0])
  
  applied_users = dict()
  for item in q_result_applied_users:
    if item[0] not in applied_users:
      applied_users[item[0]] = [item[1]]
    else:
      applied_users[item[0]].append(item[1])
  
  return funds_list, applied_users

def new_request(user_name,user_token,client_id,
                numRec,recsys_prompt,recsys_completion,
                model):

  conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    sslmode='require'
  )

  command = f"INSERT INTO demo_stats (user_name, user_token, \
client_id, num_rec, model, recsys_prompt, recsys_completion) \
VALUES ('{user_name}','{user_token}',{client_id},{numRec},\
'{model}', { Json(recsys_prompt)}, { Json(recsys_completion) })"

#  print(command)

  cur = conn.cursor()
  cur.execute(command)
  conn.commit()

  cur.close()
  conn.close()

