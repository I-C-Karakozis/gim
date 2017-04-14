def gen_response(success=True, msg=None, data=None):
    res = {}
    res['status'] = 'success' if success else 'failed'
    if msg is not None:
        res['message'] = msg
    if data is not None:
        res['data'] = data
    return res
