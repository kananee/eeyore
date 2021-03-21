import json
import time
from flask import Flask
from flask_jsonpify import jsonpify
from flask_restful import Resource,Api,reqparse
import requests
import pandas as pd

app=Flask(__name__)
api=Api(app)

@app.route('/')
def index():
    return "hello world"

class get_mathcal(Resource):
    def get(self):
        parser=reqparse.RequestParser()
        parser.add_argument('input1',type=str)
        parser.add_argument('input2',type=str)
        parser.add_argument('operation',type=str)
        dictp=parser.parse_args()
        inp1=dictp['input1']
        inp2=dictp['input2']
        oper=dictp['operation']
        if(oper=='plus'):
            oper='+'
        else:
            oper='-'
        stringcal=inp1+' '+oper+' '+inp2
        print(stringcal)
        answ = eval(stringcal)
        result={}
        result['stringcal']=stringcal
        result['answer']=answ
        return(result)
api.add_resource(get_mathcal, '/cal',endpoint='cal')
if __name__=='__main__':
    app.run(threaded=True)
