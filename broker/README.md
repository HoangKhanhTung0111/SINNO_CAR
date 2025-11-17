1: Open docker desktop
2: Open terminal and run "docker pull emqx/emqx:latest"
3: Run "docker run -d --name emqx -p 1883:1883 -p 8083:8083 -p 18083:18083 emqx/emqx:latest"