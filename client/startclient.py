import subprocess

# Lista dei file da eseguire
scripts = ["sintetizza-elevenLabs.py", "poseDetection.py"]


for script in scripts:
    subprocess.Popen(["xterm", "-e", f"python3 {script}"])
subprocess.Popen(["xterm", "-e", f"node-red"])
