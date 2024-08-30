from flask import Flask, render_template, request, session, make_response, jsonify, flash, redirect, url_for
from dotenv import load_dotenv
from db_operations import check_login, get_plans, new_request
from recsys import build_preferences_prompt, build_recommendation_prompt, ask_to_gpt
import markdown

import os

application = Flask(__name__)
application.secret_key = 'RECSYS-AI-DEMO'
load_dotenv()


@application.route('/')
@application.route('/index/')
def home():
  flash('This is a demo for RecSys. Avoid misuse.',category='info')
  return render_template('login.html')


@application.route('/login/', methods=['POST'])
def login():
  try:
    #token = 'demo@recsys24'
    token = request.form['token']
    name = request.form['name']
    
    if check_login(token):
      #users_ids = get_users()
      fund_list, funds_applied = get_plans()
      users_ids = funds_applied.keys()
      session['funds_list'] = fund_list
      session['applied_list'] = funds_applied

      flash(f'Welcome, {name}!', category='success') # Send toast

      resp = make_response(render_template('main.html',users=users_ids))
      resp.set_cookie('recsys_demo_name',name)
      resp.set_cookie('recsys_demo_token',token)
      return resp

    else:
      return 'Unauthorized Access. Check your token.'
  except:
    return '<h1>Try again later or contact us.</h1>'


@application.route('/funds/', methods=['GET'])
def getUserFunds():
  userId = request.args.get('userid')
  all_funds = session['funds_list']
  if userId == None:
    return make_response( jsonify( {'list_size':len(all_funds),'available_funds': all_funds} ) )

  if userId.startswith('Select'):
    return make_response(jsonify({}))

  users_funds = session['applied_list']
  #print(f'{userId} funds: {users_funds[userId]}')
  
  candidate_set = set(all_funds) - set(users_funds[userId])

  return make_response( jsonify( { 'user_funds': users_funds[userId], 'candidate_set': list(candidate_set) } ) )


@application.route('/preferences/',methods=['GET'])
def getPreferences():
  print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
  userId = request.args.get('userid')
  numRec = request.args.get('numRec')
  print(f'New request of `{numRec}` recommendations for the user: {userId}')

  user_funds = session['applied_list'][userId]

  prefs_prompt = build_preferences_prompt(user_funds)

  try:
    prefs_completion = ask_to_gpt(prefs_prompt,os.getenv('OPENAI_MODEL'))
    completion = prefs_completion['completion'].choices[0].message.content
    answer = markdown.markdown(completion)
    
    resp = make_response( jsonify( {"preferences" : answer, 'completion': completion} ) )
    resp.set_cookie('recsys_demo_selected_user',userId)
    resp.set_cookie('recsys_demo_numrec',numRec)
  except Exception as e:
    print(f'Error in ASK to GPT about user preferences: {str(e)}')
    resp = make_response( jsonify( { } ) )
  
  return resp



@application.route('/recommendation/',methods=['POST'])
def getRecommendation():
  data = request.get_json()
  
  prefsCompletion = data['prefsCompletion']
  
  userId = request.cookies.get('recsys_demo_selected_user')
  numRec = request.cookies.get('recsys_demo_numrec')
  name = request.cookies.get('recsys_demo_name')
  token = request.cookies.get('recsys_demo_token')

  all_funds = session['funds_list']
  users_funds = session['applied_list'][userId]
  candidate_set = set(all_funds) - set(users_funds)


  recsys_prompt = build_recommendation_prompt(users_funds,candidate_set, prefsCompletion, numRec)

  try:
    print()
    recsys_completion = ask_to_gpt(recsys_prompt,os.getenv('OPENAI_MODEL'))
    completion = recsys_completion['completion'].choices[0].message.content
    answer = markdown.markdown(completion)
    
    resp = make_response( jsonify( {"recommendation" : answer, 'completion': completion} ) )
    
    # Save the request into database
    new_request(name,token,userId,numRec,recsys_completion['prompt'],
                recsys_completion['completion'],os.getenv('OPENAI_MODEL'))

  except Exception as e:
    print(f'Error requesting recommendation to GPT: {str(e)}')
    resp = make_response( jsonify( { } ) )
  
  return resp


if __name__ == "__main__":
  load_dotenv()
  print('Starting server')
  application.run(debug=True)
