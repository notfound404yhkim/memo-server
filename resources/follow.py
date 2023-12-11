from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required #요청 받기
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
import pandas as pd


# 팔로워 팔로위 관련
class FollowResource(Resource):
    # 친구추가 
    @jwt_required()
    def post(self,followee_id):
        user_id = get_jwt_identity()
        print(followee_id)

        try:
            connection = get_connection()
            query = '''insert into follow
                        (followerId,followeeId)
                        values
                        (%s,%s);'''
            
            record = (user_id,followee_id)
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(Error)
            cursor.close()
            connection.close()
            return{"ERROR" : str(e)},500
        
        return{"Result " : "Success" },200
    
    @jwt_required()
    def delete(self,followee_id):
        user_id = get_jwt_identity()
        print(followee_id)

        try:
            connection = get_connection()
            query = '''delete from follow
                       where followerId =%s and followeeId =%s;'''
            
            record = (user_id,followee_id)
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            print(Error)
            cursor.close()
            connection.close()
            return{"ERROR" : str(e)},500
        
        return{"Result " : "Success" },200
    

class FollowMemoResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        offset = request.args.get('offset')
        limit = request.args.get('limit')
        try:
            connection = get_connection()
            query = '''select m.id as memoId, m.userId, m.title,
                        m.date as date , m.content, m.createdAt,m.updateAt,u.nickname
                        from follow f 
                        join memo m 
                        on f.followeeId = m.userId 
                        join user u
                        on m.userId = u.id
                        where f.followerId = %s and m.date > now()
                        order by m.date asc
                        limit '''+offset+''' , '''+limit+''' ;'''
            
            record = (user_id,)
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
            print(Error)
            cursor.close()
            connection.close()
            return{"ERROR" : str(e)},500 

        # 날짜 포맷 변경 
        i = 0
        for row in result_list:
            result_list[i]['date'] = row['date'].isoformat()
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updateAt'] = row['updateAt'].isoformat()
            i = i+1

        return {"result " : "success",
            "items" : result_list,
            "count " : len(result_list)},200