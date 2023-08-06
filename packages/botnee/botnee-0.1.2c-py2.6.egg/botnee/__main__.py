"""
botnee main function: Runs unit test
"""

#from botnee import process, corpus

import sys


print "Running unit tests..."

kb_input = None
print "Test using Standard document format (1) or JSON format (2):"
while kb_input not in [1, 2]:
    try:
        kb_input = int(raw_input())
    except ValueError:
        print 'Invalid Number'

if(kb_input==1):
    function_list = [
        ("standard_document_io", "read_directory"),
        ]
elif(kb_input==2):
    function_list = [
        ("json_io", "read_json"),
        ("json_io", "get_all_tekb_inputt"),
        ]
else:
    function_list = [
        ("standard_document_io", "read_directory"),
        ("json_io", "read_json"),
        ("json_io", "get_all_tekb_inputt"),
        ]

function_list.extend([
    ("process", "process_doc"),
    ("process", "create_guid_indices"),
    ("process", "get_tokens_lists_by_guid"),
    ("process", "create_dictionary"),
    ("process", "tokens_to_hash"),
    ("process", "calculate_tf"),
    ("process", "calculate_idf"),
    ("process", "calculate_tfidf"),
    ("process", "calculate_kernel"),
    ("corpus", "Corpus"),
    ("process", "merge_dictionaries"),
    ("process", "merge_ids"),
    ("process", "merge_tokens"),
    ("process", "merge_tf"),
    ("process", "merge_idf"),
    ("process", "merge_meta_dict"),
    ("process", "merge_data_dict"),
    ("corpus", "merge_corpora"),
    ("corpus", "stress")
    ])
results = []
test_data = []

for function in function_list:
    (result, test_data) = test_harness.test_harness(function, test_data)
    results.append(result)

# close files
for data in test_data:
    if data.has_key('corpus'):
        data['corpus'].close()

sys.stdout.write("Tests completed")
if(all(results)):
    print " successfully"
else:
    print " with errors"

