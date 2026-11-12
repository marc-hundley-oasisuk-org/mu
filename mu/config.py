import os
import sys
import platformdirs

# The default directory for application data (i.e., configuration).
DATA_DIR = platformdirs.user_data_dir(appname="mu", appauthor="python")

# The name of the default virtual environment used by Mu.
VENV_NAME = "mu_venv"

# The directory containing default virtual environment.
VENV_DIR = os.path.join(DATA_DIR, VENV_NAME)

# Maximum line length for using both in Check and Tidy
MAX_LINE_LENGTH = 88

# Build-time feature controls.
#
# Examination mode is deliberately the safe default.
#
# Packaged builds set sys._mu_build_profile through a PyInstaller runtime
# hook generated at build time. Source execution defaults to Exam.
#
# The student import policy is independent of these settings and remains
# mandatory in all supported builds.

import sys

BUILD_PROFILE = getattr(sys, "_mu_build_profile", "Exam")

if BUILD_PROFILE == "Teaching":
    ENABLE_CHECK = True
    ENABLE_TIDY = True
    ENABLE_CODE_ASSIST = True
else:
    BUILD_PROFILE = "Exam"
    ENABLE_CHECK = False
    ENABLE_TIDY = False
    ENABLE_CODE_ASSIST = False

# The user's home directory.
HOME_DIRECTORY = os.path.expanduser("~")

# Name of the directory within the home folder to use by default
WORKSPACE_NAME = "mu_code"
