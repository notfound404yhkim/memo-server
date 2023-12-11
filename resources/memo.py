from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required #요청 받기
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
import pandas as pd

class MemoListResource(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        user_id = get_jwt_identity()
        
        try:
            connection = get_connection()
            query = ''' insert into memo
                        (userId,title,date,content)
                        values
                        (%s,%s,%s,%s);'''
            
            record = (user_id, data['title'],
                      data['date'],data['content'])
            
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return{"Error" : str(e)},500

        return{"Result" : "success"},200 
    @jwt_required()
    def get(self):
        
        user_id = get_jwt_identity()

        # 쿼리 스트링 가져오기 (쿼리 파라미터)
        # get에서는 쿼리 파라미터를 이용해 데이터를 가져옴
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        
        print(offset)
        print(limit)
      
        try:
            connection = get_connection()
            query = '''select id,title,date,content
                        from memo
                        where userId = %s
                        order by date
                        limit '''+ str(offset) +''', '''+ str(limit) +'''    ;'''
            
            record = (user_id ,)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
          
            result_list = cursor.fetchall()  

            print(result_list)

            # date time 은 파이썬에서 사용하는 데이터 타입이므로
            # JSON 형식이 아니다. 따라서,
            # JSOON은 문자열이나 숫자만 가능하므로
            # datetime을 문자열로 바꿔주어야 한다. 

            cursor.close()
            connection.close()


        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return{"Error" : str(e)},500
        
        i = 0
        for row in result_list:
            result_list[i]['date'] = row['date'].isoformat()
            # result_list[i]['createdAt'] = row['createdAt'].isoformat()
            # result_list[i]['updateAt'] = row['updateAt'].isoformat()
            i = i+1

        return {"result " : "success",
            "items" : result_list,
            "count " : len(result_list)},200
    
class MemoResource(Resource):
    @jwt_required()
    def delete(self,memo_id):
        user_id = get_jwt_identity()
        print(user_id)
        print(memo_id)
        
        try:
            connection = get_connection()
            query = ''' delete from memo
                        where id =%s and userId =%s;'''
            
            record = (memo_id, user_id)
            
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return{"Error" : str(e)},500

        return{"Result" : "success"},200 
    

    @jwt_required()
    def put(self,memo_id):
        data = request.get_json()
        user_id = get_jwt_identity()
        print(user_id)
        print(memo_id)
        
        try:
            connection = get_connection()
            query = ''' update memo
                        set title = %s,date = %s,content = %s
                        where id = %s and userId = %s;'''
            
            record = (data['title'], data['date'],
                      data['content'],memo_id,user_id)
            
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return{"Error" : str(e)},500

        return{"Result" : "success"},200 
    

    

    
    
    

      






