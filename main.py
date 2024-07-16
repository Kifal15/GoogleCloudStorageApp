from flask import Flask, request, redirect, url_for, session, jsonify
from google.cloud.sql.connector import Connector
from flask import render_template
import random
import string
from google.cloud.storage.blob import Blob
from google.cloud import storage  # Import the storage module
# Initialize Google Cloud Storage client
storage_client = storage.Client()
bucket_name = 'yourbucketname(just go and make a bucket in gcp)'  # Replace with your bucket name
bucket = storage_client.bucket(bucket_name)
app = Flask(__name__)

# Initialize Connector object
connector = Connector()

# Function to establish a connection to the database
def establish_connection():
    try:
        conn = connector.connect(
            "your-database-connection-string",  # Placeholder for the actual connection string
            "pymysql",
            user="your-username",              # Placeholder for the actual username
            password="your-password",          # Placeholder for the actual password
            db="your-database-name"            # Placeholder for the actual database name
        )
        return conn
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to create users table if it doesn't exist
def create_users_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255),
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                allocated_storage_mb INT DEFAULT 10,
                used_storage_mb INT DEFAULT 0
            )
        """)
        conn.commit()  # Commit the transaction
        cursor.close()  # Close cursor
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
# Function to generate a unique user ID
def generate_user_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Function to check if a connection can be made and create users table
def check_connection():
    conn = establish_connection()
    if conn:
        if create_users_table(conn):
            return conn
    return None

# Route for homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = check_connection()
        if conn:
            cursor = conn.cursor()
            user_id = generate_user_id()
            # Allocate 10MB of storage to the new user
            cursor.execute("INSERT INTO users (user_id, email, password, allocated_storage_mb) VALUES (%s, %s, %s, %s)", (user_id, email, password, 10))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('login'))
        else:
            return 'Failed to establish connection to Cloud SQL.'

    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sign Up</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    text-align: center;
                }
                form {
                    width: 300px;
                    margin: 0 auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.1);
                }
                input[type="text"],
                input[type="password"] {
                    width: calc(100% - 20px);
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                input[type="submit"] {
                    width: 100%;
                    padding: 10px;
                    margin-top: 10px;
                    background-color: #007bff;
                    color: #fff;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>Sign Up</h1>
            <form method="post">
                <input type="text" name="email" placeholder="Email">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Sign Up">
            </form>
        </body>
        </html>
    '''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = check_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                session['email'] = email
                return redirect(url_for('profile'))
            else:
                return 'Invalid email or password'
        else:
            return 'Failed to establish connection to Cloud SQL.'

    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                    text-align: center;
                }
                form {
                    width: 300px;
                    margin: 0 auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.1);
                }
                input[type="text"],
                input[type="password"] {
                    width: calc(100% - 20px);
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                input[type="submit"] {
                    width: 100%;
                    padding: 10px;
                    margin-top: 10px;
                    background-color: #007bff;
                    color: #fff;
                    border: none;
                    border-radius: 3px;
                    cursor: pointer;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>
            <h1>Login</h1>
            <form method="post">
                <input type="text" name="email" placeholder="Email">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Login">
            </form>
        </body>
        </html>
    '''

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'email' in session:
        email = session['email']
        conn = check_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, allocated_storage_mb, used_storage_mb FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data:
                user_id, allocated_storage_mb, used_storage_mb = user_data
                cursor.close()

                # Styles for file upload form and file list
                form_style = '''
                    <style>
                        form {
                            width: 300px;
                            margin: 20px auto;
                            background-color: #fff;
                            padding: 20px;
                            border-radius: 5px;
                            box-shadow: 0px 0px 10px 0px rgba(0,0,0,0.1);
                        }
                        input[type="file"] {
                            width: calc(100% - 20px);
                            padding: 10px;
                            margin: 10px 0;
                            border: 1px solid #ccc;
                            border-radius: 3px;
                        }
                        input[type="submit"] {
                            width: 100%;
                            padding: 10px;
                            margin-top: 10px;
                            background-color: #007bff;
                            color: #fff;
                            border: none;
                            border-radius: 3px;
                            cursor: pointer;
                        }
                        input[type="submit"]:hover {
                            background-color: #0056b3;
                        }
                        ul {
                            list-style-type: none;
                            padding: 0;
                            margin: 0;
                        }
                        li {
                            margin-bottom: 10px;
                        }
                        a {
                            color: #007bff;
                            text-decoration: none;
                        }
                        a:hover {
                            text-decoration: underline;
                        }
                    </style>
                '''

                if request.method == 'POST':
                    if 'file' not in request.files:
                        return jsonify({'error': 'No file part'}), 400

                    file = request.files['file']

                    if file.filename == '':
                        return jsonify({'error': 'No selected file'}), 400

                    # Calculate file size in MB
                    file_size_mb = file.content_length / (1024 * 1024)

                    # Check if user has enough storage space
                    if used_storage_mb + file_size_mb > allocated_storage_mb:
                        return jsonify({'error': 'Not enough storage space'}), 400

                    # Upload file to Google Cloud Storage
                    file_path = f"{user_id}/{file.filename}"
                    blob = bucket.blob(file_path)
                    blob.upload_from_file(file)

                    # Update used storage in database
                    used_storage_mb += file_size_mb
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET used_storage_mb = %s WHERE user_id = %s", (used_storage_mb, user_id))
                    conn.commit()
                    cursor.close()

                    return jsonify({'message': 'File uploaded successfully'}), 201

                # Display uploaded files and search functionality
                blobs = list(bucket.list_blobs(prefix=f"{user_id}/"))
                if blobs:
                    file_list = [blob.name.split("/")[-1] for blob in blobs]
                    search_query = request.args.get('search')
                    if search_query:
                        file_list = [file for file in file_list if search_query.lower() in file.lower()]
                    file_list_html = '<ul>'
                    for file_name in file_list:
                        file_path = f"{user_id}/{file_name}"
                        file_url = url_for('download_file', file_path=file_path)
                        delete_url = url_for('delete_file', file_path=file_path)
                        file_list_html += f'<li><a href="{file_url}">{file_name}</a> <a href="{delete_url}" style="color: red;">Delete</a></li>'
                    file_list_html += '</ul>'
                else:
                    file_list_html = 'No files uploaded yet.'

                conn.close()

                return f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>User Profile</title>
                    {form_style}
                </head>
                <body>
                    <h1>User Profile</h1>
                    <p>Email: {email}</p>
                    <p>User ID: {user_id}</p>
                    <h2>Upload File</h2>
                    <form action="/profile" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".txt,.pdf,.doc,.docx,.jpg,.jpeg,.png">
                        <button type="submit">Upload</button>
                    </form>
                    <h2>Uploaded Files</h2>
                    <form action="/profile" method="get">
                        <input type="text" name="search" placeholder="Search files">
                        <button type="submit">Search</button>
                    </form>
                    {file_list_html}
                </body>
                </html>
                '''
            else:
                cursor.close()
                conn.close()
                return 'User not found'
        else:
            return 'Failed to establish connection to Cloud SQL.'
    else:
        return redirect(url_for('login'))

# Route for deleting files from Google Cloud Storage
@app.route('/delete_file', methods=['POST', 'DELETE'])
def delete_file():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user_id = get_user_id_by_email(email)
    if not user_id:
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'POST':
        file_path = request.form.get('file_path')
    elif request.method == 'DELETE':
        file_path = request.args.get('file_path')
    else:
        return jsonify({'error': 'Method Not Allowed'}), 405

    if not file_path:
        return jsonify({'error': 'Missing file path'}), 400

    # Check if the file exists
    blob = bucket.blob(file_path)
    if not blob.exists():
        return jsonify({'error': 'File not found'}), 404

    # Delete the file from Google Cloud Storage
    blob.delete()

    # Update the used storage in the database
    conn = establish_connection()
    if not conn:
        return jsonify({'error': 'Failed to establish connection to Cloud SQL.'}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT used_storage_mb FROM users WHERE user_id = %s", (user_id,))
    used_storage_mb = cursor.fetchone()['used_storage_mb']
    blob_size_mb = blob.size / (1024 * 1024)
    used_storage_mb -= blob_size_mb
    cursor.execute("UPDATE users SET used_storage_mb = %s WHERE user_id = %s", (used_storage_mb, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'File deleted successfully'}), 200
# Route for downloading files
@app.route('/download/<path:file_path>')
def download_file(file_path):
    blob = bucket.blob(file_path)
    file_contents = blob.download_as_string()
    return file_contents, 200, {'Content-Disposition': f'attachment; filename="{file_path.split("/")[-1]}"'}
# Route for logging out
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Route for administrators to deactivate a user
@app.route('/deactivate/<int:user_id>', methods=['PUT'])
def deactivate_user(user_id):
    conn = check_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET active = FALSE WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            return jsonify({'message': 'User deactivated successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Failed to establish connection to database'}), 500

# Route for administrators to delete a user
@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = check_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            cursor.close()
            return jsonify({'message': 'User deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Failed to establish connection to database'}), 500

if __name__ == '__main__':
    app.run(debug=True)
