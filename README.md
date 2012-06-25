sprintly-to-github
==================

Python scripts for fetching data from sprintly and pushing it to github issue tracker. Best used on a github repo without any existing issues. If there are existing github issues it will try to overwrite them but will probably not be able to if you didn't create them, I haven't tested this.

I've only tested it on one project which went OK: [csl-editor](https://github.com/citation-style-editor/csl-editor).

**Use at your own risk!**

## Instructions

- Fetch data from sprint.ly to a local sprintlyData.json file:

```
python getSprintlyData.py username sprintlyAPIKey sprintlyProductId
```

(find your sprintlyAPIKey in your [Account Profile](https://sprint.ly/account/profile/))

- Push data to Github:

```
python sendToGithub.py username password repositoryOwner repository
```
