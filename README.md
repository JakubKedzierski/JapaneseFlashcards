# JapaneseFlashcards
Japanese-English Flashcards - microservice project  

## Info  
* Flashcards - `python ./app.py`, localhost:8000   
    * debug flashcard: `curl -X POST -H "Content-Type: application/json" http://localhost:8000/debug_endpoints/send_flashcard/{user_id}`, eg: 
      `curl -X POST -H "Content-Type: application/json" http://localhost:8000/debug_endpoints/send_flashcard/5`
* Notifications - `python ./app.py`, localhost:8001   
    * setup account on https://mailtrap.io/
    * copy credentials to app/serices/Notifications/.env from inboxes -> 'SMTP Settings' -> Show Credentials
    * setup account on https://www.twilio.com/docs/sms/api
    * copy credentials to app/serices/Notifications/.env from inboxes -> 'Account Info' -> Account SID / Auth Token
      
    * env file should look like that:  
      `
      MAIL_SERVER='sandbox.smtp.mailtrap.io'
      MAIL_PORT = 2525
      MAIL_USERNAME = 'user_name'
      MAIL_PASSWORD = 'user_password'
      MAIL_STARTTLS = True
      MAIL_SSL_TLS = False
      MAIL_FROM = 'flashcards@gmail.com'
      SMS_SID = 'sms_sid'
      SMS_AUTH_TOKEN = 'sms_auth_token'
      SMS_FROM = 'sms_from'
      SMS_TO = 'sms_to'
      `
    * if email limit exceeded create new account? and type in new credentials (getting error "Connection refused"), same for sms
  
  
* UserManager - `python ./app.py`, localhost:8002  
    * Test:  
        * save user - `curl -X POST -H "Content-Type: application/json" -d '{"user_email": "Kacper.Miowalski@example.com", "user_phone": "123456781", "token": "my-token", "level":"3"}' http://localhost:8002/user/add_user`  
        * get user - `curl localhost:8002/user/1`  
        * Info: data validation -> frontend
        * DB view: `qlite3 user_database.db` and then: `select * from user;`
   
* Quiz - `python ./app.py`, localhost:8003  
     * Test:
         * send quizes for all users - `curl -X POST -H "Content-Type: application/json" http://localhost:8003/debug_endpoints/send_quizes`  
         * send quizes for all users - `curl -X POST -H "Content-Type: application/json" http://localhost:8003/debug_endpoints/send_single_quiz/{user_id}`   
    

* Twilio: `curl -X POST "https://api.twilio.com/2010-04-01/Accounts/sid/Messages.json" ^`
  `--data-urlencode "Body=Hello from Twilio" ^`
  `--data-urlencode "From=phone" ^`
  `--data-urlencode "To=phone" ^`
  `-u "sid:auth_token"`
  
## Run Kaffka in container and connect flashcards to it Tutorial:  
   
  
here good tutorial: https://www.youtube.com/watch?v=jtBVppyfDbE&t=869s&ab_channel=ChristianLempa for some steps below  
  
Windows + VSCode + Dokcer:  
install WSL2 and ubuntu distro  
set default WSL distro to ubuntu  
install Docker Desktop  
install VSCode  
install DevContainers, RemoteExplorer, Docker, SQLite extension in vs code, reload  
connect remotly to VSCode via WSL:ubuntu (left down corner in vscode) and open proper workspace/folder (pull git repo), make sure you can access  
proper folders via WSL in vscode  
you can create named worskapce from git repository in vscode  
probably  you need to reinstall/reload some of extensions above being connected to WSL in vscode  
launch DockerDesktop app  
click docker-compose.yml and then right-click on docker-compose.yml in vscode and then Compose Up  

You should see this in terminal:  
⠿ Network japaneseflashcards_default  Created                                                          
⠿ Container zookeeper Started                                                                                                  
⠿ Container broker Started        
  
Check Docker extension (left panel in VS Code), you should see green arrow at top (japaneseflashcards containers)  
and running in background 2 containers  
You can check logs right clicking on container and then 'View Logs'  
  
In docker desktop you should see images: flashcards and 2 containers running in background (broker and zookeeper).  
If something is broken you can do 'Compose down' in vscode or kill containers in Docker app and then restart / try to fix something   
  
If you are sure everything works you can run flashcards app:  
go to app/servies/Flashcards and run e.g: pyton3 app.py   
You may need to install proper dependencies, some of them are included in requirements.txt  
  
Good app startup finishes with:  
'INFO:     Application startup complete.'  
