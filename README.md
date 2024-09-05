## Development Tools ##

*Install via Admin*

# VS Code #

*System Installer* [https://code.visualstudio.com/docs/?dv=win64](https://code.visualstudio.com/docs/?dv=win64)

# Cursor IDE #

*Download and Install* [https://www.cursor.com/features](https://www.cursor.com/features)

# Git #

*Download* [https://git-scm.com/download/win](https://git-scm.com/download/win)




# GitHub Setup

1. Create a GitHub account:
   - Go to [GitHub](https://github.com) and sign up for a new account.
   - Follow the prompts to complete your profile.

2. Generate a new SSH key:
   - Open a terminal or command prompt.
   - Run the following command, replacing "your_email@example.com" with the email you used for GitHub:
     ```
     ssh-keygen -t ed25519 -C "your_email@example.com"
     ```
   - Press Enter to accept the default file location.
   - Enter a secure passphrase when prompted (optional but recommended).

3. Add the SSH key to your GitHub account:
   - Copy the contents of your public key file (usually `~/.ssh/id_ed25519.pub`).
   - Go to GitHub Settings > SSH and GPG keys > New SSH key.
   - Paste your key and give it a descriptive title.

# SSH Configuration #

Add the following to your SSH config file (usually located at `~/.ssh/config`):


        Host github.com
        IdentityFile ~/.ssh/id_ed25519
4. Clone the repository:
   - Open a terminal or command prompt.
   - Navigate to the directory where you want to clone the repository.
   - Run the following command:
     ```
     git clone git@github.com:chaelir/kids.git
     ```

5. Configure Git (if not done already):
   ```
   git config --global user.name "Your Name"
   git config --global user.email "your_email@example.com"
   ```

Now you're ready to start working with the repository!


