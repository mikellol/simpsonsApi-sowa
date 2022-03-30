from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort
from flask_pymongo import pymongo
from flask_cors import CORS
import app.db_config as database

app =Flask(__name__)
api = Api(app)
CORS(app)

'''  '''
post_characters_args= reqparse.RequestParser()
post_characters_args.add_argument("id",type=int,help="ERROR id value needs to be an integer", required=True)
post_characters_args.add_argument("name",type=str,help="ERROR name is required", required=True)
post_characters_args.add_argument("gender",type=str,help="ERROR gender is required", required=True)
post_characters_args.add_argument("image",type=str,help="ERROR you need to add the image url", required=True)


patch_characters_args=reqparse.RequestParser()
patch_characters_args.add_argument("id",type=int,help="ERROR id value needs to be an integer", required=False)
patch_characters_args.add_argument("name",type=str,help="ERROR name is required", required=False)
patch_characters_args.add_argument("gender",type=str,help="ERROR gender is required", required=False)
patch_characters_args.add_argument("image",type=str,help="ERROR you need to add the image url", required=False)



class Test(Resource):
    def get(self):
        return jsonify({"message":"You are connected"})

''' Class for getting the list of characters using a for to call every character, retunring it as a json response '''
class Characters(Resource):
    def get(self):
        response= list(database.db.characters.find())
        characters=[]
        for character in response:
            del character['_id']
            characters.append(character)
        return jsonify({'results':characters})


''' Class for manipulating data from a single character '''
class Character(Resource):

    ''' Returns the information from a character using the variable 'id' from the list of characters '''
    def get(self,id):
        response = database.db.characters.find_one({'id':id})
        del response['_id']
        return jsonify(response)

    ''' The post method let us create a new character using a set of requirements to fill, in case of a duplicate of an id an error will be shown'''
    def post(self):
        args=post_characters_args.parse_args()
        self.abort_if_id_exist(args['id'])    
        #print(args)
        database.db.characters.insert_one({
            'id': args['id'],
            'name': args['name'],
            'gender': args['gender'],
            'image': args['image'],

           
        })
        return jsonify(args)
        

    ''' The put method let us modify the information from a character only when we refill every slot of information and in case of a non existing is, it will show us an error '''
    def put(self,id):
        args=post_characters_args.parse_args()
        self.abort_if_not_exist(id)
        database.db.characters.update_one(
            {'id':id},
            {'$set':{
                'id': args['id'],
                'name': args['name'],
                'gender': args['gender'],
                'image': args['image'],

            }}
        )
        return jsonify(args)

    ''' The patch method let us replace modify infromation from a character, and being able to only modify what we need without having to fill every infromation slot again '''
    def patch(self,id):
        character= self.abort_if_not_exist(id) #In case of a non exsiting id, it will show us an error
        args= patch_characters_args.parse_args()
        
        database.db.characters.update_one(
            {'id':id},
            {'$set':{
                'id': args['id'] or character['id'],
                'name': args['name'] or character['name'],
                'gender': args['gender'] or character['gender'],
                'image': args['image'] or character['image'],
      
            }}
        )
        character= self.abort_if_not_exist(id)
        del character['_id']
        return jsonify(character)
    
    ''' The delete method let us delete all the information in the database from an character using the variable "id" '''
    def delete(self,id):
        character=self.abort_if_not_exist(id) #In case of a non exsiting id, it will show us an error
        database.db.characters.delete_one({'id':id})
        del character['_id']
        return jsonify({'deleted':character})

    ''' Method to show an error, stopping the process, when we are trying to create a new character with an existing id '''
    def abort_if_id_exist(self,id):
        if database.db.characters.find_one({'id':id}):
            abort(jsonify({'error':{'406':f"The character with the id: {id} already exist"}}))

    ''' Method to show an error, stopping the process, when we are trying to modify information from a character with a non existing id '''
    def abort_if_not_exist(self,id):
        character=database.db.characters.find_one({'id':id})
        if not character: 
            abort(jsonify({'error':{'404':f"The character with the id: {id} not found"}}))
        else:
            return character


api.add_resource(Test,'/test/')
api.add_resource(Characters,'/characters/')
api.add_resource(Character,'/character/', '/character/<int:id>/')

if __name__=='__main__':
    app.run(load_dotenv=True, port=8080)