# urban-terror-statistics
A flask application that serves statistics about an Urban Terror server. 

This is a simple flask application which takes in the output of a running Urban Terror server, and this program parses it in such a fashion as to provide meaningful statistics regarding the server. The data includes: players, their weapons, their gear, their kills/frags, etc; the name of the current map and its image; and server configurations and rules. Additionally, if provided with a correct RCON (remote console) password, administrative action may be taken on the server from this application, including that of kicking. 

The graphical interface to this program is quite poor, bearing a bad practicing of HTML and CSS, as well as the lack thereof JavaScript or any interactive features. Nonetheless, it provides an interface which is nonetheless useful, albeit not looking or feeling modern. An image detailing the graphical interface will be posted here; however, currently it will remain absent. Additionally, the images of the weapons were initially present, but they have since been lost--they were poor anyway. 

You may host this program on any port you choose, which then you would preferably proxy through something like NGINX. If you want to see more configuration options, please view and configure the *config.py* file which encompasses the various parameters that may be changed throughout this application. 

You will need (in order to run this application successfully):

 - Urban Terror
 - Python
 - NodeJS
	 - Note: it is essentially impossible to find a Quake 3 Arena--which Urban Terror is based off of--RCON library for Python that works, so taking the easy route: I used a NodeJS RCON library that works without any resistance, making it into a command-line application that *this* program interfaces with via subprocess; in other words, I am being extremely lazy. 
 - (optional) NGINX, for proxying efforts
 - For Python:
	 - pip (for flask)
	 - flask 
 - A UNIX-like environment



To quote the help menu--which can be issued by passing -h as a command-line parameter to the urt-stats.py file:

```
urt-stats - Generate a statistics page in real time for Urban Terror, with Python + Flask.

USAGE:
python urt-stats.py
Server logging information must be piped into stdin.
You may pipe the output of the dedicated server program to urt-stats.
Example:
./urt-ded-x86_64 | python urt-stats.py
You may also, albeit less efficiently, parse the games.log file by piping it into this program.
urt-stats will generate an HTML page containing the players and their characteristics, along with a moderation panel, accessible by the correct RCON password as specified in this program's config.
```

