


def service_details(uc_data,city_name,service_name):
    city_id = [city['city_name'] for city in uc_data].index(city_name.lower())
    service_id = [service['display_name'].lower() for service in uc_data[city_id]['services']].index(service_name.lower())
    options = uc_data[city_id]['services'][service_id]['serivce_detail_info'][0]['meta_data']['questions']
    option_text = " or ".join([o['text'] for o in options])
    return "Let us know what help do you need. It can be {0}".format(option_text)