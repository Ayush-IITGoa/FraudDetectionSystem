import json

def check_fraud(id_number, country_code):
    is_fraudulent = False

    with open('customer_care.json', 'r') as file:
        data = json.load(file)


    # Iterate through each record in the JSON data
    for record in data:
        record_id = record.get('idnumber')  # Get the ID number from the record
        record_country = record.get('countrycode')  # Get the country code from the record

        # Check if both ID number and country code match
        if country_code is not None:
            if record_id == id_number and record_country == country_code:
                # print(f"Fraud detected: Both ID Number and Country Code match.")
                is_fraudulent = True
                return

        # Check if only ID number matches
        if record_id == id_number:
            # print(f"Suspicious activity detected: Only ID Number matches.")
            is_fraudulent = True
    return is_fraudulent

def more_entries(new_entries):
    with open('customer_care.json', 'r') as file:
        data = json.load(file)

    data_to_write = []
    for idnumber, country_code in new_entries:
        new_entry = {
            "suspectname": None,
            "idnumber": {idnumber},
            "countrycode": country_code  # Use the country code from the array
        }
        data_to_write.append(new_entry)
    data.extend(data_to_write)

    # Save the updated data back to a JSON file
    with open('customer_care.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
