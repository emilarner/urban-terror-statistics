// con.js [server] [password] [command]
// prints response in stdout.

// dependency: quake3-rcon

// I have found no Python library that can do this, so I have to outsource this task to JavaScript. 
// It is very clear that I do not like JavaScript, but it is managable.
// A source of criticism: why do the arguments begin at index 2? 

var Q3RCon = require('quake3-rcon');

const server = process.argv[2]
const password = process.argv[3]  
const command = process.argv[4]

var rcon = new Q3RCon({
    address: server,
    port: 27960,
    password: password,
    debug: false
});

rcon.send(command, function(resp) {
    console.log(resp);
});
