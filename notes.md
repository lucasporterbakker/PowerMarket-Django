# Save the (disk) space !

Story to properly remove an **unwanted** file or folder (ie *big folder* or file with secrets inside...) from git repository **and** all git history.

1. After backuped the file or folder somewhere:

```bash
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch -r apps/solar/MLdata' \
--prune-empty --tag-name-filter cat -- --all

  Rewrite cf22e6b3f813063542a530ff885a228d61bf7163 (389/435) (35 seconds passed, remaining 4 predicted)    rm 'apps/solar/MLdata/basicapproach30khidden/checkpoint'
  rm 'apps/solar/MLdata/basicapproach30khidden/latestmodel_alt.data-00000-of-00001'
  rm 'apps/solar/MLdata/basicapproach30khidden/latestmodel_alt.index'
  rm 'apps/solar/MLdata/basicapproach30khidden/latestmodel_alt.meta'
  rm 'apps/solar/MLdata/safemodel2/checkpoint'
  rm 'apps/solar/MLdata/safemodel2/latestmodel_az.data-00000-of-00001'
  rm 'apps/solar/MLdata/safemodel2/latestmodel_az.index'
  rm 'apps/solar/MLdata/safemodel2/latestmodel_az.meta'
  [...]

echo "apps/solar/MLdata" >> .gitignore
git add .gitignore
git commit -m "Add apps/solar/MLdata to .gitignore"
git push origin --force --all
git push origin --force --tags
```

2. All collaborators have to [**rebase**](https://git-scm.com/book/en/Git-Branching-Rebasing), not merge, any branches they created off of your old (tainted) repository history. One merge commit could reintroduce some or all of the tainted history that you just went to the trouble of purging.

```bash
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now
```

[Original sources on Github](https://help.github.com/articles/removing-sensitive-data-from-a-repository/)
