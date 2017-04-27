""" process_patient_results.py

    Python2.7 script to process patient information and output records in JSON
    format
 
    Copyright (C) 2017 Jordan Muscatello

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

import argparse
import csv
import json
import datetime

class Patient(object):
    """
    Contains all patient information

    Parameters:
    patient_id - int, hospital patient id
    patient_uuid - string, patient uuid
    firstname - string
    lastname - string
    dob - string, date of birth (already ISO 8601)
    -----
    result_list - Results object, list of lab results
    """
    result_list = []

    def __init__(self, patient_id, patient_uuid, firstname, lastname, dob):
        self.patient_id = patient_id
        self.patient_uuid = patient_uuid        
        self.firstname = firstname
        self.lastname = lastname
        self.dob = dob

    def return_dictionary(self):
        """ returns Patient as dictionary (for json output)"""
        
        patient_dict = {}
        result_dict_list = []
        for result in self.result_list:
            result_dict_list.append(result.return_dictionary())

        patient_dict["lastName"] = self.lastname
        patient_dict["firstName"] = self.firstname
        patient_dict["dob"] = self.dob
        patient_dict["lab_results"] = result_dict_list
        patient_dict["id"] = self.patient_uuid

        return patient_dict

class Result(object):
    """
    Lab results of a single profile
    
    Parameters
    patient_id - int, hospital patient id
    timestamp - string (converted to ISO 8601)
    profile - (string, string), name and code of sample
    -----
    panel_list - List of Panel objects
    """
    panel_list = []

    def __init__(self, patient_id, timestamp, profile):
        self.patient_id = patient_id
        self.timestamp = timestamp
        self.profile = profile
    def return_dictionary(self):
        """returns Result as dictionary (for json output)"""
        result_dict = {}
        panel_dict_list = []  
        for panel in self.panel_list:           
            panel_dict_list.append(jdefault(panel))

        result_dict["panel"] = panel_dict_list
        result_dict["profile"] = {"name":self.profile[0], 
                                  "code":self.profile[1]}
        result_dict["timestamp"] = self.timestamp

        return result_dict
 
class Panel(object):
    """
    results panel for a single profile
    
    Parameters
    code - string, SNOMED code of test
    label - string, description of code
    value - string, value of test
    unit - string, test units
    lower - double, lower bound
    upper - double, upper bound
    """
    
    def __init__(self, SNOMED, label, value, unit, lower, upper):
        self.code = SNOMED
        self.label = label
        self.value = value
        self.unit = unit
        self.lower = lower
        self.upper = upper         
    
def load_patients(pat_info_json):
    """ 
    Returns list of Patient objects from json patient info
 
    Parameters:
    pat_info_json - file object corresponding to json input of patient data
   
    Output:
    patient_list - list of newly initialised patient objects
    """ 

    pat_info_list = json.load(pat_info_json)
    patient_list = []
    for pat_info in pat_info_list:
        p_id = int(pat_info['identifiers'][0])
        p_uuid = pat_info['id']
        p_fname = pat_info['firstName']
        p_lname = pat_info['lastName']
        p_DOB = pat_info['dateOfBirth'] # could use date object but leave atm

        new_patient = Patient(p_id, p_uuid, p_fname, p_lname, p_DOB)
        patient_list.append(new_patient)

    return patient_list

def load_results_codes(labresults_code_csv):
    """
    Returns hash tables for lab results 
    code -> SNOMED 
    code -> description

    Parameters:
    labresults_code_csv - file object corresponding to csv file for lab codes
    
    Returns:
    code_SNOMED_dict - code to SNOMED
    code_description_dict - code to description
    
    """
    code_SNOMED_dict = {}
    code_description_dict = {}
    code_reader = csv.reader(labresults_code_csv)

    for row in code_reader:
        code_SNOMED_dict[row[0]] = row[1]
        code_description_dict[row[0]] = row[2]

    return code_SNOMED_dict, code_description_dict

def generate_lab_results(labresults_csv, code_SNOMED_dict, 
                         code_description_dict, patient_list):
    """
    Iterates over .csv file containing lab results - uses sampleID string 
    to identify results blocks from each profile

    Parameters:
    labresults_csv - file object of lab results
    code_SNOMED_dict - string:string dictionary
    code_description_dict - string:string dictionary
    patient_list - list of Patient objects to assign Result to

    Returns:
    result_list - list of Results objects 
    """
    result_list = []
    sample_id_prev = None
    patient_id_prev = None
    date_prev = None
    profile_name_prev = None
    profile_code_prev = None
    results_reader = csv.reader(labresults_csv)
    first_row = True
    res_start = 5 # start column of results in csv file (from zero)
    res_end = 29 # last column of results in csv file (from zero)
    panel_list = []
    patient_results_dict = {}
    for patient in patient_list:
        patient_results_dict[patient.patient_id] = []


    for row in results_reader:
        ## can test for errors at this point, e.g. incorrect no. of columns
        if first_row: # skip first row
            first_row = False
        else: 
            sample_id = row[1]
            patient_id = int(row[0])
            # convert date to ISO 8601
            date_split = row[2].split('/')            
            date = datetime.date(int(date_split[2]), 
                                 int(date_split[1]), 
                                 int(date_split[0])).isoformat()
            profile_name = row[3]
            profile_code = row[4]
            code = row[30]
            unit = row[31]
            if row[32]: lower = float(row[32]) 
            else: lower = None
            if row[33]: upper = float(row[33])
            else: upper = None

            # split results into code-value pair   
            code_value_dict = {}
            for i in range(res_start, res_end+1):
                if row[i]:
                    pair = row[i].split('~') 
                    code_value_dict[pair[0]] = pair[1]
  
            SNOMED = code_SNOMED_dict[code]
            description = code_description_dict[code]
            value = code_value_dict[code]
            panel_new = Panel(SNOMED, 
                              description, 
                              value, 
                              unit, 
                              lower, 
                              upper)

            if sample_id != sample_id_prev:
                # create new result 
                result_new = Result(patient_id_prev, date_prev, 
                                    (profile_name_prev, profile_code_prev))
                result_new.panel_list = panel_list             

                panel_list = []
 
                # Add result to patient list
                patient_results_dict[patient_id].append(result_new)

           
            panel_list.append(panel_new)
            patient_id_prev = patient_id
            date_prev = date
            profile_name_prev = profile_name
            profile_code_prev = profile_code
            sample_id_prev = sample_id

    # Assign results lists to patient objects
    for patient in patient_list:
        patient.result_list = patient_results_dict[patient_id]    
        
    return result_list

def jdefault(object):
    """ outputs dictionary from object """
    return object.__dict__

def output_patients_to_json(patient_list):
    """
    Outputs patient test information to json file
    
    Parameters: 
    patient_list - list of Patient objects    
    """  
    patient_dict_list = []
    for patient in patient_list:
        patient_dict_list.append(patient.return_dictionary())
 
    with open('patient_data.json', 'w') as outfile:
        json.dump({"patients":patient_dict_list}, 
                  outfile, indent=4, separators=(',', ': ')) 

def assign_result(patient_list, result):
    """
    Matches Result with Patient and adds to result list 
   
    Parameters:
    patient_list - list of Patient objects
    result - Result object  
    """    
    for patient in patient_list:
        if result.patient_id == patient.patient_id:
            patient.result_list.append(result)
             

def check_result_assignment(patient_list):
    for patient in patient_list:
        for result in patient.result_list:
            if result.patient_id != patient.patient_id: 
                print "ERROR p_id {} : f_id {}".format(patient.patient_id, 
                                                 result.patient_id)

def main():

    ## Parse file names
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, nargs=3, 
                        help=("labresults and patient info records to open:\n"
                              "\n<labresults (csv)> <labresults code (csv)> "
                              "<patient information (json)>"),
                        required=True)

    args = parser.parse_args()
    fname_list = args.f 

    labresults_csv = open(fname_list[0], 'r')
    labresults_codes_csv = open(fname_list[1], 'r')
    pat_info_json = open(fname_list[2], 'r')

    patient_list = load_patients(pat_info_json)

    code_SNOMED_dict, code_description_dict = load_results_codes(
                                              labresults_codes_csv)
    
    generate_lab_results(labresults_csv, code_SNOMED_dict, 
                         code_description_dict, patient_list)

    output_patients_to_json(patient_list)

if __name__ == "__main__":
    main()
