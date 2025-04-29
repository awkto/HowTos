## Add GitLab user via CLI

Avoid using the web altogether when spinning up Gitlab environments repeatedly for labs and testing. Do this by creating an API token through the rails console, then using that API token to create an admin user.

<br>

<br>

### Create an API token via CLI (Optional)

If you want to automate this further, you can use the rails console to create the API token for the root user

1. SSH into Gitlab
2. Open rails console

```
gitlab-rails console
```
3. Enter commands to create token for root

```
user = User.find_by(username: 'root')
token = user.personal_access_tokens.create(
  name: 'API Token from Rails script',
  scopes: ['api'],
  expires_at: 1.year.from_now 
)
puts token.token 
```

<br>

<br>

### Add via Rest API

1. Log in to GitLab web as root and create a token
2. Create script **adduser.sh** :

```
TOKEN="glpat-ySSyyoPQ11brrr88iiEE"
EMAIL="guy@example.com"
USERNAME="guybrush"
PASSWORD='M0kiM0ki$1'
NAME="guybrush"
GITLAB_URL="https://gitlab.example.com"

curl --request POST "${GITLAB_URL}/api/v4/users" \
     --header "PRIVATE-TOKEN: $TOKEN" \
     --form "email=$EMAIL" \
     --form "username=$USERNAME" \
     --form "name=$NAME" \
     --form "password=$PASSWORD" \
     --form "skip_confirmation=true" \
     --form "admin=true"
```
3. Replace all the variables with your specific user details
4. Make script executable `chmod +x adduser.sh` 
5. Execute the script `./adduser.sh`



### Add license via Rest APi

1. Log in to GitLab web as root and create a token
2. Base64 encode the license

```
echo [LICENSE STRING] | base64
```
3. Create script **addlicense.sh** :

```
TOKEN="[ADD TOKEN HERE]
GITLAB_URL="https://gitlab.example.com"
LICENSE_B64=[ENCODED LICENSE HERE]

curl --request POST "${GITLAB_URL}/api/v4/licenses" \
--header "PRIVATE-TOKEN: $TOKEN" \
--form "license=$LICENSE_64"
```
4. Replace all the variables with your specific user details
5. Make script executable `chmod +x addlicense.sh` 
6. Execute the script `./addlicense.sh`
