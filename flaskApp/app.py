from flask import Flask, request, make_response, jsonify
import requests
import json


with open('data/UrbanClap_data.json') as json_file:
    uc_data = json.load(json_file)
json_file.close()


app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hello world! Welcome to Call Asst Website</h1> <p>The website is under development. Please contact at lodhapratik9@gmail.com for any queries</p>'

import requests
import textdistance



location_info=[{'name': 'Ahmedabad', 'value': 'ahmedabad'}, {'name': 'Bangalore', 'value': 'bangalore'}, {'name': 'Chennai', 'value': 'chennai'}, {'name': 'Delhi NCR', 'value': 'delhi'}, {'name': 'Chandigarh Tricity', 'value': 'chandigarh'}, {'name': 'Jaipur', 'value': 'jaipur'}, {'name': 'Dubai', 'value': 'dubai'}, {'name': 'Abu Dhabi', 'value': 'abudhabi'}, {'name': 'Hyderabad', 'value': 'hyderabad'}, {'name': 'Kolkata', 'value': 'kolkata'}, {'name': 'Mumbai', 'value': 'mumbai'}, {'name': 'Pune', 'value': 'pune'}]

def service_details_fn(uc_data,city_name,service_name):
    city_id = [city['city_name'] for city in uc_data].index(city_name.lower())
    service_id = [service['display_name'].lower() for service in uc_data[city_id]['services']].index(service_name.lower())
    try:
        options = uc_data[city_id]['services'][service_id]['serivce_detail_info'][0]['meta_data']['questions']
        option_text = " or ".join([o['text'] for o in options])
        reply = "Let us know what help do you need. It can be {0}".format(option_text)
    except:
        question = uc_data[city_id]['services'][service_id]['serivce_detail_info'][0]['title']
        answers = [ans['title'] for ans in uc_data[city_id]['services'][service_id]['serivce_detail_info'][0]['meta_data']['answers']]
        reply = question + " A sample reply can be " + " or ".join(answers)
    return reply

def jaccard_similarity(list1, list2):
    list1 = list(list1.lower())
    list2 = list(list2.lower())
    intersection = len(set(list1).intersection(list2))
    union = len(set(list1)) + len(set(list2)) - intersection
    return intersection / union


def find_city(city,location_info):
    max_score = 0
    max_location = ""
    for location in location_info:
        score = textdistance.levenshtein.normalized_similarity(location['name'].lower(),city.lower())
        location['Similarity_score'] = score
        if score>max_score:
            max_score = score
            max_location = location
        else:
            continue
    return location_info, max_location

def find_service(service,max_location,URL_TEMPLATE):
    URL = URL_TEMPLATE.format(max_location['value'])
    r = requests.get(url = URL)
    r_data = r.json()
    r_data = r_data["success"]["data"]
    services = [x['display_name'] for x in r_data]
    print(services)
    max_score = 0
    max_service = ""
    for serv in services:
        score = textdistance.levenshtein.normalized_similarity(serv,service)
        if score>max_score:
            max_score = score
            serivce_selected = serv
        else:
            continue
    return serivce_selected

def service_center(data,location_info):
    URL_TEMPLATE = "https://www.urbanclap.com/api/v1/customercategories/search/category/city_{0}_v2/a"
    location_info, max_location = find_city(data['parameters']['geo-city'],location_info)
    service_selected = find_service(data['parameters']['Service'],max_location,URL_TEMPLATE)
    reply = "We are happy to help you with that. Please confirm that you want a {0} service and you are in {1} city ".format(service_selected,max_location['name'])
    return reply,max_location['name'],service_selected


def results():
    response = {'fulfillmentText': 'We are still working on improvements'}
    try:
        req = request.get_json(force=True)
        query_results = req.get('queryResult')
        action = query_results['action']
        parameters = query_results['parameters']

        if(action in ["Purpose.Purpose-custom","Purpose.Purpose-custom.Purpose-custom-fallback"]):
            reply, max_location, max_service = service_center(req.get("queryResult"),location_info)
            response['fulfillmentText'] = reply
            response["outputContexts"] = [{
                                            "name": "projects/urbanclap-ecvjtu/agent/sessions/36b839e5-325a-4931-b604-193fa382bb12/contexts/service_details",
                                            "lifespanCount": 5,
                                            "parameters":{
                                            "city_name":max_location, "service_name":max_service
                                            }
                                          }]

        elif(action in ["Purpose.Purpose-custom.Purpose-custom-yes"]):
            print("In this function")
            output_context = query_results['outputContexts']
            output_context_service = [out for out in output_context if out["name"].find("service_details") !=-1]
            print(output_context_service)
            ocs_parameters = output_context_service[0]["parameters"]
            print(ocs_parameters)
            reply = service_details_fn(uc_data,ocs_parameters['city_name'],ocs_parameters['service_name'])
            response['fulfillmentText'] = reply
        else:
            reply = "no intent found"
            response['fulfillmentText'] = reply
        # return a fulfillment response
    except Exception as e:
        print(e)
        reply = e
        response['fulfillmentText'] = reply 
    return response


@app.route('/webhook', methods=['GET', 'POST'])
def function():
    print("In Webhook")
    try:
        return make_response(jsonify(results()))
    except:
        return make_response(jsonify({'fulfillmentText':'Apologies - The Urban Clap API failed to respond'}))
        
if __name__ == '__main__':
    app.run(debug=True)
