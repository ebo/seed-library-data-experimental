# seed-library-data-experimental
temporary repository used to experiment with structure and various ideas.  This is intended to be deleted after the structure solidifies, and we do not end up leaving a lot of flotsum and jetsom.

## Contributing

The koha-seed related repositories work on a [Forking
workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow)
methodology.  This works by first forking the repository, making your modifications, and then submitting a pull request.

One additional aim of the main repository is to have "No Junk In The
Trunk," and be able to compile/deploy directly from the main or master
branch.

### setting up your fork

In order to easily contribute to the koha-seed related projects, you
will first have to create a fork of the original repository, then link
the upstream remote:

  '''bash
  git clone git@github.com:$USER/seed-library-data-experimental.git
  cd seed-library-data-experimental

  git remote add upstream git@github.com:ebo/seed-library-data-experimental.git
  git remote -v
  '''

You should now see

  '''bash
  origin	https://github.com/<USER>/seed-library-data-experimental (fetch)
  origin	https://github.com/<USER>/seed-library-data-experimental (push)
  upstream	https://github.com/ebo/seed-library-data-experimental (fetch)
  upstream	https://github.com/ebo/seed-library-data-experimental (push)
  '''
  
### Creating branches

It is considered best practice to not make changes directly to the
main or master branch, but to create an isolated bug fix or feature
using a descriptive branch name:

  '''bash
  git checkout -b feature/your-feature-name
  '''

### Push Changes to Your Fork

Upload your newly created feature branch and commits back up to your
GitHub repository:

  '''bash
  git push origin feature/your-feature-name
  '''
  
### Merge your main or master branch with upstream

...

### Open a Pull Request (PR)

Visit your fork's landing page on the GitHub web interface.

Click the Compare & pull request button, which appears in a banner
automatically after a fresh push.

Set the base repository to the original main project and the head
repository to your fork's feature branch.

Submit a clear title along with a markdown description outlining what
your code alters or fixes.

