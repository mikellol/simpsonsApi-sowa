from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort
from flask_pymongo import pymongo
from flask_cors import CORS
import app.db_config as database

app =Flask(__name__)
api = Api(app)
CORS(app)

post_students_args= reqparse.RequestParser()

post_students_args.add_argument("id",type=int,help="ERROR id value needs to be an integer", required=True)
post_students_args.add_argument("first_name",type=str,help="ERROR first_name is required", required=True)
post_students_args.add_argument("last_name",type=str,help="ERROR last_name is required", required=True)
post_students_args.add_argument("image",type=str,help="ERROR you need to add the image url", required=True)
post_students_args.add_argument("group",type=str, required=False)
post_students_args.add_argument("career",type=str, required=False)

class Test(Resource):
    def get(self):
        return jsonify({"message":"You are connected"})

class Student(Resource):
    def get(self,id):
        response = database.db.students.find_one({'id':id})
        del response['_id']
        return jsonify(response)

class Students(Resource):
    def get(self):
        response= list(database.db.students.find())
        students=[]
        for student in response:
            del student['_id']
            students.append(student)
        return jsonify({'results':students})

    
    def post(self):
        args=post_students_args.parse_args()
        self.abort_if_id_exist(args['id'])      #self.abort_if_id_exist(request.json['id'])
        #print(args)
        database.db.students.insert_one({
            'id': args['id'],
            'first_name': args['first_name'],
            'last_name': args['last_name'],
            'image': args['image'],
            'group': args['group'],
            'career': args['career'],
            #'career': request.json['career'],
        })
        return jsonify(args)
        #return jsonify({"200": request.json})

    def put(self,id):
        args=post_students_args.parse_args()
        self.abort_if_not_exist(id)
        database.db.students.update_one(
            {'id':id},
            {'$set':{
                'id': args['id'],
                'first_name': args['first_name'],
                'last_name': args['last_name'],
                'image': args['image'],
                'group': args['group'],
                'career': args['career'],
            }}
        )
        return jsonify(args)

    def patch(self):
        pass
    
    def delete(self):
        pass

    def abort_if_id_exist(self,id):
        if database.db.students.find_one({'id':id}):
            abort(jsonify({'error':{'406':f"The student with the id: {id} already exist"}}))

    def abort_if_not_exist(self,id):
        student=database.db.students.find_one({'id':id})
        if not student: 
            abort(jsonify({'error':{'404':f"The student with the id: {id} not found"}}))
        else:
            return student


api.add_resource(Test,'/test/')
api.add_resource(Students,'/students/','/students/<int:id>')
api.add_resource(Student,'/students/<int:id>/')

if __name__=='__main__':
    app.run(load_dotenv=True, port=8080)