from flask import Flask, render_template, request, session, make_response, jsonify, flash, redirect, url_for
from dotenv import load_dotenv
from db_operations import check_login, get_plans, new_request
from recsys import build_preferences_prompt, build_recommendation_prompt, ask_to_gpt
import markdown

application = Flask(__name__)
application.secret_key = 'SAKS-IA-MVP'
load_dotenv()


test_preference_completion = {
    "completion": {
      "choices": [
        {
          "finish_reason": "stop",
          "index": 0,
          "logprobs": "null",
          "message": {
            "content": "Based on your applied funds\u2014Templeton Global Balanced, JPM US Bond, and PIMCO Low Average Duration\u2014it's possible to deduce several key investment preferences and priorities you might have. Let's break down these preferences step-by-step:\n\n### 1. Diversification\n\n- **Global Exposure**: By investing in the Templeton Global Balanced Fund, you're indicating a preference for global diversification, not just across different asset classes but also across various geographical regions. This fund typically invests in a mix of global equities and fixed income securities, aiming to provide growth while managing risk.\n- **Asset Class Diversification**: Your choice of funds shows an interest in both stocks (equity) and bonds (fixed income), which can help in spreading risk. The balanced nature of the Templeton fund, combined with specific bond funds (JPM US Bond and PIMCO Low Average Duration), suggests you value a mix of asset classes to achieve a balanced risk-return profile.\n\n### 2. Risk Management\n\n- **Balanced Approach**: The Templeton Global Balanced Fund inherently aims for a balance between growth (through equities) and income (through bonds), which can be seen as a strategy to manage risk while seeking returns. This indicates a moderate risk tolerance where you're looking for growth but with a cushion against market volatility.\n- **Quality and Duration in Bonds**: By choosing the JPM US Bond and PIMCO Low Average Duration funds, you're focusing on US bonds, which are generally considered safe, especially if they are of high credit quality. The emphasis on \"Low Average Duration\" with the PIMCO fund suggests a strategy to minimize interest rate risk, as shorter-duration bonds are less sensitive to changes in interest rates compared to longer-duration bonds.\n\n### 3. Focus on Stability and Income\n\n- **Income Generation**: Bond funds like JPM US Bond and PIMCO Low Average Duration are typically sought after for their potential to generate income, which can be an important aspect if you're looking for steady cash flows from your investments.\n- **Stability**: The inclusion of bond funds, especially one with a low average duration, indicates a preference for stability and preservation of capital. Bonds, particularly short-term and high-quality ones, tend to offer lower volatility compared to stocks, which can be appealing if you prioritize capital preservation.\n\n### 4. Strategic Interest Rate Positioning\n\n- **Interest Rate Sensitivity**: By choosing a fund with a low average duration (PIMCO Low Average Duration), you're likely concerned about the impact of rising interest rates on your portfolio. This shows a strategic approach to interest rate risk, as lower-duration bonds have less price volatility in response to interest rate changes.\n\n### Summary of Your Preferences\n\nIn summary, your applied funds suggest that you value a diversified investment approach that balances growth with income and stability. You seem to have a moderate risk tolerance, with a strategic focus on managing interest rate risk and generating income while also seeking global exposure to equities and bonds. Your choices reflect a nuanced understanding of how different investment strategies can work together to achieve a balanced and diversified portfolio.",
            "role": "assistant"
          }
        }
      ],
      "created": 1709648062,
      "id": "chatcmpl-8zPqgEQkDE7cojAr9nFGipNE4wCc8",
      "model": "gpt-4-0125-preview",
      "object": "chat.completion",
      "system_fingerprint": "fp_00ceb2df5b",
      "usage": {
        "completion_tokens": 629,
        "prompt_tokens": 89,
        "total_tokens": 718
      }
    },
    "prompt": [
      {
        "content": "You are an investment specialist, tell me what are my preferences and explain them.",
        "role": "system"
      },
      {
        "content": "The funds I apply are (applied funds): TEMPLETON GLOBAL BALANCED , JPM US BOND , PIMCO LOW AVERAGE DURATION .\n\nWhat are the most important features for me apply in funds based on my applied funds (summarize my preferences and explain step-by-step)?\nAnswer:",
        "role": "user"
      }
    ]
  }

