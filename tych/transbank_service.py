import requests

TRANSBANK_API_URL = "https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.2/transactions"

# Credenciales de integración (pruebas)#
TBK_API_KEY_ID     = "597055555532"
TBK_API_KEY_SECRET = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"


def get_headers():
    return {
        "Authorization": "Token",
        "Tbk-Api-Key-Id": TBK_API_KEY_ID,
        "Tbk-Api-Key-Secret": TBK_API_KEY_SECRET,
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }


def crear_transaccion(buy_order, session_id, amount, return_url):
    #Paso 1: Crear transacción en Transbank#
    body = {
        "buy_order": str(buy_order),
        "session_id": str(session_id),
        "amount": int(amount),
        "return_url": return_url,
    }
    response = requests.post(TRANSBANK_API_URL, json=body, headers=get_headers())
    return response


def confirmar_transaccion(token_ws):
    #Paso 2: Confirmar la transacción. Retorna detalle del pago#
    url = f"{TRANSBANK_API_URL}/{token_ws}"
    response = requests.put(url, headers=get_headers())
    return response


def revertir_transaccion(token_ws, amount):
    #Reversión en caso de rechazo#
    url = f"{TRANSBANK_API_URL}/{token_ws}/refunds"
    response = requests.post(url, json={"amount": int(amount)}, headers=get_headers())
    return response