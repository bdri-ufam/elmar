# ELMAR - Explainable Language Modeling for financial Advisor Recommendation

ELMAR is a prototype tool designed to help financial advisors recommend private pension funds to investors based on their preferences, offering personalized investment suggestions.
The tool leverages Large Language Models (LLMs), which enhance explicability by providing clear and understandable rationales for recommendations and effectively handles both sequential and cold-start scenarios. 

## Requirements & Server

Python  (tested on 3.9, 3.10 and 3.11) and [Flask](https://flask.palletsprojects.com/en/3.0.x/).

Install dependencies:
> `pip install -r requirements.txt`

Run the server:
> `python application.py`

The project contains the files need to deploy in [AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/) (including for who is FreeTier eligible).

NOTES
> 1 A `.env` file is mandatory to set the environment vars for the application work properly. Use the template available in [`.env.example`](.env.example). 
> 2 It is need update the database schema to be used to load and save data. Look for the SQL queries in the [`db_operations.py`](db_operations.py) file.



Enjoy!
