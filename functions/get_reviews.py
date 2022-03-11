import sys
from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
def main(dict):
    authenticator = IAMAuthenticator(dict['IAM_API_KEY'])
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(dict['COUCH_URL'])
    id = dict.get('dealerId', None)
    if id:
        response = service.post_find(db='reviews',
        selector={"dealership": int(id)},
        ).get_result()
    else:    
        response = service.post_all_docs( db='reviews', include_docs=True).get_result()
    try:
        # result_by_filter=my_database.get_query_result(selector,raw_result=True)
        result= {
        'headers': {'Content-Type':'application/json'},
        'body': {'data':response}
        }
        return result
    except Exception as err:
        print("connection error")
        return {"error": err}
