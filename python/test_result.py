

# Containing whole result of prediction
class TestResultClass(object):
    # Class Name (ex: xxxx)
    name = None
    # Class Label  (ex: 4)
    label = None
    # Class Score
    score = 0
    # Class Box coodinate ([xmin, ymin, xmax, ymax])
    box = None


class TestResultImage(object):
    # Image name
    name = None
    # Classes in this image
    classes = None
    # Filepath (absolute path)
    filepath = None

    def sort_classes(self):
        if self.classes:
            self.classes.sort(key=lambda r: r.label)


class TestResultGroup(object):
    # Group Name (ex: Card)
    name = None
    # Required class labels (ex: 0, 3, 5)
    required_classes = None
    # Images in this group
    images = None


class TestResult(object):

    passed_count = 0
    tested_count = 0

    group = None

    def is_passed(self):
        return self.passed_count != 0 and (self.passed_count == self.tested_count)
