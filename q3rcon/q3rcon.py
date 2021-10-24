import os
import subprocess



def rcon_exec(server, password, command) -> str:
    args = "node {filename} {server} {password}".format(
        filename = os.path.dirname(os.path.realpath(__file__)) + "/" + "con.js",
        server = server,
        password = password
    )



    process = subprocess.Popen(args.split(" ") + [command], stdout = subprocess.PIPE)
    #                          ^^^ lazy way to avoid rewriting code

    return process.stdout.read().decode()