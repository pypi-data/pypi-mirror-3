"""
Testing of reading of JSON files. MongoDB functions currently not included.
"""
import sys

import botnee

def test_read_json(test_data):
    """Test reading of directory with multiple json documents per file"""
    try:
        #test_data = {'jobjs': []}
        test_data = []

        prefix = botnee._data_directory + 'test/json/'
        fnames = [  'gutjnl-small-test.txt',
                    'jnnp-small-test.txt',
                    'combined-small-test.txt'  ]

        for fname in fnames:
            fname = prefix + fname
            test_data.append({'jobjs': botnee.json_io.read_json(fname), 'fname': fname})

        # Get ids as dict
        for data in test_data:
            data['ids'] = {}
            if isinstance(data['jobjs'], dict):
                sys.stdout.write(str(data['jobjs']['id']) + "...")
                data['ids'][data['jobjs']['id']] = 0
            else:
                for i,jobj in enumerate(data['jobjs']):
                    sys.stdout.write("\n" + str(i) + ":" + str(jobj['id']) + "...")
                    data['ids'][jobj['id']] = i

            # Check for uniqueness of ids
            assert len(set(data['ids'].values())) == len(data['ids'])
            assert len(set(data['ids'].keys())) == len(data['ids'])

        '''
        # Get ids as list
        for data in test_data:
            data['ids'] = []
            for jobj in data['jobjs']:
                data['ids'].append(jobj['id'])
        assert(len(set(data['ids'])) == len(data['ids']))
        '''

        result = len(test_data)==3
    except Exception as e:
        print e

        test_data = None
        result = False
        botnee.debug.debug_here()
    return (result, test_data)


def test_get_all_text(test_data):
    """Test of pulling out the body text from JSON documents"""
    try:
        for data in test_data:
            #data['tokens_list'] = []
            data['docs'] = []
            for jobj in data['jobjs']:
                text = botnee.json_io.get_all_text(jobj)
                #(text, data_dict) = botnee.process.process_text(text)
                #data['tokens_list'].append(data_dict['tokens'])
                data['docs'].append({'body': text, 'guid': jobj['id']})
        result = True
    except Exception as e:
        print e

        result = False
        botnee.debug.debug_here()
    return (result, test_data)