test_recommendation_completion = {
  'prompt': [{'role': 'system', 'content': 'You are an investment specialist, based on my preferences, recommend 15 funds to me invest and explain the recommendations'}, {'role': 'user', 'content': 'The funds I apply are (applied funds): TEMPLETON GLOBAL BALANCED , JPM US BOND , PIMCO LOW AVERAGE DURATION .\n\nWhat are the most important features for me apply in funds based on my applied funds (summarize my preferences and explain step-by-step)?\nAnswer:'}, {'role': 'assistant', 'content': "Based on your applied funds—Templeton Global Balanced, JPM US Bond, and PIMCO Low Average Duration—it's possible to infer several key investment preferences and priorities you might have. Let's break down these preferences step-by-step:\n\n### 1. Diversification\n\n**Preference Explanation:**\n- **Geographic Diversification:** By investing in the Templeton Global Balanced Fund, you're indicating a preference for global exposure, diversifying across different countries and regions to mitigate risk associated with any single market.\n- **Asset Class Diversification:** The mix of equity and fixed income in the Templeton Global Balanced Fund, along with specific bond funds like JPM US Bond and PIMCO Low Average Duration, shows a balanced approach to asset allocation. This mix helps in achieving a balance between growth (through equities) and income/stability (through bonds).\n\n### 2. Risk Management\n\n**Preference Explanation:**\n- **Balanced Fund:** The Templeton Global Balanced Fund typically invests in a mix of stocks and bonds, which can be seen as a strategy to manage risk through diversification. Balanced funds aim to reduce volatility compared to pure equity funds.\n- **Low Average Duration Bonds:** By choosing the PIMCO Low Average Duration fund, you're likely focused on minimizing interest rate risk. Lower duration bonds are less sensitive to changes in interest rates, which can be a conservative approach in uncertain or rising rate environments.\n\n### 3. Income Generation\n\n**Preference Explanation:**\n- **Bond Funds:** Both the JPM US Bond and PIMCO Low Average Duration funds indicate a preference for income generation through fixed income investments. Bonds provide regular interest payments, which can be an important feature for investors seeking steady income.\n\n### 4. Quality and Stability\n\n**Preference Explanation:**\n- **Reputable Fund Managers:** Investing in funds managed by well-known firms like Templeton, JPMorgan, and PIMCO suggests a preference for established, reputable managers. These firms have extensive research capabilities and a history of managing investments through various market conditions.\n- **US Bond Exposure:** The choice of JPM US Bond indicates a tilt towards investments perceived as relatively safe, given the stability and liquidity of the US bond market. This can be seen as a preference for quality and lower default risk in the fixed income portion of your portfolio.\n\n### 5. Flexibility and Liquidity\n\n**Preference Explanation:**\n- **Low Average Duration & Balanced Fund:** These choices suggest a preference for maintaining some level of liquidity and flexibility. Lower duration bonds can be more easily adjusted in response to changing market conditions, and balanced funds offer the flexibility to rebalance between stocks and bonds internally.\n\n### Summary\n\nYour applied funds suggest that you value a diversified investment approach that balances growth with income and stability. You seem to prioritize risk management through asset and geographic diversification, and you prefer investments that offer a mix of income generation, quality, and some level of liquidity and flexibility. Your choices reflect a cautious but strategic approach to investing, aiming to achieve a balanced risk-reward profile."}, {'role': 'user', 'content': 'The available funds (CANDIDATE SET) are: BGF US FLEXIBLE EQUITY , FRANKLIN INNOVATION , MFS MERIDIAN UK EQUITY , MFS MERIDIAN GLOBAL INTRINSIC VALUE , BSF STYLE ADVANTAGE , BGF WORLD GOLD , BGF NEXT GENERATION TECHNOLOGY , INVESCO GLOBAL CONVERTIBLE , JPM GLOBAL MACRO , JPM GLOBAL STRATEGIC BOND , NEUBERGER BERMAN NEXT GENERATION MOBILITY , INVESCO RESPONSIBLE JAPANESE EQUITY VALUE DISCOVER , PIMCO INCOME , JPM GLOBAL BOND OPPORTUNITIES , MFS MERIDIAN PRUDENT CAPITAL , SCHRODER ISF QEP GLOBAL EMERGING MARKETS , JPM US SMALL CAP GROWTH , PIMCO DIVERSIFIED INCOME , INVESCO PAN EUROPEAN EQUITY INCOME , SCHRODER ISF GLOBAL CLIMATE CHANGE EQUITY , PIMCO TRENDS MANAGED FUTURES STRATEGY , AB RMB INCOME PLUS PORTFOLIO , SCHRODER ISF GLOBAL EQUITY YIELD , TEMPLETON LATIN AMERICA , JANUS HENDERSON GLOBAL SMALLER COMPANIES , JPM ASIA PACIFIC INCOME , BGF WORLD REAL ESTATE SECURITES , NEUBERGER BERMAN EMERGING MARKETS EQUITY , AB FCP I - EMERGING MARKETS GROWTH PORTFOLIO , JPM GLOBAL NATURAL RESOURCES , SCHRODER ISF EUROPEAN LARGE CAP , JPM GREATER CHINA , TEMPLETON EASTERN EUROPE , BGF EURO SHORT DURATION BOND , BGF ESG MULTI-ASSET , INVESCO PAN EUROPEAN EQUITY , JPM US SELECT EQUITY PLUS , JPM LATIN AMERICA EQUITY , BSF SYSTEMATIC ESG WORLD EQUITY , INVESCO ASIAN FLEXIBLE BOND , JPM US SUSTAINABLE EQUITY , AB FCP I - SHORT DURATION BOND PORTFOLIO , INVESCO GLOBAL CONSUMER TRENDS , JPM GLOBAL MACRO OPPORTUNITIES , AB SICAV I - SUSTAINABLE US THEMATIC PORTFOLIO , SCHRODER ISF GLOBAL TARGET RETURN , JPM GLB REAL ESTATE SECURITIES USD , FRANKLIN GLOBAL REAL ESTATE , JPM EMERGING MARKETS STRATEGIC BOND , BSF GLOBAL REAL ASSET SECURITIES , FRANKLIN MUTUAL GLB DISCOVERY , INVESCO DEVELOPED SMALL AND MID-CAP EQUITY , JPM RUSSIA , MORGAN STANLEY INVESTMENT FUNDS GLOBAL CORE EQUITY , SCHRODER ISF INDIAN EQUITY , BGF CHINA , BGF ASIAN MULTI-ASSET INCOME , NEUBERGER BERMAN SUSTAINABLE EMERGING MARKET CORPORT DEBT , BSF SYSTEMATIC GLOBAL EQUITY , JPM BRAZIL EQUITY , MORGAN STANLEY INVESTMENT FUNDS GLOBAL INFRASTRUCTURE , JPM GLOBAL VALUE , SCHRODER ISF US SMALL & MID-CAP EQUITY , BGF ESG EMERGING MARKETS BOND , BSF SYSTEMATIC GLOBAL LONG/SHORT EQUITY , JPM INDIA , SCHRODER ISF GLOBAL CREDIT INCOME , SCHRODER ISF ASIAN CREDIT OPPORTUNITIES , BGF CHINA FLEXIBLE EQUITY , MORGAN STANLEY INVESTMENT FUNDS INDIAN EQUITY , BGF GLOBAL GOVERNMENT BOND , SCHRODER ISF GLOBAL CORPORATE BOND, AB SICAV I - EUROPEAN EQUITY PORTFOLIO , BSF MANAGED INDEX PORTFOLIOS - GROWTH , BGF DYNAMIC HIGH INCOME , TEMPLETON EUROLAND , MORGAN STANLEY INVESTMENT FUNDS INTERNATIONAL EQUITY, INVESCO PAN EUROPEAN SMALL CAP EQUITY , JPM GLOBAL CORPORATE BOND DURATION , SCHRODER ISF GLOBAL RECOVERY , JPM GLOBAL SELECT EQUITY , BGF GLOBAL EQUITY INCOME , FRANKLIN INDIA , AB SHORT DURATION HIGH YIELD , MFS MERIDIAN US VALUE , JPM US SELECT EQUITY , NEUBERGER BERMAN MULTI ASSET INCOME  , SCHRODER ISF GLOBAL CITIES , SCHRODER ISF GLOBAL GOLD , BGF US GOVERNMENT MORTGAGE IMPACT , FRANKLIN TECHNOLOGY , PIMCO STOCKS PLUS , AB FCP I - GLOBAL EQUITY BLEND PORTFOLIO , INVESCO MACRO ALLOCATION STRATEGY , INVESCO BALANCED-RISK ALLOCATION , JPM GLOBAL SOCIALLY RESPONSIBLE , BSF GLOBAL ABSOLUTE RETURN BOND , TEMPLETON SHARIAH GLOBAL EQUITY FUND , AB FCP I - AMERICAN INCOME PORTFOLIO , JPM GLOBAL INCOME , SCHRODER ISF GLOBAL DIVERSIFIED GROWTH , SCHRODER ISF ASIAN EQUITY YIELD , INVESCO US HIGH YIELD BOND , BGF ESG GLOBAL BOND INCOME , JPM AFRICA EQUITY , INVESCO USD ULTRA-SHORT TERM DEBT , MFS MERIDIAN EUROPEAN VALUE , PIMCO TOTAL RETURN BOND , INVESCO EURO EQUITY , MORGAN STANLEY INVESTMENT FUNDS GLOBAL PROPERTY , PIMCO GLOBAL REAL RETURN , BSF MANAGED INDEX PORTFOLIOS - CONSERVATIVE , NEUBERGER BERMAN SHORT DURATION HIGH YIELD SDG ENGAGEMENT , AB EMERGING MARKETS VALUE PORTFOLIO , INVESCO GLOBAL HIGH YIELD SHORT TERM BOND FUND , AB LOW VOLATILITY EQUITY PORTFOLIO , JPM GLOBAL DIVIDEND , TEMPLETON GLOBAL , PIMCO GLOBAL LOW DURATION REAL RETURN , NEUBERGER BERMAN GLOBAL REAL ESTATE SECURITIES , JPM KOREA EQUITY , JPM EMERGING EUROPE EQUITY , MORGAN STANLEY INVESTMENT FUNDS LATIN AMERICAN EQUITY , BGF INDIA , FRANKLIN GOLD & PRECIOUS METALS , AB GLOBAL CORE EQUITY PORTFOLIO , LOW DURATION INCOME , BSF EMERGING MARKETS FLEXI DYNAMIC BOND , JPM JAPAN EQUITY , TEMPLETON GLOBAL BOND (EURO) , FRANKLIN NEXTSTEP MODERATE , FRANKLIN GLOBAL GROWTH , JPM INCOME , BLACKROCK SUSTAINABLE FIXED INCOME STRATEGIES , FRANKLIN NEXTSTEP GROWTH , MFS MERIDIAN FUNDS CONTRARIAN VALUE , SCHRODER ISF EMERGING MARKETS DEBT ABSOLUTE RETURN, JPM DIVERSIFIED RISK , BGF FUTURE OF TRANSPORT , BGF ASIAN DRAGON , AB FCP I - GLOBAL VALUE PORTFOLIO , JPM GLOBAL CONVERTIBLES , MFS MERIDIAN FUNDS U.S. GROWTH , BGF WORLD TECHNOLOGY , JPM US SHORT DURATION BOND , SCHRODER ISF CHINA OPPORTUNITIES , JPM THEMATICS - GENETIC THERAPIES , SCHRODER ISF GLOBAL SUSTAINABLE GROWTH , JANUS HENDERSON HORIZON ASIAN GROWTH , JPM EMERGING MARKETS LOCAL CURRENCY DEBT , BSF AMERICAS DIVERSIFIED EQUITY ABSOLUTE RETURN , BGF GLOBAL MULTI ASSET INCOME , INVESCO ASIA CONSUMER DEMAND , MORGAN STANLEY INVESTMENT FUNDS US DOLLAR SHORT DURATION HIGH YIELD BOND , BSF ASIA PACIFIC DIVERSIFIED EQ ABS RETURN , SCHRODER ISF EUROPEAN ALPHA ABSOLUTE RETURN , TEMPLETON GLB HIGH YIELD , SCHRODER ISF ASIAN BOND TOTAL RETURN , INVESCO INDIA BOND , PIMCO GLOBAL INVESTMENT GRADE CREDIT , ACMBERNSTEIN-SICAV CONCENTRATED GLB EQ PRTFOLIO , SCHRODER ISF US DOLLAR LIQUIDITY , JPM EMERGING MARKETS DEBT , JPM GLOBAL BALANCED , JPM TOTAL EMERGING MARKETS INCOME , MORGAN STANLEY INVESTMENT FUNDS ASIAN PROPERTY , SCHRODER ISF JAPANESE EQUITY , TEMPLETON ASIAN GROWTH , JANUS HENDERSON HORIZON EMERGING MARKET CORPORATE BOND , SCHRODER ISF UK EQUITY , JPM GLOBAL AGGREGATE BOND , PIMCO GLOBAL CORE ASSET ALLOCATION , SCHRODER ISF EMERGING MARKET HARD CURRENCY , BGF GLOBAL LONG-HORIZON EQUITY  , BGF ASIAN HIGH YIELD BOND , TEMPLETON FRONTIER MARKETS , MORGAN STANLEY INVESTMENT FUNDS GLOBAL INSIGHT , MORGAN STANLEY INVESTMENT FUNDS US DOLLAR CORPORATE BOND , AB FCP I - CHINA LOW VOLATILITY EQUITY PORTFOLIO , FRANKLIN BIOTECHNOLOGY DISCOVERY , INVESCO BELT AND ROAD DEBT , PIMCO CREDIT OPPORTUNITIES BOND , BGF EUROPEAN , SCHRODER ISF ASIAN LOCAL CURRENCY BOND , BGF CIRCULAR ECONOMY , SCHRODER ISF ASIAN CONVERTIBLE BOND , JPM EUROPE EQUITY ABSOLUTE ALPHA , SCHRODER ISF SUSTAINABLE EUROPEAN MARKET NEUTRAL , MORGAN STANLEY INVESTMENT FUNDS GLOBAL CONVERTIBLE BOND , JPM US TECHNOLOGY , MFS MERIDIAN MANAGED WEALTH , MFS MERIDIAN DIVERSIFIED INCOME , FRANKLIN GLOBAL CONVERTIBLE SECURITIES , JPM INVESTMENT GLOBAL CONVERTIBLES CONSERVATIVE , AB SUSTAINABLE EURO HIGH YIELD PORTFOLIO , SCHRODER ISF BRIC , AB INDIA GROWTH PORTFOLIO , BGF WORLD FINANCIALS , MFS MERIDIAN GLOBAL RESEARCH FOCUSED , FRANKLIN MUTUAL U.S. VALUE , NEUBERGER BERMAN US REAL ESTATE SECURITIES , BGF GLOBAL HIGH YIELD BOND , SCHRODER ISF GLOBAL MULTI-ASSET GROWTH AND INCOME , JPM GLOBAL GOVERNMENT SHORT DURATION BOND , MORGAN STANLEY INVESTMENT FUNDS SUSTAINABLE ASIA EQUITY , SCHRODER ISF US LARGE CAP , BGF EURO-MARKETS , INVESCO SUSTAINABLE PAN EUROPEAN STRUCTURED EQUITY , MFS MERIDIAN US GOVERNMENT BOND , MORGAN STANLEY INVESTMENT FUNDS EMERGING MARKETS DEBT , AB CHINA A SHARES EQUITY PORTFOLIO , BSF MANAGED INDEX PORTFOLIOS - MODERATE , SCHRODER ISF CHINA A , TEMPLETON EUROPEAN SMALL-MID CAP , SCHRODER ISF JAPANESE SMALLER CO , INVESCO GLOBAL INCOME , JPM EUROPE EQUITY PLUS , BGF EURO CORPORATE BOND , JPM INCOME OPPORTUNITY , FRANKLIN GLOBAL AGGREGATE BOND , JANUS HENDERSON HORIZON GLOBAL PROPERTY EQUITY , JANUS HENDERSON HORIZON BIOTECHNOLOGY , AB GLOBAL REAL ESTATE SECURITIES PORTFOLIO , JPM GLOBAL HIGH YIELD BOND , JANUS HENDERSON HORIZON ASIAN DIVIDEND INCOME , BGF WORLD HEALTHSCIENCE , INVESCO EMERGING MARKET FLEXIBLE BOND , BGF LATIN AMERICAN , TEMPLETON GLOBAL INCOME , FRANKLIN STRATEGIC INCOME , JPM GLOBAL HEALTHCARE , PIMCO GLOBAL INVESTMENT GRADE CREDIT ESG , NEUBERGER BERMAN CORPORATE HYBRID BOND , FRANKLIN FLOATING RATE , AB SELECT US EQUITY , FRANKLIN HIGH YIELD , INVESCO US VALUE EQUITY , JPM US OPPORTUNISTIC LONG-SHORT EQUITY , BSF EMERGING MARKETS EQUITY STRATEGIES , INVESCO ENVIRONMENTAL CLIMATE OPPORTUNITIES BOND , BGF SYSTEMATIC CHINA A-SHARE OPPORTUNITIES , MORGAN STANLEY INVESTMENT FUNDS   GLOBAL CREDIT , NEUBERGER BERMAN GLOBAL HIGH YIELD SDG ENGAGEMENT  , SCHRODER ISF STRATEGIC BOND , BGF EMERGING MARKETS CORPORATE BOND , BGF JAPAN SMALL & MIDCAP OPPORTUNITIES , BSF EMERGING MARKETS SHORT DURATION BOND , SCHRODER ISF EURO EQUITY , MFS MERIDIAN GLOBAL EQUITY INCOME , BGF JAPAN FLEXIBLE EQUITY , BGF ESG EMERGING MARKETS LOCAL CURRENCY BOND , MORGAN STANLEY INVESTMENT FUNDS EMERGING MARKETS FIXED INCOME OPPORTUNITIES , JPM MULTI-MANAGER ALTERNATIVES , BGF SYSTEMATIC GLOBAL EQUITY HIGH INCOME , JPM AMERICA EQUITY , BGF EMERGING MARKETS LOCAL CURRENCY BOND , BGF EUROPEAN EQUITY INCOME , MFS MERIDIAN EURO CREDIT , SCHRODER ISF CHANGING LIFESTYLES , BGF CHINA BOND , MFS MERIDIAN GLOBAL CONCENTRATED  , SCHRODER ISF EMERGING ASIA , SCHRODER ISF QEP GLOBAL ESG EX FOSSIL FUELS , BGF ASIA PACIFIC EQUITY INCOME , MORGAN STANLEY INVESTMENT FUNDS GLOBAL BRANDS EQUITY INCOME , JANUS HENDERSON HORIZON GLOBAL HIGH YIELD BOND , AB INTERNATIONAL TECHNOLOGY PORTFOLIO , BGF EMERGING MARKETS , PIMCO CAPITAL SECURITIES , BGF ASIAN GROWTH LEADERS , MORGAN STANLEY INVESTMENT FUNDS US CORE EQUITY , NEUBERGER BERMAN EMERGING MARKET DEBT BLEND , AB EMERGING MARKET CORPORATE DEBT PORTFOLIO  , SCHRODER ISF ASIAN OPPORTUNITIES , BGF WORLD BOND , FRANKLIN Gulf Wealth Bond , BGF NATURAL RESOURCES GROWTH & INCOME , JPM US VALUE , MORGAN STANLEY INVESTMENT FUNDS GLOBAL HIGH YIELD BOND , JPM GLOBAL CORPORATE BOND , BGF ESG EMERGING MARKETS CORPORATE BOND , SCHRODER ISF GLOBAL CREDIT HIGH INCOME , MORGAN STANLEY INVESTMENT FUNDS DEVELOPING OPPORTUNITY , PIMCO EMERGING MARKETS BOND , AB ASIA INCOME OPPORTUNITIES PORTFOLIO , JPM EUROPE SELECT EQUITY , AB SELECT ABSOLUTE ALPHA PORTFOLIO , JPM EMERGING MARKETS OPPORTUNITIES , BGF EMERGING MARKETS EQUITY INCOME , JPM PACIFIC EQUITY , JPM EMERGING MARKETS SMALL CAP , JPM EUROPE DYNAMIC , JPM AGGREGATE BOND , JPM ASIA PACIFIC EQUITY , JPM ASEAN EQUITY , FRANKLIN INCOME , TEMPLETON GROWTH EURO , BSF GLOBAL EVENT DRIVEN , SCHRODER ISF TAIWANESE EQUITY , BGF FINTECH , BSF MANAGED INDEX PORTFOLIOS - DEFENSIVE , AB FCP I - JAPAN STRAT.VALUE PORTFOLIO , SCHRODER ISF GLOBAL ENERGY TRANSITION , SCHRODER ISF QEP GLOBAL ESG , JPM EMERGING MARKETS INVESTMENT GRADE BOND , BGF ESG EMERGING MARKETS BLENDED BOND , JPM EUROPE EQUITY , INVESCO FUNDS SICAV CONTINENTAL EUROPEAN SMALL CAP , BGF EMERGING EUROPE , SCHRODER ISF QEP GLOBAL QUALITY , MORGAN STANLEY INVESTMENT FUNDS EMERGING MARKETS CORPORATE DEBT , MFS MERIDIAN US CONCENTRATED GROWTH , BGF EURO MARKETS .\n\nRecommend 15 funds from the CANDIDATE SET based on my preferences and similarity with the funds I have (Format: [no. recommended fund name: recommendation reason]).\n\nAnswer:'}], 
  'completion':{
    "id": "chatcmpl-8zpx3g7okT79JGvkVNcnSpDg3HYum",
    "object": "chat.completion",
    "created": 1709748401,
    "model": "gpt-4-0125-preview",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "Given your preferences for diversification, risk management, income generation, quality and stability, and flexibility and liquidity, here are 15 funds from the candidate set that align with your investment strategy:\n\n1. **PIMCO Income**: This fund is known for its focus on generating income through a diversified portfolio of fixed income securities. It aligns with your preference for income generation and quality investments.\n\n2. **JPM Global Strategic Bond**: Offers a diversified approach to global fixed income, similar to your interest in the JPM US Bond, but with a broader geographic exposure, aligning with your diversification and risk management preferences.\n\n3. **BGF World Gold**: Given your balanced approach, adding a commodity fund like this can provide an inflation hedge and further diversification, especially in volatile markets.\n\n4. **BGF Next Generation Technology**: Reflects a preference for growth and innovation, similar to the forward-looking aspect of the Franklin Innovation fund you've chosen. It offers exposure to technology advancements globally.\n\n5. **JPM Global Macro**: This fund's strategy is based on global macroeconomic trends, offering diversification and the potential for risk-adjusted returns, aligning with your preference for global exposure and risk management.\n\n6. **PIMCO Diversified Income**: Similar to the PIMCO Low Average Duration fund, this offers a diversified approach to income generation with a focus on credit risk diversification, aligning with your income and risk management preferences.\n\n7. **Schroder ISF Global Climate Change Equity**: Adds an ESG (Environmental, Social, and Governance) dimension to your portfolio, reflecting a growing trend in responsible investing, without compromising on global diversification.\n\n8. **JPM Global Bond Opportunities**: Offers a flexible approach to global fixed income investing, seeking opportunities across a wide range of bond markets, aligning with your preference for income and global diversification.\n\n9. **BGF ESG Multi-Asset**: This fund combines your interest in balanced and diversified investments with a focus on ESG criteria, offering a mix of asset classes with an ethical investment approach.\n\n10. **Neuberger Berman Next Generation Mobility**: Focuses on companies benefiting from the trend towards new mobility solutions, offering growth potential and aligning with your interest in innovative and forward-looking investments.\n\n11. **JPM Asia Pacific Income**: Provides geographic diversification into the Asia-Pacific region with a focus on income generation, aligning with your diversified and income-focused investment strategy.\n\n12. **PIMCO Global Investment Grade Credit**: Offers exposure to high-quality global corporate bonds, aligning with your preference for quality and stability in the fixed income portion of your portfolio.\n\n13. **BGF Global Multi-Asset Income**: This fund provides a diversified approach to asset allocation with a focus on income generation across multiple asset classes, aligning with your balanced investment approach.\n\n14. **JPM US Small Cap Growth**: Adds growth potential to your portfolio through exposure to small-cap US companies, offering diversification and the possibility of higher returns, albeit with higher risk.\n\n15. **Schroder ISF Global Equity Yield**: Focuses on global equities with attractive dividend yields, aligning with your interest in income generation alongside global diversification.\n\nThese recommendations are based on the inferred preferences from your applied funds, aiming to maintain a balance between growth, income, and risk management across a diversified set of global investments."
        },
        "logprobs": "null",
        "finish_reason": "stop"
      }
    ],
    "usage": {
      "prompt_tokens": 4274,
      "completion_tokens": 683,
      "total_tokens": 4957
    },
    "system_fingerprint": "fp_70b2088885"
  }
}



