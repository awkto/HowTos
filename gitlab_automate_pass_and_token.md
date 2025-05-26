This guide outlines the steps to reset a user's password and create a personal access token in GitLab using the Rails console. This is particularly useful for automating post-deployment configurations in lab environments.

## How to Reset a User Password and Create an API Token in GitLab via Rails Console

These instructions assume you have SSH access to your GitLab server.

### 1. SSH into the GitLab Server

Open your terminal and connect to your GitLab instance via SSH. Replace `gitlab.example.com` with your GitLab server's hostname or IP address.

```bash
ssh git@gitlab.example.com
```

### 2. Start the Rails Console

Once connected via SSH, navigate to the GitLab home directory (if you're not already there) and start the Rails console.

```bash
sudo gitlab-rails console
```

You should see output indicating the console is loading, eventually presenting a `irb(main):001:0>` prompt.

### 3. Reset User Password (e.g., for 'root')

To reset a user's password, you first need to find the user object and then update their password. In this example, we'll reset the `root` user's password.

```ruby
user = User.find_by_username('root') # Find the user by their username
new_password = 'your_new_secure_password' # Define the new password
user.password = new_password
user.password_confirmation = new_password
user.password_automatically_set = false # Important: Prevents GitLab from forcing a password reset on next login
user.save! # Save the changes
```

Replace `'your_new_secure_password'` with a strong, secure password of your choice. You will receive output confirming the user object was saved.

**Alternative ways to select a user:**

You can also find a user by their email address:

```ruby
user = User.find_by(email: 'user@example.com')
```

Or by their ID:

```ruby
user = User.find(1) # Replace 1 with the user's actual ID
```

### 4. Create an API Access Token (for the user, e.g., 'root')

To create a personal access token, you'll use the user object you just retrieved or find it again.

```ruby
user = User.find_by_username('root') # Ensure you have the user object
token = user.personal_access_tokens.create(scopes: [:api, :read_user, :read_repository, :write_repository], name: 'Automated Deployment Token', expires_at: 365.days.from_now)
token.set_token # Generate the token string
token.save!

puts token.token # Display the generated token
```

**Explanation of the token creation parameters:**

* `scopes`: Defines the permissions the token will have. Common scopes include:
    * `:api`: Full read/write access to the API.
    * `:read_user`: Read user profile data.
    * `:read_repository`: Read repository data.
    * `:write_repository`: Write to repository data.
    * Consult the GitLab API documentation for a full list of scopes.
* `name`: A descriptive name for your token.
* `expires_at`: (Optional) Sets an expiration date for the token. In this example, it's set to expire one year from now. You can adjust this as needed (e.g., `nil` for no expiration, or a specific date like `Date.today + 30.days`).

**Important:** The `puts token.token` command will display the generated token string. **Copy this token immediately** as it will not be displayed again once you exit the Rails console. Treat this token like a password, as it grants access to your GitLab instance.

### 5. Exit the Rails Console

Once you have completed your tasks, exit the Rails console:

```ruby
exit
```

### Optional: Automating GitLab License Key or Activation

For completely automated deployments of GitLab Enterprise Edition (EE), you might also consider automating the addition of a license key. While this isn't directly done via the Rails console for a simple "add license file" operation, you can leverage the GitLab API to upload a license file.

First, you would need the API token generated above. Then, you could use a `curl` command or a script in your automation pipeline to upload the license.

Here's a conceptual example using `curl` (replace placeholders with your actual data):

```bash
curl --request POST --header "Private-Token: <your_gitlab_api_token>" \
     --form "license=<@path/to/your/gitlab_license.gitlab-license>" \
     "https://gitlab.example.com/api/v4/license"
```

* Replace `<your_gitlab_api_token>` with the token you generated.
* Replace `<@path/to/your/gitlab_license.gitlab-license>` with the actual path to your GitLab license file.
* Replace `https://gitlab.example.com` with your GitLab instance URL.

This method allows for a more comprehensive automation of your GitLab lab instance deployments.
