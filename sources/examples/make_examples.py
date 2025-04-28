"""Generate all examples."""

import make_iso18004_examples
import make_eci_examples
import make_application_examples
import make_miscellaneous_examples


def main():
    make_iso18004_examples.main()
    make_eci_examples.main()
    make_application_examples.main()
    make_miscellaneous_examples.main()


if __name__ == "__main__":
    main()
