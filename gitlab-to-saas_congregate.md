# Congregate Instructions for Gitlab Migration

This is a start to end instruction set for using Congregate to migrate from a self hosted Gitlab instance to Gitlab.com SAAS version. Note you will likely need enterprise license on both ends.

[Official instructions here](https://gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate/-/blob/master/docs/using-congregate.md#quick-start)

## Container Setup
1. Set up a linux machine with Docker / podman installed (recommend Ubuntu)
2. Pull container image for [congregate](https://gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate)
```
docker pull \
registry.gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate:latest-debian
``` 
3. Create a shell script to _Start_ your congregate container instance

```
#!/bin/bash
docker run -p 8000:8000 -v /var/run/docker.sock:/var/run/docker.sock -v /etc/hosts:/etc/hosts \
--name congregate-bg -d -it 1545c8faa1ac  /bin/bash
```

4. Create another shell script to _Resume_ or log in to the congregate container

```
#!/bin/bash
docker exec -it congregate-bg /bin/bash
```

5. If you need to remove old exited containers run

```
docker ps -a
docker rm [image ID]
```

Or in a single line bulk delete
```
docker rm -v -f $(docker ps -qa)
```

## Token Creation and Obfuscate
1. Create a Group access token from your Gitlab.com namespace or subgroup
2. Create a Personal Access Token from an Admin user on Gitlab self hosted instance
3. On Congregate, exec into the container with ```docker exec -it congregate-bg /bin/bash```
4. Use **congregate obfuscate** command and hit enter
5. Copy and paste one of your admin/group tokens
6. The command will take your token as input, and output the obfuscated version, SAVE this
7. Repeat these steps 4,5,6 for your other token as well
8. Keep the obfuscated tokens and enter them below when configuring the congregate.conf file

## Config File Setup
1. Grab a congregate.conf template file [here](https://gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate/-/blob/master/congregate.conf.template)
2. Update the following fields in the conf file

**Destination section**
```
[DESTINATION]
### General configuration for GitLab server
dstn_hostname = https://gitlab.com
dstn_access_token = [obfuscated group access token from gitlab.com namespace]
import_user_id = [ID of a user that has access to the namespace]
dstn_parent_group_id = [ID of the group you're importing into, could be namespace or subgroup]
dstn_parent_group_path = mynamespace/mysubgroup
```

**Source section**
```
[SOURCE]
### General configuration for GitLab server
### This configuration is considered when the source is a GitLab server
src_type = GitLab
src_hostname = https://gitty.dnsif.ca
src_access_token = [obfuscated admin token from gitlab selfhosted instance]
```

**Export sectino should be left this way**
```
location = filesystem
filesystem_path = /opt/congregate/data/scratch
```

**App section should also be left this way**
```
[APP]
export_import_status_check_time = 10
export_import_timeout = 3600
```
3. Save the file locally on the linux machine running the congregate container
4. Use **docker cp** command to copy the file into the running congregate container with
```
docker cp congregate.conf congregate-bg:/opt/congregate/data/congregate.conf
```

## Congregate List to pull and stage projects
...

## Update waves csv file, use template [from here](https://gitlab.com/gitlab-org/professional-services-automation/tools/migration/congregate/-/blob/master/templates/stage-wave-template.csv)
...


### Stage Projects
### Stage Groups
### Stage Users
