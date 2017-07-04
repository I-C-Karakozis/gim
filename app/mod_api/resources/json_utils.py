from app import app
from app.mod_api import models

auth_schema = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
        },
    "required": ["email", "password"],
    "additionalProperties": False
    }

def gen_response(success=True, msg=None, data=None):
    res = {}
    res['status'] = 'success' if success else 'failed'
    if msg is not None:
        res['message'] = msg
    if data is not None:
        res['data'] = data
    return res

def video_info(video, u_id):
    return {
        'video_id': video.v_id,
        'uploaded_on': video.uploaded_on,
        'tags': [t.name for t in video.tags],
        'upvotes': len([vt for vt in video.votes if vt.upvote]),
        'downvotes': len([vt for vt in video.votes if not vt.upvote]),
        'user_vote': models.Vote.get_vote(u_id, video.v_id)
        }
