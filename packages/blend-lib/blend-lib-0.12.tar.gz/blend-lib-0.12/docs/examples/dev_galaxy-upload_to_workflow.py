from blend.galaxy import GalaxyInstance
# Define a connection to an instane of Galaxy
gi = GalaxyInstance('http://127.0.0.1:8000', 'c18666899798c5ad233c511cd2d66c2d')
# Create a data library
l = gi.libraries.create_library('Set 13')
# Uload some data to the data library
gi.libraries.upload_file_from_url('44875ff5c2e98ea3',
    'http://115.146.92.164/datasets/e93bfde97eb9384b/display?to_ext=fastqsanger')
gi.libraries.upload_file_from_url('44875ff5c2e98ea3',
    'http://115.146.92.164/datasets/4d6ed4e369701852/display?to_ext=fastqsanger')
# Create a history
gi.histories.create_history('Run 13')
# Get information on how to run a workflow
ws = gc.workflows.get_workflows()
gi.workflows.show_workflow(ws[0]['id'])
# {u'id': u'93ab6bbd094e1dcd',
#  u'inputs': {u'25': {u'label': u'Input Dataset', u'value': u''},
#  u'27': {u'label': u'Input Dataset', u'value': u''}},
#  u'name': u'Map',
#  u'url': u'/api/workflows/93ab6bbd094e1dcd'}
dataset_map = {'25': {'id':'499d91f547f339b6', 'src':'ld'}, '27': {'id':'ec357da7e146b394', 'src':'ls'}}
gi.workflows.run('93ab6bbd094e1dcd', dataset_map, 'ea910ab58b5234dc')

