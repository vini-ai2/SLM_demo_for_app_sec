# Command Injection evaluation case 13
subprocess.Popen("grep " + term + " data.txt", shell=True)

