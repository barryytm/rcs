from __future__ import division, print_function, unicode_literals

import json, pymongo, requests, jsonschema, parser, db, config, os

from flask import Flask, Response
from flask.ext.restful import reqparse, request, abort, Api, Resource

app = Flask(__name__)
app.config.from_object(config)
if os.environ.get('RCS_CONFIG'):
    app.config.from_envvar('RCS_CONFIG')
api = Api(app)

client = pymongo.MongoClient( host=app.config['DB_HOST'], port=app.config['DB_PORT'] )
jsonset = client[app.config['DB_NAME']].json
validator = jsonschema.validators.Draft4Validator( json.load(open(app.config['REG_SCHEMA'])) )

def get_doc( smallkey ):
    return jsonset.find_one({'smallkey':smallkey})


class Doc(Resource):
    def get(self, lang, smallkey):
        doc = get_doc( smallkey, lang )
        print( doc )
        if doc is None:
            return None,404
        return Response(json.dumps(doc['data']),  mimetype='application/json')

    def put(self, smallkey):
        data = parser.make_feature_node()
        data = make_feature_parser().parse_args()
        print( data )
        get_feature_service( data )
        print( data )
        jsonset.remove( { 'smallkey':smallkey } )
        jsonset.insert( { 'smallkey':smallkey, 'data':data } )
        return smallkey, 201

class Docs(Resource):
    def get(self, lang, smallkeylist):
        keys = [ x.strip() for x in smallkeylist.split(',') ]
        docs = [ get_doc(smallkey,lang)['data'] for smallkey in keys ]
        return Response(json.dumps(docs),  mimetype='application/json')

class Register(Resource):
    def put(self, smallkey):
        try:
            s = json.loads( request.data )
        except:
            return 'Unparsable body',400
        if not validator.is_valid( s ):
            return Response(json.dumps({ 'errors': [x.message for x in validator.iter_errors(s)] }),  mimetype='application/json'), 400
        data = parser.make_feature_node()
        print( data )
        data = parser.get_feature_service( data )
        print( data )
        jsonset.remove( { 'smallkey':smallkey } )
        jsonset.insert( { 'smallkey':smallkey, 'data':data } )
        return smallkey, 201

    def delete(self, smallkey):
        jsonset.remove( { 'smallkey':smallkey } )
        return '', 204


api.add_resource(Doc, '/doc/<string:lang>/<string:smallkey>')
api.add_resource(Docs, '/docs/<string:lang>/<string:smallkeylist>')
api.add_resource(Register, '/register/<string:smallkey>')

if __name__ == '__main__':
    app.run(debug=True)
