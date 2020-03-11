# Simple python rnd project manager: tas

Tas lets you easily create new projects from template, automatically install requirements, run env and commit (coming soon!) with one command.

### tas _does..._

* create projects from template
* download additional files to project if needed
* manage requirements and env
* run jupyter

### tas _does not but should..._
* interactive template creation
* git integration
* support windows
* support conda
* support zeppeline

----


## Installation osx/linux

1. **get python package**
```sh
$ pip install tas
```
2. **Add tas to your env variables**
    - **Zsh note**: Modify your `~/.zshrc` file instead of `~/.bash_profile`.
    - **Ubuntu and Fedora note**: Modify your `~/.bashrc` file instead of `~/.bash_profile`.
```sh
echo 'alias tas="python -m tas"' >> ~/.bash_profile
```
3. **Restart your shell so the path changes take effect.**
    ```sh
    $ exec "$SHELL"
    ```

## Key concepts of tas:
1. Namespace is a directory with projects (default one is ```~/Documents/tas_projects```)
2. Template is a number of steps to perform when starting new project (folders, env, requirements, submodules that used in your team)
3. path = PosixPath standard
4. Name - uninque (in one namespace) string 
## Usage:
0. Create `new` project
```sh
tas new mega_project
```
1. `run` existing project
```sh
tas run mage_project
```
2. `list` objects (`a`-all, `p`-projects, `n`-namespace, `t`-templates)
```sh
tas list a
```
3. `del` objects (`n`-namespace, `p`-projects)
```sh
tas del mega_project -t p
```
4.  `set` settings value (`-ns` namespace)
For now only for namespaces, lets change default path
```sh
tas set default /home/user/Documents/company_name
```
New namespace:
```sh
tas set company_name /home/user/Documents/company_name
```
5. Run project in not default ns:
```sh
tas run mega_project -ns company_name
```

## Default template:
here should be a motivation behind the default template

### Thanks
- pyenv creator for the idea of simplicity
    
### License

[The MIT License](LICENSE)
