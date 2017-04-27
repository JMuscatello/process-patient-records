# process_patient_results.py

Python 2.7 script to generate JSON output from patient record files. Requires labresults in .csv, labresults-code in .csv and patient data in .json format. Example input fiels are supplied.

OPTIONS:

    -f <path-to-labresults(csv)> <path-to-labresults-code(csv)> <path-to-patients(json)>

Specifies files to open (required)
    
OUTPUT FILES:
    patient_data.json - JSON file in specified format containing patient data, lab results and panels for each result
    
USAGE EXAMPLE:

    $ python2.7 process_patient_results.py -f labresults.csv labresults-codes.csv patients.json

will generate the file "patient_data.json"

ABOUT:

The code utilises the csv and json modules in python2.7 for ease of input and output. Patient data is loaded into an objects. The results file is iterated over and common panels are grouped together in a Result object based on the sampleID field. These are then converted to dictionaries and lists in preparation for JSON output. 

KNOWN BUGS:

At the moment the JSON output is not set to a specific order, so whilst all the information is stored in the relevant pairs, the output order is not identical to the specified format.

Jordan Muscatello, April 2017 
