"""
Tests for reading files in standard document format from disk
"""

import botnee
import botnee_config

def test_read_directory(test_data):
    """Test of reading of directory"""
    try:
        collector_directory = botnee_config._data_directory + 'test/journal-collector-output/'
        for i in range(3):
            test_data.append({'docs': botnee.standard_document_io.read_directory(collector_directory + "corpus" + str(i) + "/", "txt", True)})
        
        result = True
    except Exception as e:
        print e

        result = False
        botnee.debug.debug_here()
    return (result, test_data)
