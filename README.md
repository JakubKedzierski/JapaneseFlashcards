# JapaneseFlashcards
Japanese-English Flashcards - microservice project  
  
Run Kaffka in container and connect flashcards to it Tutorial:  
  
  
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
