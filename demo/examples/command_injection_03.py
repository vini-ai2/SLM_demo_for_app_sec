# Command Injection evaluation case 3
subprocess.Popen("grep " + term + " data.txt", shell=True)

