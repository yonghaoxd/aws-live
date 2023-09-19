from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'student'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.tarc.edu.my')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    Stud_id = request.form['Stud_id']
    Stud_name = request.form['Stud_name']
    Stud_phoneNo = request.form['Stud_phoneNo']
    Stud_email = request.form['Stud_email']
    Stud_cgpa = request.form['Stud_cgpa']
    Stud_programme = request.form['Stud_programme']
    Stud_img = request.files['Stud_img']

    insert_sql = "INSERT INTO student VALUES (%s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if Stud_img.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (Stud_id, Stud_name, Stud_phoneNo, Stud_email, Stud_cgpa, Stud_programme))
        db_conn.commit()

        # Uplaod image file in S3 #
        Stud_img_name_in_s3 = "stud-id-" + str(Stud_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=Stud_img_name_in_s3, Body=Stud_img)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                Stud_img_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=Stud_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

