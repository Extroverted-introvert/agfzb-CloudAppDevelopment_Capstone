import sys
from ibmcloudant.cloudant_v1 import Document, CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
def main(dict):
    authenticator = IAMAuthenticator(dict['IAM_API_KEY'])
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(dict['COUCH_URL'])
    review = dict.get('review', None)
    if review:
        response = service.post_document(db='reviews', document=dict["review"]).get_result()
    else:    
        response = "No input Data"
    try:
        result= {
        'headers': {'Content-Type':'application/json'},
        'body': {'data':response}
        }
        return result
    except Exception as err:
        print("connection error")
        return {"error": err}
