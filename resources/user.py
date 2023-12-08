
from email_validator import validate_email, EmailNotValidError
from flask import request
from flask_jwt_extended import create_access_token #요청 받기
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

from utils import check_password, hash_password


class UserRegisterResource(Resource):
    def post(self):
        #1. json을 가져옴
        data = request.get_json()

        #2. 이메일 체크
        try :
            validate_email(data['email'])  
        
        except EmailNotValidError as e:
            print (e)
            return {'error ' : str(e)},400
        
        #3. 비밀번호 체크
        if len(data['password']) < 4 or len(data['password']) > 14:
            return {"error" : '비밀번호 길이가 올바르지 않습니다.'},400

        #4. 비밀번호를 암호화 한다.
        password = hash_password(data['password'])
        print(password)
        
        #5. sql 연결 쿼리 전송
        try :
            # mysql 연결 
            connection = get_connection()

            query = '''insert into user
                    (email,password,nickname)
                    values
                    (%s,%s,%s);  '''
            
            record = (data['email'],password,data['nickname'])
            # 커서생성 
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()

            # 커서가 마지막 유저 아이디를 가지고있음
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return{"result" : "fail" , "Error " : print(e)},500
            
        #6. 정상 동작
        # 결과 와, 생성한 토큰을 클라이언트에게 리턴.
        access_token = create_access_token(user_id)

        return {"result" : "success" , "tokken" : access_token},200
    
class UserLoginResource(Resource):
    def post(self):
        
        data = request.get_json()

        try:
           connection = get_connection()

           query = '''select *
                    from user
                    where email = %s; 
                    '''
           record = (data['email'] , )  # 데이터가 하나 일때는 , 포함 

           cursor = connection.cursor(dictionary=True)
           cursor.execute(query,record)
           #가져온 data를 리스트 형태로 리턴
           result_list = cursor.fetchall() 

           cursor.close()
           connection.close()


        except Error as e:
            print(e)
            cursor.close()
            connection.close()
            return {"Error" : print(e)},500
        
        # 회원 가입 한 이메일인지 체크 
        if len(result_list) == 0 :
            return {"Error" : "회원 가입을 먼저 하십시오."}, 400

        # 유저가 입력한 PW, DB에 있는 PW 체크 
        check = check_password(data['password'],result_list[0]['password'])

        if check == False:
            return{"ERROR" : "비밀번호가 틀립니다"},400
        
        # 토큰 만들기
        access_token = create_access_token(result_list[0]['id'])

        return {"result" : "sucess",
                 "accessToken" : access_token},200