@application.route('/')
@application.route('/index/')
def home():
  flash('This is a demo for SAKS partners. Avoid misuse.',category='info')
  return render_template('login.html')


@application.route('/login/', methods=['POST'])
def login():
  try:
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
      resp.set_cookie('saks_mvp_name',name)
      resp.set_cookie('saks_mvp_token',token)
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
  #print(f'Fundos do {userId} : {users_funds[userId]}')
  
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
    prefs_completion = ask_to_gpt(prefs_prompt)
#    prefs_completion = test_preference_completion
#    print(prefs_completion)
#    completion = prefs_completion['completion']['choices'][0]['message']['content']
    completion = prefs_completion['completion'].choices[0].message.content
#    print()
#    print(completion)
    answer = markdown.markdown(completion)
    
    resp = make_response( jsonify( {"preferences" : answer, 'completion': completion} ) )
    resp.set_cookie('saks_mvp_selected_user',userId)
    resp.set_cookie('saks_mvp_numrec',numRec)
  except Exception as e:
    print(f'Error in ASK to GPT about user preferences: {str(e)}')
    resp = make_response( jsonify( { } ) )
  
  return resp



@application.route('/recommendation/',methods=['POST'])
def getRecommendation():
  data = request.get_json()
  
  prefsCompletion = data['prefsCompletion']
  
  userId = request.cookies.get('saks_mvp_selected_user')
  numRec = request.cookies.get('saks_mvp_numrec')
  name = request.cookies.get('saks_mvp_name')
  token = request.cookies.get('saks_mvp_token')

  all_funds = session['funds_list']
  users_funds = session['applied_list'][userId]
  candidate_set = set(all_funds) - set(users_funds)


  recsys_prompt = build_recommendation_prompt(users_funds,candidate_set, prefsCompletion, numRec)

  try:
    print()
    recsys_completion = ask_to_gpt(recsys_prompt)
#    recsys_completion = test_recommendation_completion
#    print(recsys_completion)
#    completion = recsys_completion['completion']['choices'][0]['message']['content']
    completion = recsys_completion['completion'].choices[0].message.content
    answer = markdown.markdown(completion)
    
    resp = make_response( jsonify( {"recommendation" : answer, 'completion': completion} ) )
    
    # Salvar o resultado do pedido no banco
    new_request(name,token,userId,numRec,recsys_completion['prompt'],
                recsys_completion['completion'],"gpt-4-turbo-preview")

  except Exception as e:
    print(f'Error requesting recommendation to GPT: {str(e)}')
    resp = make_response( jsonify( { } ) )
  
  return resp


if __name__ == "__main__":
  load_dotenv()
  print('Starting server')
  application.run(debug=True)
