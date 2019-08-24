from flask import Flask, request, make_response, jsonify
import json


"""
Sample request 
{'responseId': 'b73b9cd6-dfb8-4791-b95a-c69a04957b8b-5e314962', 'queryResult': {'queryText': '502, Maskar House, Goregaon East', 'parameters': {'address': 'Maskar House, Goregaon East', 'number': [502.0], 'geo-city': ''}, 'allRequiredParamsPresent': True, 'fulfillmentText': 'What would you like to have ?', 'fulfillmentMessages': [{'text': {'text': ['What would you like to have ?']}}], 'outputContexts': [{'name': 'projects/foodbot-ywldrl/agent/sessions/93908294-ca63-d49f-5b51-1a6c0e7c2368/contexts/delivery', 'lifespanCount': 5, 'parameters': {'address': 'Maskar House, Goregaon East', 'address.original': 'Maskar House, Goregaon East', 'number': [502.0], 'number.original': ['502'], 'geo-city': '', 'geo-city.original': ''}}], 'intent': {'name': 'projects/foodbot-ywldrl/agent/intents/ca3c5532-fbb6-400c-932b-b0cceb16d7ee', 'displayName': 'delivery:location'}, 'intentDetectionConfidence': 1.0, 'languageCode': 'en'}, 'originalDetectIntentRequest': {'payload': {}}, 'session': 'projects/foodbot-ywldrl/agent/sessions/93908294-ca63-d49f-5b51-1a6c0e7c2368'}

"""

def check_context(contexts_arr,context_name):
    return (len([cn for cn in contexts_arr if cn['name'].find(context_name)!=-1])>0)

def process_location(query_results):
    parameters = query_results['parameters']
    if(len(parameters['address'])<5 and not check_context(query_results['outputContexts'],"address_saved")):
        print("triggering location event")
        return {"followupEventInput":{
            "name":"getlocation"
        }}
    else:
        print("Processing the address at ",parameters['address'])
        {
        "fulfillmentText":"What would you like to order?",
        "outputContexts": [
            {
                "name": "projects/foodbot-ywldrl/agent/sessions/93908294-ca63-d49f-5b51-1a6c0e7c2368/contexts/address_saved",
                "lifespanCount":25
            } 
        ]
        }
    return 1

def intent_handler(intent,query_results):
    if(intent == "delivery:location"):
        return process_location(query_results)
    elif(intent == "delivery:order"):
        print("Processing Order")
    else:
        return {"fulfillmentText":"The work is still in progress for the intent {}".format(intent)}
    

def naturals_response_handler():
    req = request.get_json(force=True)
    query_results = req.get('queryResult')
    intent = query_results['intent']['displayName']
    reply = intent_handler(intent,query_results)
    return reply
