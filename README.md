# It's a simple session based authentication built using fastAPI in python

- Clone the repository and run the following the command to fire the server. 
    `uvicorn main:app --reload `

- There are 5 routes
  -  `/api/signup` -  Allows a user to sign up using email and password and stores the same in a mongoDB cluster.
  -  `/api/login`  -  Allows a user to login using the same email id and password
  -  `/api/logout` -  Allows the user to logout from the current session
  -  `/api/upload-picture` -  Allows the user the upload the local path of a picture stored in the picture folder . The user needs to be logged in to use this functionality. Uses sessions to keep track of current user
  -  `/api/view-picture` /- Any user can see all the upload pictures with or without authentication.

 
