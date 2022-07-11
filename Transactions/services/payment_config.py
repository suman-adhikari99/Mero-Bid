import requests

def KhaltiPaymentVerification(amount, token):
    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
        'token': token,
        'amount': amount
    }
    headers = {
        "Authorization": "Key test_secret_key_f7a9de1ca6b540b8bee11390beca94ba"}
    return requests.post(url, payload, headers=headers)


def EsewaPaymentVerification(request):
    oid = request.data.get("oid")
    amt = request.data.get("amt")
    refId = request.data.get("refId")
    url ="https://esewa.com.np/epay/transrec"
    payload = {
            'amt': amt,
            'scd': 'NP-ES-BOLPATRA',
            'rid': refId,
            'pid': oid,

    }
    return requests.post(url, payload)



