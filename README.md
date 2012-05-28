sprintly-to-github
==================

Python scripts for fetching data from sprintly and pushing it to github issue tracker. It will try to overwrite any existing issues but may not be able to if you didn't create them, I haven't tried this.

I've only tested it on one project which went OK: [csl-editor](https://github.com/citation-style-editor/csl-editor).

**Use at your own risk!**

## Instructions

1. Fetch data from sprint.ly to a local sprintlyData.json file:
-- python getSprintlyData.py username sprintlyAPIKey sprintlyProductId

(find your sprintlyAPIKey in your [Account Profile](https://sprint.ly/account/profile/))

2. Push data to Github:
-- python sendToGithub.py username password repositoryOwner repository
