# Command Injection evaluation case 10
subprocess.run(["sh", "-c", "echo " + message])

