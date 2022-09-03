from pprint import pprint
import requests
import os

foods = ["chicken", "carrots", "potatoes", "tomatoes"]

USDA_KEY = os.environ['usda_key']
URL = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={USDA_KEY}&query="
URL_2 = f"https://api.nal.usda.gov/fdc/v1/foods/list?api_key={USDA_KEY}"


response = requests.get(f"{URL_2}").json()
lst = {}
# for x in response:
#     lst[x['description']] = x['fdcId']
#
# print(lst)
pprint(response)
# def nutrients(food):
#     query = []
#     url = f"{URL_2}{food}"
#
#     response = requests.get(f"{url}").json()
#     return response


