"""
This script allows you to perform an easy release
"""
import re
from os.path import dirname

from git import Repo, Tag


class VTag:
    """
    Holds the version information of a tag
    """

    def __init__(self):
        self.tag: Tag = None
        self.major = None
        self.minor = None
        self.bug = None

    @classmethod
    def from_tag(cls, tag: Tag):
        """
        Creates this VTag from a tag object
        """
        print(tag)
        tag_ = re.search(r".*(\d+\.\d+\.\d+).*", tag.name, re.IGNORECASE)
        if not tag_:
            RuntimeError(f"Couldn't parse the tag {tag.name}")
        vtag = cls()
        vtag.tag = tag
        major, minor, bug = tag_.group(1).split(".")
        vtag.major = int(major)
        vtag.minor = int(minor)
        vtag.bug = int(bug)
        return vtag

    # pylint: disable=redefined-outer-name
    def next_tag(self, update: int = 0):
        """
        Next tag. update specifies 0 for bug, 1 for minor, 2 for major
        """
        next_ = VTag()
        next_.major = self.major
        next_.minor = self.minor
        next_.bug = self.bug
        if update == 0:
            next_.bug += 1
        elif update == 1:
            next_.bug = 0
            next_.minor += 1
        elif update == 2:
            next_.bug = 0
            next_.minor = 0
            next_.major += 1
        return next_

    def get_path(self):
        """
        Returns the tag path or the vX.X.X style path from this tag
        """
        if self.tag is not None:
            return self.tag.path
        return f"v{self.major}.{self.minor}.{self.bug}"

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.bug}"

    def __eq__(self, other):
        return (self.major, self.minor, self.bug) == (
            other.major,
            other.minor,
            other.bug,
        )

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return (self.major, self.minor, self.bug) < (
            other.major,
            other.minor,
            other.bug,
        )


if __name__ == "__main__":
    repo = Repo(path=dirname(__file__))
    tags = [VTag.from_tag(tag) for tag in repo.tags]
    tags.sort()
    latest = tags[-1]
    print("The latest version is", latest)
    updates = {"0": "bug", "1": "minor", "2": "major"}
    update = input(
        "Please specify, what type of release this should be. [0] bug, 1 minor, 2 major\n"
    )
    if update == "":
        update = "0"
    assert update in "012", "Update type has to be 0, 1 or 2"
    print(f"I will perform a {updates[update]} update")
    next_ = latest.next_tag(update=int(update))
    print("Next version will be", next_.get_path())
    input("Please confirm with enter")
    next_.tag = repo.create_tag(path=next_.get_path())
    print("Now to publish your changes, please use the following command:")
    print("git push --tags")
