## Docker without Sudo

How to enable running docker commands without sudo

<br>

1. Create group

```
sudo groupadd docker
```

<br>
2. Add user to group

```
sudo usermod -aG docker your_username
```

<br>
3. Refresh session (logout or use following command)

```
newgrp docker
```

<br>
4. Test running docker command

```
docker run hello-world
```

<br>
