Authors: 
  - Jack Fitzgerald 
  - Patrick Keleher


How to run the project:

  1.) Run the ss.py script on 1 or more computers by executing 'python ss.py [port]' 
  (NOTE: the port is optional, default is 8081)
  
  2.) Take note of the IP address and port that gets printed after running ss.py.
  
  3.) Construct a new chainlist file and add in the <SSaddr, SSport> pairs for each stepping stone.
  
  4.) Run the awget.py script by executing 'python awget.py <URL> [-c chainlist]' 
  (NOTE: specifying the chainlist file is optional, the default is chaingang.txt) 

  5.) If all goes well, the file that is returned should be stored in the same directory where the awget.py script was executed. 


Important things to note:

  - All sockets will timeout after 10 seconds if nothing is received.
