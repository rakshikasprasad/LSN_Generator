from app import app

# Vercel requires a function named "handler"
def handler(event, context):
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)