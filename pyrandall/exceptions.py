INVALID_VERSION_MSG = (
    "Unsupported schema version for pyrandall. " "Please choose from: {}"
)


class InvalidSchenarioVersion(Exception):
    def __init__(self, correct_versions):
        super(Exception, self).__init__(
            INVALID_VERSION_MSG.format(", ".join(correct_versions))
        )
